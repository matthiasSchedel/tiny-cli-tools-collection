import json
from pathlib import Path

from form_filler.utils import load_data_file


def test_load_json_data_file(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"fields": []}), encoding="utf-8")
    data = load_data_file(path)
    assert data["fields"] == []
