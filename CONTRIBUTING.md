# Contributing

## Development Model

- Every CLI is an independent Python package under `packages/<name>`.
- Keep changes scoped to one package unless you are updating shared repo docs/workflows.
- Prefer small PRs with tests and docs updates in the same change.
- Use issue/PR templates for consistent triage and review quality.

## Setup

1. Install Python 3.10+.
2. Move into the package you want to change.
3. Install editable dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Optional for monorepo-wide setup:

```bash
./scripts/bootstrap-all.sh
```

## Quality Bar

- Add/adjust tests for behavior changes.
- Keep CLI output deterministic when possible.
- Provide clear error messages and non-zero exit codes on failure.
- Update package `README.md` and `docs/index.md` when CLI flags/behavior change.

## Pull Request Checklist

- [ ] Tests added or updated
- [ ] `pytest` passes for changed package
- [ ] `./scripts/run_all_tests.sh` passes for cross-package changes
- [ ] CLI help text is accurate
- [ ] README/docs updated
- [ ] Version bumped in package `pyproject.toml` when release behavior changes

## Release Notes

When behavior changes, add a concise entry to `CHANGELOG.md`.
