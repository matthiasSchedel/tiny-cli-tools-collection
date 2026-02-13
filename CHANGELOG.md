# Changelog

All notable changes to this project will be documented in this file.

The format is inspired by Keep a Changelog and this project follows semantic versioning per package.

## [Unreleased]

### Added
- Monorepo with 9 independently publishable CLI packages.
- Packaging metadata and console entrypoints for each package.
- Unit test suites for each package.
- End-to-end CLI tests in `e2e/test_cli_e2e.py`.
- Full test harness script: `scripts/run_all_tests.sh`.
- Dockerized test harness: `Dockerfile.test` and `scripts/docker-test.sh`.
- Publish automation script: `scripts/publish-package.sh`.
- GitHub Actions workflows for CI and manual package publishing.
- Open-source governance docs (`CONTRIBUTING`, `SECURITY`, `SUPPORT`, templates).

### Fixed
- `api-mocker` dynamic route factory compatibility with FastAPI/Pydantic v2.
- Cross-package pytest import collision by running package tests in isolation.

