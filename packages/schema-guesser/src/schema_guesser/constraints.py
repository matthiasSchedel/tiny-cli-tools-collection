from __future__ import annotations

from typing import Any, Dict, List


def infer_numeric_constraints(values: List[Any]) -> Dict[str, Any]:
    numeric = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
    if not numeric:
        return {}
    return {"minimum": min(numeric), "maximum": max(numeric)}


def infer_string_constraints(values: List[Any]) -> Dict[str, Any]:
    strings = [v for v in values if isinstance(v, str)]
    if not strings:
        return {}
    lengths = [len(v) for v in strings]
    return {"minLength": min(lengths), "maxLength": max(lengths)}
