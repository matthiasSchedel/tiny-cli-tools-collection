from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

import tiktoken


@dataclass(frozen=True)
class Segment:
    text: str
    start: int
    end: int
    boundary_type: str
    complete: bool = True


def get_encoding(name: str):
    try:
        return tiktoken.get_encoding(name)
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported encoding: {name}") from exc


def count_tokens(text: str, encoding_name: str) -> int:
    if not text:
        return 0
    encoding = get_encoding(encoding_name)
    return len(encoding.encode(text))


def tail_tokens(text: str, token_count: int, encoding_name: str) -> str:
    if token_count <= 0 or not text:
        return ""
    encoding = get_encoding(encoding_name)
    encoded = encoding.encode(text)
    if len(encoded) <= token_count:
        return text
    return encoding.decode(encoded[-token_count:])


def split_paragraphs(text: str) -> List[Segment]:
    if not text:
        return []
    segments: List[Segment] = []
    start = 0
    for match in re.finditer(r"\n\s*\n", text):
        end = match.start()
        if end > start:
            segments.append(
                Segment(text=text[start:end], start=start, end=end, boundary_type="paragraph")
            )
        start = match.end()
    if start < len(text):
        segments.append(
            Segment(text=text[start:], start=start, end=len(text), boundary_type="paragraph")
        )
    return [s for s in segments if s.text.strip()]


def split_sentences(text: str) -> List[Segment]:
    if not text:
        return []
    pattern = re.compile(r"[^.!?\n]+(?:[.!?]+|$)", re.M)
    segments: List[Segment] = []
    for match in pattern.finditer(text):
        content = match.group(0)
        if content.strip():
            segments.append(
                Segment(
                    text=content,
                    start=match.start(),
                    end=match.end(),
                    boundary_type="sentence",
                )
            )
    return segments


def split_markdown_sections(text: str) -> List[Segment]:
    if not text:
        return []
    heading_pattern = re.compile(r"(?m)^#{1,6}\s+.*$")
    matches = list(heading_pattern.finditer(text))
    if not matches:
        return split_paragraphs(text)
    segments: List[Segment] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        section = text[start:end]
        if section.strip():
            segments.append(
                Segment(text=section, start=start, end=end, boundary_type="markdown_section")
            )
    return segments


def split_fixed_width(text: str, width: int, overlap: int = 0) -> Iterable[Segment]:
    if width <= 0:
        raise ValueError("width must be > 0")
    step = max(1, width - max(0, overlap))
    for start in range(0, len(text), step):
        end = min(len(text), start + width)
        if start >= end:
            continue
        yield Segment(text=text[start:end], start=start, end=end, boundary_type="character")
        if end == len(text):
            break
