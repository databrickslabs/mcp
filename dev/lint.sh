#!/usr/bin/env bash
set -euo pipefail

# Usage: ./lint.sh [--fix]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX=false

if [[ "${1:-}" == "--fix" ]]; then
  FIX=true
fi

echo "Linting Python files in servers/... with black and ruff"

if $FIX; then
  echo "🛠  Fixing formatting with black and ruff"
  uv pip install --system black ruff
  black servers/
  ruff check servers/ --fix
else
  uv pip install --system black ruff
  echo "🔍 Checking formatting (without fixing)"
  black servers/ --check
  ruff check servers/
fi
