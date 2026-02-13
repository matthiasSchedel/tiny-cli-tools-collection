from __future__ import annotations

from pathlib import Path

from ..utils import convert_with_pandoc


def convert_docx(input_path: Path, output_path: Path, **kwargs) -> None:
    convert_with_pandoc(input_path, output_path, from_format="docx", **kwargs)
