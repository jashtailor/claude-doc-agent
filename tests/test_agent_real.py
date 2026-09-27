import json
from types import SimpleNamespace
from unittest.mock import patch

import agent


class FakeStream:
    """Stands in for the `with client.messages.stream(...) as stream:` context
    manager, exposing just the two attributes run_real touches."""

    def __init__(self, text, final_message):
        self._text = text
        self._final_message = final_message

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False

    @property
    def text_stream(self):
        return iter([self._text] if self._text else [])

    def get_final_message(self):
        return self._final_message


def _tool_use_message(tool_name, tool_input, tool_id="toolu_1"):
    block = SimpleNamespace(type="tool_use", name=tool_name, input=tool_input, id=tool_id)
    return SimpleNamespace(content=[block], stop_reason="tool_use")


def _text_message(text):
    block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[block], stop_reason="end_turn")


def test_run_real_round_trips_tool_result_as_json(capsys):
    tool_input = {"document": "invoice_10432.txt", "field": "amount due"}
    turns = [
        FakeStream("Let me check.", _tool_use_message("extract_field", tool_input)),
        FakeStream("The amount due is $12,340.00.", _text_message("The amount due is $12,340.00.")),
    ]
    stream_calls = []

    class FakeMessages:
        def stream(self, **kwargs):
            # Snapshot messages now: agent.py mutates the same list object
            # after this call returns, so a bare reference would later
            # reflect turns that haven't happened yet.
            stream_calls.append({**kwargs, "messages": list(kwargs["messages"])})
            return turns[len(stream_calls) - 1]

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.messages = FakeMessages()

    with patch("anthropic.Anthropic", FakeClient):
        agent.run_real("What is the amount due on invoice INV-10432?")

    out = capsys.readouterr().out
    assert "[tool call: extract_field(document='invoice_10432.txt', field='amount due')]" in out

    expected_result = agent.doc_tools.extract_field(**tool_input)
    assert f"[tool result: {json.dumps(expected_result)}]" in out

    # The second turn must receive the tool result back as JSON (a dict),
    # not a Python repr string, so the model can parse it.
    second_turn_messages = stream_calls[1]["messages"]
    tool_result_block = second_turn_messages[-1]["content"][0]
    assert tool_result_block["tool_use_id"] == "toolu_1"
    assert tool_result_block["content"] == json.dumps(expected_result)
    assert json.loads(tool_result_block["content"]) == expected_result


def test_run_real_stops_after_max_turns(capsys):
    keep_calling_tool = _tool_use_message("search_docs", {"query": "anything"})

    class FakeMessages:
        def stream(self, **kwargs):
            return FakeStream("", keep_calling_tool)

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.messages = FakeMessages()

    with patch("anthropic.Anthropic", FakeClient):
        agent.run_real("Will this ever stop?")

    err = capsys.readouterr().err
    assert f"stopped after {agent.MAX_TURNS} turns" in err
