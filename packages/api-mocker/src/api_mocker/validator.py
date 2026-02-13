from __future__ import annotations

from typing import Any, Dict, List

from jsonschema import ValidationError, validate


def validate_body(schema: Dict[str, Any], payload: Any) -> List[str]:
    try:
        validate(instance=payload, schema=schema)
        return []
    except ValidationError as exc:
        return [exc.message]
