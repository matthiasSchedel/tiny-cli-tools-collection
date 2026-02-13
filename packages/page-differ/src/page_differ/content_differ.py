from __future__ import annotations

import difflib
from typing import Dict, List

from bs4 import BeautifulSoup


def _paragraphs(soup: BeautifulSoup) -> List[str]:
    text = soup.get_text("\n", strip=True)
    parts = [line.strip() for line in text.splitlines() if line.strip()]
    return parts


def diff_content(before: BeautifulSoup, after: BeautifulSoup) -> Dict[str, object]:
    left = _paragraphs(before)
    right = _paragraphs(after)
    similarity = difflib.SequenceMatcher(a="\n".join(left), b="\n".join(right)).ratio()
    return {
        "added_paragraphs": [p for p in right if p not in left],
        "removed_paragraphs": [p for p in left if p not in right],
        "text_similarity": round(similarity, 4),
    }
