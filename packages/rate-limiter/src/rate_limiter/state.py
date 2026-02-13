from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator

from .bucket import BucketState

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


@contextmanager
def locked_state_file(path: Path) -> Iterator[tuple[object, Dict[str, dict]]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as f:
        if fcntl:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        f.seek(0)
        raw = f.read().strip()
        data: Dict[str, dict] = json.loads(raw) if raw else {}
        try:
            yield f, data
        finally:
            f.seek(0)
            f.truncate()
            f.write(json.dumps(data))
            f.flush()
            if fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def default_state(capacity: int, refill_rate: float) -> BucketState:
    import time

    return BucketState(
        tokens=float(capacity), last_refill=time.time(), capacity=capacity, refill_rate=refill_rate
    )


def from_payload(payload: dict, capacity: int, refill_rate: float) -> BucketState:
    return BucketState(
        tokens=float(payload.get("tokens", capacity)),
        last_refill=float(payload.get("last_refill", 0.0)),
        capacity=int(payload.get("capacity", capacity)),
        refill_rate=float(payload.get("refill_rate", refill_rate)),
    )


def to_payload(state: BucketState) -> dict:
    return {
        "tokens": state.tokens,
        "last_refill": state.last_refill,
        "capacity": state.capacity,
        "refill_rate": state.refill_rate,
    }
