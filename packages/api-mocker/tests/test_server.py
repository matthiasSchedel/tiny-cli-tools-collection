from api_mocker.server import create_app
from fastapi.testclient import TestClient


def test_server_route_from_spec() -> None:
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
    }
    client = TestClient(create_app(spec))
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_root_route_available_when_spec_has_no_root_get() -> None:
    spec = {
        "openapi": "3.0.0",
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"name": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    }
                }
            }
        },
    }
    client = TestClient(create_app(spec))
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "api-mocker"
    assert "/users" in payload["mock_paths"]
