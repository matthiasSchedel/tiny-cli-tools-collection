from __future__ import annotations

from typing import Any, Dict, List, Tuple

import jsonpatch
from jsonschema import ValidationError, validate


def apply_patch(
    document: Any, operations: List[Dict[str, Any]], schema: Dict[str, Any] | None = None
) -> Tuple[Any, Dict[str, Any]]:
    patch = jsonpatch.JsonPatch(operations)
    result = patch.apply(document, in_place=False)
    validation = {"valid": True, "errors": []}
    if schema is not None:
        try:
            validate(instance=result, schema=schema)
        except ValidationError as exc:
            validation = {"valid": False, "errors": [exc.message]}
    return result, validation
