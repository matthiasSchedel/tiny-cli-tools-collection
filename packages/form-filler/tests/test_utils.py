import json
from pathlib import Path

from form_filler.utils import load_data_file, resolve_config_urls, resolve_input_url


def test_load_json_data_file(tmp_path: Path) -> None:
    path = tmp_path / "data.json"
    path.write_text(json.dumps({"fields": []}), encoding="utf-8")
    data = load_data_file(path)
    assert data["fields"] == []


def test_resolve_input_url_relative_file(tmp_path: Path) -> None:
    target = tmp_path / "page.html"
    target.write_text("<html></html>", encoding="utf-8")
    resolved = resolve_input_url("./page.html", base_dir=tmp_path)
    assert resolved == target.as_uri()


def test_resolve_config_urls_for_main_and_step(tmp_path: Path) -> None:
    form_path = tmp_path / "form.html"
    step_path = tmp_path / "step.html"
    form_path.write_text("<html></html>", encoding="utf-8")
    step_path.write_text("<html></html>", encoding="utf-8")
    config = {
        "url": "./form.html",
        "steps": [{"url": "./step.html", "fields": []}],
        "fields": [],
    }
    resolved = resolve_config_urls(config, base_dir=tmp_path)
    assert resolved["url"] == form_path.as_uri()
    assert resolved["steps"][0]["url"] == step_path.as_uri()
