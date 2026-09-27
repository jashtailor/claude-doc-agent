import doc_tools


def test_search_docs_finds_relevant_invoice():
    hits = doc_tools.search_docs("Harborview amount due")
    documents = [h["document"] for h in hits]
    assert "invoice_10432.txt" in documents


def test_search_docs_ranks_by_relevance():
    hits = doc_tools.search_docs("forklift loading dock safety")
    assert hits
    assert hits[0]["document"] == "memo_safety_protocol.txt"


def test_search_docs_no_match_returns_empty():
    assert doc_tools.search_docs("xenon quantum toaster") == []


def test_extract_field_exact_document_name():
    result = doc_tools.extract_field("invoice_10432.txt", "amount due")
    assert result["value"] == "$12,340.00"
    assert result["field"] == "Amount Due"


def test_extract_field_fuzzy_field_name():
    result = doc_tools.extract_field("invoice_10432.txt", "payment")
    assert result["field"] == "Payment Terms"
    assert result["value"] == "Net 30"


def test_extract_field_document_name_without_extension():
    result = doc_tools.extract_field("invoice_10432", "due date")
    assert result["value"] == "2024-07-12"


def test_extract_field_unknown_document():
    result = doc_tools.extract_field("not_a_real_document", "amount due")
    assert "error" in result


def test_extract_field_unknown_field():
    result = doc_tools.extract_field("invoice_10432.txt", "shoe size")
    assert "error" in result
    assert "available_fields" in result
