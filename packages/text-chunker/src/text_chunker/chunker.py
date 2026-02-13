from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from . import strategies
from .utils import Segment, count_tokens, split_sentences, tail_tokens


@dataclass
class Chunk:
    index: int
    text: str
    tokens: int
    characters: int
    start_offset: int
    end_offset: int
    boundaries: Dict[str, object]


def _split_long_segment(segment: Segment, max_tokens: int, encoding: str) -> List[Segment]:
    parts = split_sentences(segment.text)
    if len(parts) <= 1:
        from .utils import split_fixed_width

        return [
            Segment(
                text=s.text,
                start=segment.start + s.start,
                end=segment.start + s.end,
                boundary_type="split",
                complete=False,
            )
            for s in split_fixed_width(
                segment.text, width=max(1, min(2000, len(segment.text) // 2 or 1))
            )
        ]
    split_parts: List[Segment] = []
    for p in parts:
        split_parts.append(
            Segment(
                text=p.text,
                start=segment.start + p.start,
                end=segment.start + p.end,
                boundary_type="split_sentence",
                complete=count_tokens(p.text, encoding) <= max_tokens,
            )
        )
    return split_parts


def _choose_segments(text: str, strategy: str, max_chars: int, overlap: int) -> List[Segment]:
    if strategy == "character":
        return strategies.by_character(text, max_chars=max_chars, overlap=overlap)
    if strategy == "token":
        return strategies.by_token(text)
    if strategy == "paragraph":
        return strategies.by_paragraph(text)
    if strategy == "semantic":
        return strategies.by_semantic(text)
    return strategies.by_sentence(text)


def chunk_text(
    text: str,
    *,
    max_tokens: int = 1000,
    max_chars: Optional[int] = None,
    overlap: int = 0,
    strategy: str = "sentence",
    encoding: str = "cl100k_base",
    include_metadata: bool = True,
) -> Dict[str, object]:
    if not text:
        metadata = {
            "total_chunks": 0,
            "total_tokens": 0,
            "total_characters": 0,
            "strategy": strategy,
            "max_tokens": max_tokens,
            "overlap": overlap,
            "encoding": encoding,
        }
        return {"chunks": [], "metadata": metadata if include_metadata else {}}

    token_budget = max_tokens if max_tokens > 0 else 1000
    char_budget = max_chars if max_chars and max_chars > 0 else None
    segments = _choose_segments(text, strategy, max_chars=max_chars or 1000, overlap=overlap)

    if strategy == "token":
        # Build pseudo-segments from word+whitespace spans so spacing is preserved.
        import re

        words = list(re.finditer(r"\S+\s*", text))
        segments = []
        for word in words:
            start = word.start()
            end = word.end()
            segments.append(
                Segment(text=text[start:end], start=start, end=end, boundary_type="token")
            )

    chunks: List[Chunk] = []
    current: List[Segment] = []
    queue = deque(segments)
    while queue:
        seg = queue.popleft()
        seg_tokens = count_tokens(seg.text, encoding)
        if seg_tokens > token_budget and strategy != "character":
            split = _split_long_segment(seg, token_budget, encoding)
            if len(split) == 1 and split[0].text == seg.text:
                from .utils import split_fixed_width

                split = [
                    Segment(
                        text=s.text,
                        start=seg.start + s.start,
                        end=seg.start + s.end,
                        boundary_type="split",
                        complete=False,
                    )
                    for s in split_fixed_width(seg.text, width=max(1, len(seg.text) // 2))
                ]
            queue.extendleft(reversed(split))
            continue

        candidate = current + [seg]
        candidate_text = "".join(item.text for item in candidate)
        candidate_tokens = count_tokens(candidate_text, encoding)
        candidate_chars = len(candidate_text)
        exceeds = candidate_tokens > token_budget or (
            char_budget is not None and candidate_chars > char_budget
        )
        if exceeds and current:
            chunk_text_value = "".join(item.text for item in current)
            first = current[0]
            last = current[-1]
            chunks.append(
                Chunk(
                    index=len(chunks),
                    text=chunk_text_value,
                    tokens=count_tokens(chunk_text_value, encoding),
                    characters=len(chunk_text_value),
                    start_offset=first.start,
                    end_offset=last.end,
                    boundaries={
                        "type": first.boundary_type,
                        "complete": all(s.complete for s in current),
                    },
                )
            )
            current = [seg]
        else:
            current = candidate

    if current:
        chunk_text_value = "".join(item.text for item in current)
        first = current[0]
        last = current[-1]
        chunks.append(
            Chunk(
                index=len(chunks),
                text=chunk_text_value,
                tokens=count_tokens(chunk_text_value, encoding),
                characters=len(chunk_text_value),
                start_offset=first.start,
                end_offset=last.end,
                boundaries={
                    "type": first.boundary_type,
                    "complete": all(s.complete for s in current),
                },
            )
        )

    if overlap > 0 and len(chunks) > 1:
        for idx in range(1, len(chunks)):
            prefix = tail_tokens(chunks[idx - 1].text, overlap, encoding)
            if prefix:
                chunks[idx].text = prefix + chunks[idx].text
                chunks[idx].tokens = count_tokens(chunks[idx].text, encoding)
                chunks[idx].characters = len(chunks[idx].text)
                chunks[idx].boundaries["complete"] = False

    total_tokens = sum(c.tokens for c in chunks)
    total_chars = sum(c.characters for c in chunks)
    metadata = {
        "total_chunks": len(chunks),
        "total_tokens": total_tokens,
        "total_characters": total_chars,
        "strategy": strategy,
        "max_tokens": token_budget,
        "overlap": overlap,
        "encoding": encoding,
    }
    payload = {"chunks": [asdict(c) for c in chunks]}
    if include_metadata:
        payload["metadata"] = metadata
    return payload
