# form-filler docs

## Local examples

```bash
form-filler --no-submit "file://$PWD/packages/form-filler/examples/contact-form.html" packages/form-filler/examples/contact-form.yaml
form-filler --no-submit "file://$PWD/packages/form-filler/examples/registration-step1.html" packages/form-filler/examples/registration.yaml
```

## Typed fields

```yaml
fields:
  - selector: "#email"
    value: "test@example.com"
    type: email
  - selector: "#country"
    value: "US"
    type: select
```
