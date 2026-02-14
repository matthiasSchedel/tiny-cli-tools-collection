# webhook-relay docs

## Inspect captured requests

Open the UI at `http://127.0.0.1:8080/` after starting:

```bash
webhook-relay --storage webhooks.db
```

## Replay to local service

```bash
webhook-relay --forward http://localhost:3000
```

If WebSocket dependencies are unavailable in your Uvicorn install, the UI will automatically fall back to polling.
