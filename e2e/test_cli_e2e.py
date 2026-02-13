from __future__ import annotations

import json
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Iterable

import pytest
import requests


def _run(
    args: Iterable[str], *, timeout: int = 60, input_text: str | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        input=input_text,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _assert_ok(proc: subprocess.CompletedProcess[str], context: str) -> None:
    assert proc.returncode == 0, f"{context}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def _wait_for_http(url: str, timeout: float = 10.0) -> None:
    end = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < end:
        try:
            response = requests.get(url, timeout=1)
            if response.status_code < 500:
                return
        except Exception as exc:  # pragma: no cover - networking race
            last_error = exc
        time.sleep(0.2)
    raise RuntimeError(f"Service did not become ready: {url} ({last_error})")


def test_text_chunker_e2e(tmp_path: Path) -> None:
    source = tmp_path / "doc.txt"
    source.write_text("Paragraph one.\n\nParagraph two with more text.", encoding="utf-8")
    proc = _run(["text-chunker", "--strategy", "paragraph", str(source)])
    _assert_ok(proc, "text-chunker failed")
    payload = json.loads(proc.stdout)
    assert payload["metadata"]["total_chunks"] >= 1


def test_schema_guesser_e2e(tmp_path: Path) -> None:
    sample = tmp_path / "sample.jsonl"
    sample.write_text(
        '{"email":"a@example.com","age":20}\n{"email":"b@example.com","age":30}\n', encoding="utf-8"
    )
    proc = _run(["schema-guesser", str(sample)])
    _assert_ok(proc, "schema-guesser failed")
    payload = json.loads(proc.stdout)
    assert payload["type"] == "object"
    assert payload["properties"]["email"]["format"] == "email"


def test_json_patcher_e2e(tmp_path: Path) -> None:
    doc = tmp_path / "data.json"
    patch = tmp_path / "ops.json"
    doc.write_text('{"count":1}', encoding="utf-8")
    patch.write_text('[{"op":"replace","path":"/count","value":2}]', encoding="utf-8")
    proc = _run(["json-patcher", "patch", str(doc), "--patch", str(patch)])
    _assert_ok(proc, "json-patcher patch failed")
    payload = json.loads(proc.stdout)
    assert payload["success"] is True
    assert payload["result"]["count"] == 2


def test_rate_limiter_e2e() -> None:
    proc = _run(["rate-limiter", "--rps", "100", "echo", "hello"])
    _assert_ok(proc, "rate-limiter failed")
    assert "hello" in proc.stdout


def test_page_differ_e2e(tmp_path: Path) -> None:
    before = tmp_path / "before.html"
    after = tmp_path / "after.html"
    before.write_text("<html><body><h1>Old</h1><p>One</p></body></html>", encoding="utf-8")
    after.write_text("<html><body><h1>New</h1><p>One</p><p>Two</p></body></html>", encoding="utf-8")
    proc = _run(["page-differ", "--mode", "content", str(before), str(after)])
    _assert_ok(proc, "page-differ failed")
    payload = json.loads(proc.stdout)
    assert payload["changes"]["content"]["text_similarity"] < 1


def test_api_mocker_e2e(tmp_path: Path) -> None:
    spec = tmp_path / "openapi.yaml"
    spec.write_text(
        """
openapi: 3.0.0
info:
  title: Example
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
""".strip(),
        encoding="utf-8",
    )
    port = _free_port()
    proc = subprocess.Popen(
        ["api-mocker", "--host", "127.0.0.1", "--port", str(port), str(spec)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_for_http(f"http://127.0.0.1:{port}/users")
        response = requests.get(f"http://127.0.0.1:{port}/users", timeout=3)
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_webhook_relay_e2e() -> None:
    port = _free_port()
    proc = subprocess.Popen(
        ["webhook-relay", "--port", str(port), "--capacity", "10"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_for_http(f"http://127.0.0.1:{port}/")
        post = requests.post(f"http://127.0.0.1:{port}/hook", json={"ok": True}, timeout=3)
        assert post.status_code == 200
        listed = requests.get(f"http://127.0.0.1:{port}/_relay/requests", timeout=3)
        assert listed.status_code == 200
        items = listed.json()
        assert len(items) >= 1
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_doc_renderer_e2e(tmp_path: Path) -> None:
    if shutil.which("pandoc") is None:
        pytest.skip("pandoc not installed")
    source = tmp_path / "doc.md"
    output = tmp_path / "doc.html"
    source.write_text("# Title\n\nHello world", encoding="utf-8")
    proc = _run(["doc-renderer", "--to", "html", str(source), str(output)])
    _assert_ok(proc, "doc-renderer failed")
    assert output.exists()
    assert "<h1" in output.read_text(encoding="utf-8").lower()


def test_form_filler_e2e(tmp_path: Path) -> None:
    html = tmp_path / "form.html"
    html.write_text(
        """
<!doctype html>
<html><body>
  <form>
    <input id="name" type="text" />
    <input id="email" type="email" />
    <button type="submit">Submit</button>
  </form>
</body></html>
""".strip(),
        encoding="utf-8",
    )
    config = tmp_path / "data.yaml"
    config.write_text(
        """
fields:
  - selector: "#name"
    value: "Test User"
  - selector: "#email"
    value: "test@example.com"
""".strip(),
        encoding="utf-8",
    )
    proc = _run(
        [
            "form-filler",
            "--no-submit",
            "--browser",
            "chromium",
            html.resolve().as_uri(),
            str(config),
        ],
        timeout=90,
    )
    if proc.returncode != 0 and (
        "Executable doesn't exist" in proc.stderr
        or "Please run the following command to download new browsers" in proc.stderr
    ):
        pytest.skip("Playwright browser binaries are not installed in this environment")
    _assert_ok(proc, "form-filler failed")
    payload = json.loads(proc.stdout)
    assert payload["filled_fields"] == 2
    assert payload["status"] in {"success", "partial"}
