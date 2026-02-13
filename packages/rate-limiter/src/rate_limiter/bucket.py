from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass
class BucketState:
    tokens: float
    last_refill: float
    capacity: int
    refill_rate: float


class TokenBucket:
    def __init__(self, state: BucketState) -> None:
        self.state = state

    def refill(self, now: float | None = None) -> None:
        now = now if now is not None else time()
        elapsed = max(0.0, now - self.state.last_refill)
        self.state.tokens = min(
            self.state.capacity, self.state.tokens + elapsed * self.state.refill_rate
        )
        self.state.last_refill = now

    def try_consume(self, amount: float = 1.0, now: float | None = None) -> bool:
        self.refill(now=now)
        if self.state.tokens >= amount:
            self.state.tokens -= amount
            return True
        return False

    def wait_time(self, amount: float = 1.0) -> float:
        if self.state.tokens >= amount:
            return 0.0
        needed = amount - self.state.tokens
        return needed / self.state.refill_rate if self.state.refill_rate > 0 else float("inf")
