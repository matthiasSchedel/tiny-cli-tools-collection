#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <packages/<name>>"
  exit 1
fi

PACKAGE_PATH="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-tests"

if [[ ! -f "$PACKAGE_PATH/pyproject.toml" ]]; then
  echo "No pyproject.toml found in $PACKAGE_PATH"
  exit 1
fi

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  python3 -m venv "$VENV_DIR"
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
fi

pushd "$PACKAGE_PATH" >/dev/null
python -m pip install -e ".[dev]"
python -m pytest tests
popd >/dev/null
