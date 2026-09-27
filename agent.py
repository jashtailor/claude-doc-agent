#!/usr/bin/env python3
"""A small CLI agent that answers questions about a folder of documents.

Usage:
    python agent.py "What is the amount due on invoice INV-10432?"
    python agent.py --mock "Who are the parties in CTR-2031?"
    python agent.py                      # interactive mode, real API
    python agent.py --mock               # interactive mode, no API key needed

With ANTHROPIC_API_KEY set, this calls the real Claude API and streams the
answer token by token. Without a key, pass --mock to run a small rule-based
stand-in for the model so the whole demo works offline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

import doc_tools

MODEL = "claude-sonnet-5"
MAX_TURNS = 8

SYSTEM_PROMPT = """You are a document assistant for a small back office. You \
answer questions about the contracts, invoices, and internal memos in the \
company's document folder.

You have two tools:
- search_docs: keyword search across every document. Use this first to find \
which document(s) are relevant to the question.
- extract_field: pulls one named field (like "Amount Due", "Due Date", \
"Vendor", "Party A") out of a specific document's header. Use this once you \
know which document you need and which field you need from it.

Always ground your answer in what the tools return. Cite the document \
filename in your answer. If the tools don't turn up an answer, say so \
plainly instead of guessing."""

TOOLS = [
    {
        "name": "search_docs",
        "description": (
            "Keyword search across all documents in the folder. Returns the "
            "top matching documents with a relevance score and a text "
            "snippet. Use this to figure out which document(s) are relevant "
            "before asking for specific fields."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keywords to search for, e.g. 'invoice amount due Harborview'.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "extract_field",
        "description": (
            "Extracts one named field's value from a specific document's "
            "header block (e.g. 'Amount Due', 'Due Date', 'Vendor', "
            "'Party A', 'Effective Date'). Field name matching is fuzzy, so "
            "close wording is fine."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "document": {
                    "type": "string",
                    "description": "Document filename (or a distinctive part of it), as returned by search_docs.",
                },
                "field": {
                    "type": "string",
                    "description": "The field to extract, e.g. 'amount due' or 'effective date'.",
                },
            },
            "required": ["document", "field"],
        },
    },
]


def call_tool(name: str, tool_input: dict) -> dict | list:
    if name == "search_docs":
        return doc_tools.search_docs(**tool_input)
    if name == "extract_field":
        return doc_tools.extract_field(**tool_input)
    return {"error": f"Unknown tool: {name}"}


# --------------------------------------------------------------------------
# Real Claude loop
# --------------------------------------------------------------------------

def run_real(question: str) -> None:
    import anthropic

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": question}]

    for _ in range(MAX_TURNS):
        printed_any = False
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                printed_any = True
            final = stream.get_final_message()

        if printed_any:
            print()

        messages.append({"role": "assistant", "content": final.content})

        if final.stop_reason != "tool_use":
            return

        tool_results = []
        for block in final.content:
            if block.type == "tool_use":
                args = ", ".join(f"{k}={v!r}" for k, v in block.input.items())
                print(f"[tool call: {block.name}({args})]")
                result = call_tool(block.name, block.input)
                print(f"[tool result: {json.dumps(result)}]")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )
        messages.append({"role": "user", "content": tool_results})

    print(f"[stopped after {MAX_TURNS} turns without a final answer]", file=sys.stderr)


# --------------------------------------------------------------------------
# Mock loop (no API key, no network, fully deterministic)
# --------------------------------------------------------------------------

FIELD_PHRASES = [
    "amount due", "total contract value", "total", "amount",
    "due date", "issue date", "effective date", "date",
    "payment terms", "governing law", "term", "status",
    "invoice number", "document id", "memo id",
    "party a", "party b", "bill to", "vendor", "from", "to", "subject",
]

_FIELD_PHRASE_PATTERNS = [
    (phrase, re.compile(r"\b" + re.escape(phrase) + r"\b")) for phrase in FIELD_PHRASES
]


_VALUE_TRIGGERS = [
    "what is", "what's", "whats", "who is", "who are",
    "how much", "when is", "when was", "what was",
]


def _detect_field(question: str) -> str | None:
    """Only treat this as a "look up one field" question if it's phrased
    like one. Otherwise a broad question like "summarize the vendor memo"
    would trip on the word "vendor" and wrongly narrow to a single field."""
    lowered = question.lower()
    if not any(trigger in lowered for trigger in _VALUE_TRIGGERS):
        return None
    for phrase, pattern in _FIELD_PHRASE_PATTERNS:
        if pattern.search(lowered):
            return phrase
    return None


def _stream_out(text: str) -> None:
    words = text.split(" ")
    for i, word in enumerate(words):
        print(word, end=" " if i < len(words) - 1 else "", flush=True)
    print()


def run_mock(question: str) -> None:
    """A deterministic stand-in for the model: no LLM, just the same tools
    driven by a couple of simple rules. Good enough to demo the agent loop
    and to keep tests offline, not a substitute for the real thing."""
    hits = doc_tools.search_docs(question)

    if not hits:
        _stream_out("I couldn't find anything in the documents about that.")
        return

    top_document = hits[0]["document"]
    field = _detect_field(question)

    if field:
        result = doc_tools.extract_field(top_document, field)
        if "candidates" in result:
            _stream_out(
                f"'{field}' matches more than one field on {top_document}: "
                f"{', '.join(result['candidates'])}."
            )
        elif "error" in result:
            _stream_out(
                f"I found {top_document} as the closest match, but couldn't "
                f"pull a '{field}' field from it. It has: "
                f"{', '.join(result.get('available_fields', []))}."
            )
        else:
            _stream_out(
                f"According to {result['document']}, {result['field']} is "
                f"{result['value']}."
            )
        return

    lines = [f"Here's what I found across the documents:"]
    for hit in hits:
        lines.append(f"- {hit['document']}: {hit['snippet']}")
    _stream_out(" ".join(lines))


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def answer(question: str, mock: bool) -> None:
    if mock:
        run_mock(question)
    else:
        run_real(question)


def repl(mock: bool) -> None:
    mode = "mock" if mock else "live"
    print(f"Document agent ({mode} mode). Ask a question, or type 'quit'.")
    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        answer(question, mock)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("question", nargs="?", help="Question to ask. Omit for interactive mode.")
    parser.add_argument("--mock", action="store_true", help="Run without the Anthropic API.")
    args = parser.parse_args()

    if not args.mock and not os.environ.get("ANTHROPIC_API_KEY"):
        print("No ANTHROPIC_API_KEY set. Pass --mock to run offline, or set the key.", file=sys.stderr)
        sys.exit(1)

    if args.question:
        answer(args.question, args.mock)
    else:
        repl(args.mock)


if __name__ == "__main__":
    main()
