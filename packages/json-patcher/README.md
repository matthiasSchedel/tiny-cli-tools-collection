# json-patcher

Patch, merge, diff, and query JSON documents from the command line.

## Install

```bash
python3 -m pip install json-patcher
```

## Usage

```bash
json-patcher patch data.json --patch ops.json
json-patcher merge base.json override.json --strategy smart
json-patcher diff old.json new.json
json-patcher query data.json "$.users[*].email"
```
