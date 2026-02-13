# rate-limiter docs

## Command Wrapper Pattern

```bash
for url in $(cat urls.txt); do
  rate-limiter --rpm 30 -- curl "$url"
done
```

## Persistent State

```bash
rate-limiter --rpm 120 --state-file ~/.cache/rate.json --key my-api -- my-cli sync
```

