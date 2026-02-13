from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import yaml


def load_data_file(path: Path, explicit_format: str | None = None) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    fmt = explicit_format or ("yaml" if path.suffix.lower() in {".yaml", ".yml"} else "json")
    if fmt == "yaml":
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("Data file root must be an object.")
    return data
