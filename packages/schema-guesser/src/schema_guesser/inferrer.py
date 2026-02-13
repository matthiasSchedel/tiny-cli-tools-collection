from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .constraints import infer_numeric_constraints, infer_string_constraints
from .patterns import detect_string_format


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _infer_node(values: List[Any], confidence: float, strict: bool) -> Dict[str, Any]:
    non_null = [v for v in values if v is not None]
    if not non_null:
        return {"type": "null", "x-confidence": 1.0}

    type_counts = Counter(_json_type(v) for v in non_null)
    total = len(non_null)
    dominant_type, dominant_count = type_counts.most_common(1)[0]
    dominant_conf = dominant_count / total

    if len(type_counts) > 1 and strict and dominant_conf < confidence:
        raise ValueError(f"Ambiguous type inference: {dict(type_counts)}")

    if dominant_type == "object":
        key_values: Dict[str, List[Any]] = defaultdict(list)
        present_counts: Counter[str] = Counter()
        for obj in (v for v in non_null if isinstance(v, dict)):
            for key in obj.keys():
                present_counts[key] += 1
            for key, value in obj.items():
                key_values[key].append(value)
        properties = {}
        required = []
        for key, vals in key_values.items():
            field_conf = present_counts[key] / total
            child = _infer_node(vals, confidence=confidence, strict=strict)
            child["x-confidence"] = round(field_conf, 3)
            properties[key] = child
            if field_conf >= confidence:
                required.append(key)
        node: Dict[str, Any] = {
            "type": "object",
            "properties": properties,
            "required": sorted(required),
            "x-confidence": round(dominant_conf, 3),
        }
        return node

    if dominant_type == "array":
        items = []
        for arr in (v for v in non_null if isinstance(v, list)):
            items.extend(arr)
        item_schema = _infer_node(items or [None], confidence=confidence, strict=strict)
        return {
            "type": "array",
            "items": item_schema,
            "x-confidence": round(dominant_conf, 3),
        }

    if dominant_type == "string":
        strings = [v for v in non_null if isinstance(v, str)]
        format_counts = Counter(f for f in (detect_string_format(v) for v in strings) if f)
        node = {"type": "string", "x-confidence": round(dominant_conf, 3)}
        if format_counts:
            format_name, format_hits = format_counts.most_common(1)[0]
            if format_hits / len(strings) >= confidence:
                node["format"] = format_name
        node.update(infer_string_constraints(strings))
        return node

    if dominant_type in {"integer", "number"}:
        node = {"type": dominant_type, "x-confidence": round(dominant_conf, 3)}
        node.update(infer_numeric_constraints(non_null))
        return node

    if len(type_counts) > 1 and not strict:
        return {
            "anyOf": [{"type": t} for t, _ in type_counts.items()],
            "x-confidence": round(dominant_conf, 3),
        }
    return {"type": dominant_type, "x-confidence": round(dominant_conf, 3)}


def infer_schema(
    samples: Iterable[Any],
    *,
    confidence: float = 0.8,
    strict: bool = False,
    title: str | None = None,
    description: str | None = None,
) -> Dict[str, Any]:
    rows = list(samples)
    root = _infer_node(rows, confidence=confidence, strict=strict)
    schema: Dict[str, Any] = {"$schema": "http://json-schema.org/draft-07/schema#"}
    if title:
        schema["title"] = title
    if description:
        schema["description"] = description
    schema.update(root)
    schema["x-metadata"] = {
        "samples_analyzed": len(rows),
        "inference_date": datetime.now(timezone.utc).isoformat(),
    }
    return schema
