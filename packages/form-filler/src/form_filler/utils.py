from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

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


def resolve_input_url(url: str, base_dir: Path) -> str:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https", "file", "about", "data"}:
        return url
    local_path = Path(url).expanduser()
    if not local_path.is_absolute():
        local_path = (base_dir / local_path).resolve()
    return local_path.as_uri()


def resolve_config_urls(data: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
    resolved = dict(data)
    raw_url = resolved.get("url")
    if isinstance(raw_url, str):
        resolved["url"] = resolve_input_url(raw_url, base_dir=base_dir)

    raw_steps = resolved.get("steps")
    if isinstance(raw_steps, list):
        steps = []
        for step in raw_steps:
            if not isinstance(step, dict):
                steps.append(step)
                continue
            step_copy = dict(step)
            step_url = step_copy.get("url")
            if isinstance(step_url, str):
                step_copy["url"] = resolve_input_url(step_url, base_dir=base_dir)
            steps.append(step_copy)
        resolved["steps"] = steps
    return resolved
