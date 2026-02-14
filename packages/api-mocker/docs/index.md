# api-mocker docs

## Start a mock server

```bash
api-mocker examples/petstore.yaml
```

If the spec has no `GET /`, the root URL (`/`) returns service metadata and links to `/docs`.

## Enable replay API

```bash
api-mocker --replay --log-file requests.jsonl examples/petstore.yaml
```
