from __future__ import annotations

from pathlib import Path

from ..utils import convert_with_pandoc


def convert_to_pdf(input_path: Path, output_path: Path, *, from_format: str, **kwargs) -> None:
    convert_with_pandoc(input_path, output_path, from_format=from_format, to_format="pdf", **kwargs)
