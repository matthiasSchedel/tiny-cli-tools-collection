from bs4 import BeautifulSoup
from page_differ.dom_differ import diff_dom


def test_dom_diff_added_node() -> None:
    before = BeautifulSoup("<div><p>A</p></div>", "html.parser")
    after = BeautifulSoup("<div><p>A</p><span>B</span></div>", "html.parser")
    result = diff_dom(before, after)
    assert len(result["added"]) >= 1
