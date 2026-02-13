# form-filler

Fill and optionally submit web forms from JSON/YAML definitions.

## Install

```bash
python3 -m pip install form-filler
playwright install chromium
```

## Usage

```bash
form-filler https://example.com/contact examples/contact-form.yaml
form-filler --no-submit --screenshot https://example.com/form data.json
```
