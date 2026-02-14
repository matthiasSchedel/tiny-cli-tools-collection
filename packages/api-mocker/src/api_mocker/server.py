from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .generator import generate_from_schema
from .logger import RequestLogger
from .validator import validate_body


def load_spec(spec_path: Path) -> Dict[str, Any]:
    content = spec_path.read_text(encoding="utf-8")
    if spec_path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(content)
    return json.loads(content)


def _resolve_response(operation: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
    responses = operation.get("responses", {})
    for code, payload in responses.items():
        try:
            status_code = int(code)
        except ValueError:
            continue
        media = payload.get("content", {}).get("application/json", {})
        schema = media.get("schema", {})
        return status_code, schema
    return 200, {"type": "object", "properties": {"message": {"type": "string"}}}


def _resolve_request_schema(operation: Dict[str, Any]) -> Dict[str, Any]:
    request_body = operation.get("requestBody", {})
    content = request_body.get("content", {})
    media = content.get("application/json", {})
    return media.get("schema", {})


def _build_endpoint(
    *,
    response_status: int,
    response_schema: Dict[str, Any],
    request_schema: Dict[str, Any],
    validate_requests: bool,
    delay_ms: int,
    logger: RequestLogger,
):
    async def endpoint(request: Request):
        body = None
        if request.method in {"POST", "PUT", "PATCH"}:
            try:
                body = await request.json()
            except Exception:
                body = None
        if validate_requests and request_schema and body is not None:
            errors = validate_body(request_schema, body)
            if errors:
                raise HTTPException(status_code=400, detail={"validation_errors": errors})
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000)
        response_body = generate_from_schema(response_schema)
        entry = logger.add(
            method=request.method,
            path=request.url.path,
            headers=dict(request.headers),
            body=body,
            response_status=response_status,
            response_body=response_body,
        )
        response = JSONResponse(status_code=response_status, content=response_body)
        response.headers["X-Mock-Request-Id"] = str(entry.id)
        return response

    return endpoint


def create_app(
    spec: Dict[str, Any],
    *,
    log_requests: bool = True,
    log_file: Optional[Path] = None,
    replay: bool = False,
    delay_ms: int = 0,
    cors: bool = True,
    validate_requests: bool = True,
) -> FastAPI:
    app = FastAPI(title="api-mocker")
    logger = RequestLogger(log_file=log_file if log_requests else None)

    if cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    paths = spec.get("paths", {})
    if not paths:
        raise ValueError("No paths found in OpenAPI spec.")

    root_path_methods = paths.get("/", {})
    has_root_get = any(method.lower() == "get" for method in root_path_methods.keys())
    if not has_root_get:

        @app.get("/", include_in_schema=False)
        async def root():
            return {
                "service": "api-mocker",
                "docs": "/docs",
                "redoc": "/redoc",
                "mock_paths": sorted(paths.keys()),
            }

    for raw_path, methods in paths.items():
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            response_status, response_schema = _resolve_response(operation)
            request_schema = _resolve_request_schema(operation)
            endpoint = _build_endpoint(
                response_status=response_status,
                response_schema=response_schema,
                request_schema=request_schema,
                validate_requests=validate_requests,
                delay_ms=delay_ms,
                logger=logger,
            )
            app.add_api_route(raw_path, endpoint, methods=[method.upper()])

    if replay:

        @app.get("/_mock/requests")
        async def list_requests():
            return [asdict(entry) for entry in logger.list_entries()]

        @app.get("/_mock/requests/{request_id}")
        async def get_request(request_id: int):
            item = logger.get(request_id)
            if not item:
                raise HTTPException(status_code=404, detail="Request not found")
            return asdict(item)

        @app.post("/_mock/replay/{request_id}")
        async def replay_request(request_id: int):
            item = logger.get(request_id)
            if not item:
                raise HTTPException(status_code=404, detail="Request not found")
            return {"replayed": True, "request": asdict(item)}

    return app
