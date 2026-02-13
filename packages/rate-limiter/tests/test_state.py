import json
from pathlib import Path

from rate_limiter.state import locked_state_file


def test_locked_state_file(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    with locked_state_file(state_file) as (_, payload):
        payload["demo"] = {"tokens": 1}
    raw = json.loads(state_file.read_text())
    assert raw["demo"]["tokens"] == 1
