from fastapi.testclient import TestClient
from webhook_relay.server import create_app


def test_capabilities_reports_websocket_disabled() -> None:
    app = create_app(
        forward_url=None,
        storage_path=None,
        signature_provider=None,
        secret=None,
        capacity=1000,
        websocket_enabled=False,
    )
    client = TestClient(app)
    response = client.get("/_relay/capabilities")
    assert response.status_code == 200
    assert response.json() == {"websocket": False}


def test_catch_all_stores_request() -> None:
    app = create_app(
        forward_url=None,
        storage_path=None,
        signature_provider=None,
        secret=None,
        capacity=1000,
        websocket_enabled=False,
    )
    client = TestClient(app)
    post_response = client.post("/webhook", json={"ok": True})
    assert post_response.status_code == 200

    list_response = client.get("/_relay/requests")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
