# webhook-relay

Receive webhooks locally, inspect payloads, and replay captured requests.

## Install

```bash
python3 -m pip install webhook-relay
```

## Usage

```bash
webhook-relay
webhook-relay --forward http://localhost:3000 --storage webhooks.db
webhook-relay --validate-signature github --secret your-secret
```

## Notes

- Live UI updates use WebSocket when available.
- If your Uvicorn install does not include WebSocket support, the UI now falls back to periodic polling automatically.
