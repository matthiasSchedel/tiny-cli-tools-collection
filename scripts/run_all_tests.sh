#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-tests"
USE_SYSTEM_PYTHON="${USE_SYSTEM_PYTHON:-0}"

if [[ "${USE_SYSTEM_PYTHON}" != "1" && -z "${VIRTUAL_ENV:-}" ]]; then
  python3 -m venv "${VENV_DIR}"
  # shellcheck disable=SC1091
  source "${VENV_DIR}/bin/activate"
fi

python -m pip install --upgrade pip setuptools wheel

for package in "${ROOT_DIR}"/packages/*; do
  if [[ -f "${package}/pyproject.toml" ]]; then
    echo "[install] ${package}"
    python -m pip install -e "${package}[dev]"
  fi
done

echo "[test] unit tests"
for package in "${ROOT_DIR}"/packages/*; do
  if [[ -d "${package}/tests" ]]; then
    echo "[test] $(basename "${package}")"
    python -m pytest -q "${package}/tests"
  fi
done

echo "[test] e2e tests"
python -m pytest -q "${ROOT_DIR}"/e2e

echo "All tests passed."
