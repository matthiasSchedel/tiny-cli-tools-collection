# rate-limiter

Universal CLI wrapper with token-bucket rate limiting.

## Install

```bash
python3 -m pip install rate-limiter
```

## Usage

```bash
rate-limiter --rpm 60 -- curl https://api.example.com
rate-limiter --rpm 100 --state-file ~/.cache/limits.json --key github -- gh api /user
```
