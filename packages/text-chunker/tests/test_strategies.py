from text_chunker.strategies import by_paragraph, by_sentence


def test_sentence_strategy() -> None:
    segments = by_sentence("A. B. C.")
    assert len(segments) == 3


def test_paragraph_strategy() -> None:
    segments = by_paragraph("Para1\n\nPara2")
    assert len(segments) == 2
