from __future__ import annotations

from typing import List

from .utils import Segment, split_markdown_sections, split_paragraphs, split_sentences


def by_character(text: str, max_chars: int, overlap: int) -> List[Segment]:
    from .utils import split_fixed_width

    return list(split_fixed_width(text, width=max_chars, overlap=overlap))


def by_token(text: str) -> List[Segment]:
    # Token chunking is assembled in chunker.py where token budget is known.
    return [Segment(text=text, start=0, end=len(text), boundary_type="token")]


def by_sentence(text: str) -> List[Segment]:
    return split_sentences(text)


def by_paragraph(text: str) -> List[Segment]:
    return split_paragraphs(text)


def by_semantic(text: str) -> List[Segment]:
    # Semantic mode preserves markdown headings and then paragraph boundaries.
    sections = split_markdown_sections(text)
    if not sections:
        return []
    if all(s.boundary_type == "paragraph" for s in sections):
        return sections
    semantic_segments: List[Segment] = []
    for section in sections:
        sub = split_paragraphs(section.text)
        if not sub:
            semantic_segments.append(section)
            continue
        for item in sub:
            semantic_segments.append(
                Segment(
                    text=item.text,
                    start=section.start + item.start,
                    end=section.start + item.end,
                    boundary_type="semantic",
                )
            )
    return semantic_segments
