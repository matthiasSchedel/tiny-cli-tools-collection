from bs4 import BeautifulSoup
from page_differ.content_differ import diff_content


def test_content_diff() -> None:
    left = BeautifulSoup("<p>Hello</p>", "html.parser")
    right = BeautifulSoup("<p>Hello world</p>", "html.parser")
    result = diff_content(left, right)
    assert result["text_similarity"] < 1
