# api-mocker

Run local mock APIs from OpenAPI 3 specs.

## Install

```bash
python3 -m pip install api-mocker
```

## Usage

```bash
api-mocker openapi.yaml
api-mocker --port 3000 --log-file requests.jsonl --replay spec.yaml
```

## Features

- dynamic route creation from OpenAPI paths
- fake response generation from schemas
- optional request validation
- replay endpoints for recorded traffic
