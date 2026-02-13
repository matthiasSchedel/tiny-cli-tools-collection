# schema-guesser docs

## Multi-sample inference

```bash
schema-guesser user-1.json user-2.json user-3.json > user.schema.json
```

## Strict mode

```bash
schema-guesser --strict --confidence 0.95 payloads.jsonl
```

