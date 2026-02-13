# Publishing Guide (Per Package)

Each folder in `packages/` is a standalone distributable Python package.

## Prerequisites

- PyPI and/or TestPyPI account
- API token configured in environment:
  - `TWINE_USERNAME=__token__`
  - `TWINE_PASSWORD=<pypi-token>`
- Build tools:

```bash
python3 -m pip install --upgrade build twine
```

## Manual Publish

```bash
# Dry run (build + twine check)
./scripts/publish-package.sh packages/<tool-name> --dry-run

# Upload to TestPyPI
./scripts/publish-package.sh packages/<tool-name> --testpypi

# Upload to PyPI
./scripts/publish-package.sh packages/<tool-name>
```

## GitHub Action Publish

Use workflow `Publish Package` with:
- `package_path`: e.g. `packages/text-chunker`
- `repository`: `pypi` or `testpypi`

Required repo secrets:
- `PYPI_API_TOKEN`
- `TEST_PYPI_API_TOKEN`

## Versioning

1. Update version in `packages/<tool-name>/pyproject.toml`.
2. Update package changelog if you maintain one.
3. Publish.

## Post-Publish Verification

```bash
python3 -m pip install <package-name> --index-url https://pypi.org/simple
<cli-command> --help
```
