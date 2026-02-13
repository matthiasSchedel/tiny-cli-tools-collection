#!/usr/bin/env bash
set -euo pipefail

for package in packages/*; do
  if [[ -f "$package/pyproject.toml" ]]; then
    echo "Installing $package"
    python3 -m pip install -e "$package[dev]"
  fi
done

echo "Done."
