# CLI Tools Monorepo

[![CI](https://github.com/matthiasSchedel/tiny-cli-tools-collection/actions/workflows/ci.yml/badge.svg)](https://github.com/matthiasSchedel/tiny-cli-tools-collection/actions/workflows/ci.yml)
[![Publish Package](https://github.com/matthiasSchedel/tiny-cli-tools-collection/actions/workflows/publish-package.yml/badge.svg)](https://github.com/matthiasSchedel/tiny-cli-tools-collection/actions/workflows/publish-package.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

This repository contains nine production-focused Python CLI tools, each in its own package folder with independent versioning and publishing.

The goal is practical open source quality:
- clear CLI contracts
- testable core logic
- documented package boundaries
- independent publishing to PyPI/TestPyPI

## Packages

| Package | Command | Purpose |
|---|---|---|
| `text-chunker` | `text-chunker` | Split text for LLM workflows using multiple strategies. |
| `api-mocker` | `api-mocker` | Run mock APIs from OpenAPI specs for local development and tests. |
| `rate-limiter` | `rate-limiter` | Wrap any shell command with token-bucket rate limiting. |
| `schema-guesser` | `schema-guesser` | Infer JSON Schema Draft 7 from example payloads. |
| `webhook-relay` | `webhook-relay` | Receive and inspect webhook requests locally with optional forwarding. |
| `page-differ` | `page-differ` | Compare HTML/URL inputs across DOM/content/visual modes. |
| `form-filler` | `form-filler` | Fill web forms declaratively from JSON/YAML data. |
| `json-patcher` | `json-patcher` | RFC 6902 patching, merging, diffing, and JSONPath querying. |
| `doc-renderer` | `doc-renderer` | Convert between common document formats via Pandoc. |

All package sources live under `packages/`.

## Repository Layout

```text
packages/
  text-chunker/
  api-mocker/
  rate-limiter/
  schema-guesser/
  webhook-relay/
  page-differ/
  form-filler/
  json-patcher/
  doc-renderer/
scripts/
  publish-package.sh
.github/workflows/
  ci.yml
  publish-package.yml
```

## Local Development

Use Python 3.10+.

```bash
# Optional: install all package dev environments
./scripts/bootstrap-all.sh

# Example: install one package in editable mode
cd packages/text-chunker
python3 -m pip install -e ".[dev]"
pytest

# Or via helper script from repo root
./scripts/test-package.sh packages/text-chunker
```

## Full Test Suite

Run the complete install + unit + E2E matrix locally:

```bash
./scripts/run_all_tests.sh
```

Run the same matrix in Docker:

```bash
./scripts/docker-test.sh
```

Notes:
- `form-filler` E2E auto-skips if Playwright browser binaries are unavailable.
- `doc-renderer` E2E auto-skips if `pandoc` is unavailable.

## Publish an Individual Package

Each package is independently publishable.

```bash
# TestPyPI
./scripts/publish-package.sh packages/text-chunker --testpypi

# PyPI
./scripts/publish-package.sh packages/text-chunker
```

See `PUBLISHING.md` for full details.

## Open Source Standards

- Contributor guide: `CONTRIBUTING.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- Security policy: `SECURITY.md`
- Support channels: `SUPPORT.md`
- Bug log and known issues: `BUGS.md`
- Project changelog: `CHANGELOG.md`
