from __future__ import annotations

import glob
import shutil
import subprocess
from pathlib import Path
from typing import Iterable, List

FORMAT_MAP = {
    "md": "markdown",
    "html": "html",
    "rst": "rst",
    "docx": "docx",
    "odt": "odt",
    "pdf": "pdf",
}


def detect_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "markdown":
        suffix = "md"
    if suffix not in FORMAT_MAP:
        raise ValueError(f"Unsupported input format for {path}")
    return suffix


def ensure_pandoc() -> None:
    if shutil.which("pandoc") is None:
        raise RuntimeError("Pandoc is required but not installed or not in PATH.")


def convert_with_pandoc(
    input_path: Path,
    output_path: Path,
    *,
    from_format: str,
    to_format: str,
    toc: bool,
    template: Path | None,
    css: Path | None,
    metadata: Path | None,
) -> None:
    ensure_pandoc()
    command: List[str] = [
        "pandoc",
        str(input_path),
        "--from",
        FORMAT_MAP[from_format],
        "--to",
        FORMAT_MAP[to_format],
        "--output",
        str(output_path),
    ]
    if toc:
        command.append("--toc")
    if template:
        command += ["--template", str(template)]
    if css and to_format in {"html", "pdf"}:
        command += ["--css", str(css)]
    if metadata:
        command += ["--metadata-file", str(metadata)]
    subprocess.run(command, check=True)


def expand_batch(pattern: str) -> Iterable[Path]:
    return [Path(p) for p in glob.glob(pattern)]
