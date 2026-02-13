from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import requests
from bs4 import BeautifulSoup

DEFAULT_IGNORE_SELECTORS = [
    ".timestamp",
    ".date",
    "time",
    "script",
    "style",
    ".ad",
    "[data-analytics]",
]


def load_html(source: str) -> Tuple[str, str]:
    candidate = Path(source)
    if candidate.exists():
        return candidate.read_text(encoding="utf-8"), str(candidate.resolve())
    response = requests.get(source, timeout=15)
    response.raise_for_status()
    return response.text, source


def normalize_html(html: str, ignore_selectors: Iterable[str]) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")
    for selector in ignore_selectors:
        for node in soup.select(selector):
            node.decompose()
    return soup
