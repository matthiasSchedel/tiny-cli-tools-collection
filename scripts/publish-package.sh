#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <packages/<name>> [--testpypi] [--dry-run]"
  exit 1
fi

PACKAGE_PATH="$1"
shift || true

REPO_URL="https://upload.pypi.org/legacy/"
DRY_RUN="false"

for arg in "$@"; do
  case "$arg" in
    --testpypi)
      REPO_URL="https://test.pypi.org/legacy/"
      ;;
    --dry-run)
      DRY_RUN="true"
      ;;
    *)
      echo "Unknown argument: $arg"
      exit 1
      ;;
  esac
done

if [[ ! -f "$PACKAGE_PATH/pyproject.toml" ]]; then
  echo "No pyproject.toml found in $PACKAGE_PATH"
  exit 1
fi

pushd "$PACKAGE_PATH" >/dev/null
rm -rf dist build *.egg-info
python3 -m build
python3 -m twine check dist/*

if [[ "$DRY_RUN" == "true" ]]; then
  echo "Dry run complete. Artifacts built and verified."
  popd >/dev/null
  exit 0
fi

python3 -m twine upload --repository-url "$REPO_URL" dist/*
popd >/dev/null

echo "Published $PACKAGE_PATH"
