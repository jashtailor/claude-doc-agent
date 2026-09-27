import agent


def test_mock_answers_field_question(capsys):
    agent.run_mock("What is the amount due on the Harborview invoice?")
    out = capsys.readouterr().out
    assert "invoice_10432.txt" in out
    assert "$12,340.00" in out


def test_mock_answers_general_question(capsys):
    agent.run_mock("What does the loading dock safety memo say?")
    out = capsys.readouterr().out
    assert "memo_safety_protocol.txt" in out


def test_mock_handles_no_match(capsys):
    agent.run_mock("Tell me about the moon colony teleportation sasquatch")
    out = capsys.readouterr().out
    assert "couldn't find" in out.lower()


def test_detect_field_finds_known_phrase():
    assert agent._detect_field("What is the due date on this invoice?") == "due date"


def test_detect_field_returns_none_for_open_question():
    assert agent._detect_field("Summarize the vendor review memo") is None
