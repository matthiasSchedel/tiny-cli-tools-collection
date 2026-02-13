from pathlib import Path

from doc_renderer.utils import detect_format


def test_detect_format_md(tmp_path: Path) -> None:
    path = tmp_path / "doc.md"
    path.write_text("# x", encoding="utf-8")
    assert detect_format(path) == "md"
