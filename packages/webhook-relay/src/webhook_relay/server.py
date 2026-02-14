from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Set

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .signatures import validate_signature
from .storage import RelayStorage
from .ui import static_dir


class ConnectionHub:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def broadcast(self, payload: dict) -> None:
        for conn in list(self._connections):
            try:
                await conn.send_text(json.dumps(payload))
            except Exception:
                self.disconnect(conn)


def _websocket_supported() -> bool:
    try:
        import websockets  # noqa: F401

        return True
    except Exception:
        pass
    try:
        import wsproto  # noqa: F401

        return True
    except Exception:
        return False


def create_app(
    *,
    forward_url: str | None,
    storage_path: Path | None,
    signature_provider: str | None,
    secret: str | None,
    capacity: int,
    websocket_enabled: bool | None = None,
) -> FastAPI:
    app = FastAPI(title="webhook-relay")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    storage = RelayStorage(storage_path=storage_path, capacity=capacity)
    hub = ConnectionHub()
    ws_enabled = _websocket_supported() if websocket_enabled is None else websocket_enabled

    static = static_dir()
    app.mount("/_relay/static", StaticFiles(directory=static), name="relay-static")

    @app.get("/")
    async def index():
        return FileResponse(static / "index.html")

    if ws_enabled:

        @app.websocket("/_relay/ws")
        async def ws(websocket: WebSocket):
            await hub.connect(websocket)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                hub.disconnect(websocket)

    @app.get("/_relay/capabilities")
    async def capabilities():
        return {"websocket": ws_enabled}

    @app.get("/_relay/requests")
    async def list_requests():
        return [asdict(item) for item in storage.list()]

    @app.get("/_relay/requests/{request_id}")
    async def get_request(request_id: str):
        item = storage.get(request_id)
        if not item:
            raise HTTPException(status_code=404, detail="Request not found")
        return asdict(item)

    @app.delete("/_relay/requests/{request_id}")
    async def delete_request(request_id: str):
        if not storage.delete(request_id):
            raise HTTPException(status_code=404, detail="Request not found")
        return {"deleted": True, "id": request_id}

    @app.post("/_relay/replay/{request_id}")
    async def replay_request(request_id: str):
        item = storage.get(request_id)
        if not item:
            raise HTTPException(status_code=404, detail="Request not found")
        if not forward_url:
            return {"replayed": False, "reason": "No --forward URL configured."}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.request(
                method=item.method,
                url=forward_url.rstrip("/") + item.path,
                content=item.body.encode("utf-8"),
                headers=item.headers,
                params=item.query_params,
            )
        return {"replayed": True, "status_code": response.status_code}

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    async def catch_all(path: str, request: Request):
        if path.startswith("_relay/"):
            raise HTTPException(status_code=404, detail="Not found")

        body = await request.body()
        signature_valid = validate_signature(signature_provider, secret, request.headers, body)
        forwarded_status: Optional[int] = None

        if forward_url:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.request(
                    method=request.method,
                    url=forward_url.rstrip("/") + "/" + path,
                    headers=dict(request.headers),
                    params=dict(request.query_params),
                    content=body,
                )
                forwarded_status = resp.status_code

        saved = storage.insert(
            method=request.method,
            path="/" + path,
            headers=dict(request.headers),
            body=body.decode("utf-8", errors="replace"),
            query_params=dict(request.query_params),
            forwarded_status=forwarded_status,
            signature_valid=signature_valid,
        )
        await hub.broadcast(
            {
                "type": "new_request",
                "request": {
                    "id": saved.id,
                    "method": saved.method,
                    "path": saved.path,
                    "timestamp": saved.timestamp,
                },
            }
        )
        return JSONResponse(
            status_code=200,
            content={"received": True, "id": saved.id, "signature_valid": signature_valid},
        )

    return app
