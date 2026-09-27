"""The two tools the agent can call: search_docs and extract_field.

Kept separate from agent.py so both the real Claude loop and the mock
loop call the exact same code, and so tests can exercise the tools
without touching the API or the conversation loop at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "for", "of", "on", "in",
    "to", "and", "or", "what", "which", "who", "does", "do", "did", "how",
    "much", "many", "with", "this", "that", "it", "as", "by", "at", "from",
    "has", "have", "had", "our", "we", "you", "i",
}

_WORD_RE = re.compile(r"[a-zA-Z0-9$%.]+")
_FIELD_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z /]*?):\s*(.+)$")


@dataclass
class SearchHit:
    document: str
    score: int
    snippet: str

    def to_dict(self) -> dict:
        return {"document": self.document, "score": self.score, "snippet": self.snippet}


def _tokenize(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text) if len(w) > 2]


def _keywords(query: str) -> list[str]:
    tokens = _tokenize(query)
    keywords = [t for t in tokens if t not in _STOPWORDS]
    return keywords or tokens


def _snippet_for(content: str, keywords: list[str], width: int = 140) -> str:
    lower = content.lower()
    best_pos = -1
    for kw in keywords:
        pos = lower.find(kw)
        if pos != -1 and (best_pos == -1 or pos < best_pos):
            best_pos = pos
    if best_pos == -1:
        best_pos = 0
    start = max(0, best_pos - width // 2)
    end = min(len(content), best_pos + width // 2)
    snippet = content[start:end].strip().replace("\n", " ")
    snippet = re.sub(r"\s+", " ", snippet)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""
    return f"{prefix}{snippet}{suffix}"


def list_documents() -> list[str]:
    return sorted(p.name for p in DOCS_DIR.glob("*.txt"))


def search_docs(query: str, max_results: int = 3) -> list[dict]:
    """Keyword search across every document in documents/.

    Scores each document by how many times the query's keywords appear
    in it (case-insensitive) and returns the top matches with a short
    snippet of surrounding context, so the model can decide which
    document to dig into with extract_field.
    """
    keywords = _keywords(query)
    hits: list[SearchHit] = []
    for path in sorted(DOCS_DIR.glob("*.txt")):
        content = path.read_text()
        lower = content.lower()
        score = sum(lower.count(kw) for kw in keywords)
        if score > 0:
            hits.append(SearchHit(path.name, score, _snippet_for(content, keywords)))
    hits.sort(key=lambda h: h.score, reverse=True)
    return [h.to_dict() for h in hits[:max_results]]


def _resolve_document(document: str) -> Path | None:
    candidates = list_documents()
    if document in candidates:
        return DOCS_DIR / document
    stem = document.lower().replace(".txt", "")
    for name in candidates:
        if name.lower().replace(".txt", "") == stem:
            return DOCS_DIR / name
    for name in candidates:
        if stem in name.lower():
            return DOCS_DIR / name
    return None


def _parse_fields(content: str) -> dict:
    fields = {}
    for line in content.splitlines():
        if not line.strip():
            break
        match = _FIELD_LINE_RE.match(line)
        if match:
            fields[match.group(1).strip()] = match.group(2).strip()
    return fields


def _normalize(label: str) -> set[str]:
    return set(_tokenize(label))


def extract_field(document: str, field: str) -> dict:
    """Pulls a named field's value out of one document's header.

    Every document starts with a block of `Key: Value` lines (Amount
    Due, Due Date, Party A, and so on). This does fuzzy matching on the
    field name so "amount" finds "Amount Due" and "who is the vendor"
    finds "Vendor", rather than requiring an exact label.
    """
    path = _resolve_document(document)
    if path is None:
        return {"error": f"No document matching '{document}'. Known documents: {list_documents()}"}

    fields = _parse_fields(path.read_text())
    target_tokens = _normalize(field)

    best_key, best_overlap = None, 0
    for key in fields:
        key_tokens = _normalize(key)
        overlap = len(target_tokens & key_tokens)
        if overlap == 0:
            for t in target_tokens:
                if any(t in kt or kt in t for kt in key_tokens):
                    overlap = 1
                    break
        if overlap > best_overlap:
            best_key, best_overlap = key, overlap

    if best_key is None:
        return {
            "error": f"No field matching '{field}' in {path.name}.",
            "available_fields": list(fields.keys()),
        }
    return {"document": path.name, "field": best_key, "value": fields[best_key]}
