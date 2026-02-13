from text_chunker.chunker import chunk_text


def test_chunk_text_basic() -> None:
    payload = chunk_text("Hello world. This is a test.", max_tokens=4, strategy="sentence")
    assert payload["metadata"]["total_chunks"] >= 1
    assert payload["chunks"][0]["tokens"] > 0


def test_empty_input() -> None:
    payload = chunk_text("", max_tokens=100)
    assert payload["chunks"] == []
    assert payload["metadata"]["total_chunks"] == 0
