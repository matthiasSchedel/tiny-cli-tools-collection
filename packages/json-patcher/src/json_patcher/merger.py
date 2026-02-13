from __future__ import annotations

from copy import deepcopy
from typing import Any


def _merge_arrays(left: list, right: list, strategy: str) -> list:
    if strategy == "replace":
        return deepcopy(right)
    if strategy == "unique":
        out = deepcopy(left)
        for item in right:
            if item not in out:
                out.append(item)
        return out
    return deepcopy(left) + deepcopy(right)


def merge_documents(left: Any, right: Any, strategy: str, array_strategy: str) -> Any:
    if strategy == "replace":
        return deepcopy(right)

    if isinstance(left, dict) and isinstance(right, dict):
        merged = deepcopy(left)
        for key, value in right.items():
            if key not in merged:
                merged[key] = deepcopy(value)
            else:
                if strategy in {"merge", "smart"}:
                    merged[key] = merge_documents(merged[key], value, strategy, array_strategy)
                else:
                    merged[key] = deepcopy(value)
        return merged

    if isinstance(left, list) and isinstance(right, list):
        if strategy in {"append", "smart"}:
            return _merge_arrays(left, right, array_strategy if strategy == "smart" else "concat")
        return deepcopy(right)

    return deepcopy(right)
