# page-differ

Detect semantic changes between two web page versions.

## Install

```bash
python3 -m pip install page-differ
```

## Usage

```bash
page-differ https://example.com/v1 https://example.com/v2
page-differ --mode dom old.html new.html
page-differ --mode visual --screenshots before.html after.html
```
