# schema-guesser

Infer JSON Schema Draft 7 from example JSON data.

## Install

```bash
python3 -m pip install schema-guesser
```

## Usage

```bash
schema-guesser data.json
schema-guesser --confidence 0.9 sample1.json sample2.json
curl https://api.example.com/users | schema-guesser --stdin --format yaml
```
