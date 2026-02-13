from __future__ import annotations

from typing import Any, Dict, List


def validate_config(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if "fields" not in data and "steps" not in data:
        errors.append("Config must include either 'fields' or 'steps'.")
    if "fields" in data and not isinstance(data["fields"], list):
        errors.append("'fields' must be a list.")
    if "steps" in data and not isinstance(data["steps"], list):
        errors.append("'steps' must be a list.")
    return errors
