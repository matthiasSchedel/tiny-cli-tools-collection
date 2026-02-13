# Bug Log

This file tracks bugs found by the automated unit + E2E suites.

## Open

None.

## Resolved

1. `api-mocker` route registration failed on FastAPI/Pydantic v2 when creating dynamic endpoints.
   - Repro: `pytest packages/api-mocker/tests/test_server.py`
   - Error: `NameError: Fields must not use names with leading underscores`
   - Root cause: endpoint default parameters (`_response_schema`, `_request_schema`) were interpreted as request body fields.
   - Fix: replaced default-parameter closure with an endpoint factory that captures state in outer scope.
   - Status: Resolved

2. Full-suite test collection failed with duplicate test module names across packages.
   - Repro: `pytest packages/*/tests`
   - Error: `import file mismatch` for `test_utils.py`
   - Root cause: pytest module import collision between package test folders with identical filenames.
   - Fix: `scripts/run_all_tests.sh` now executes each package test directory in isolation.
   - Status: Resolved
