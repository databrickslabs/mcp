#!/usr/bin/env bash
set -euo pipefail

# Usage: ./lint.sh [--fix]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIX=false

if [[ "${1:-}" == "--fix" ]]; then
  FIX=true
fi

echo "Linting Python files in servers/... with black and ruff"
uv pip install --system black ruff

if $FIX; then
  echo "🛠  Fixing formatting with black and ruff"
  black servers/
  ruff check servers/ --fix
else
  echo "🔍 Checking formatting (without fixing)"
  if ! black servers/ --check; then
    echo -e "\n❌ Black found formatting issues. To fix them, run:"
    echo "   ./dev/lint.sh --fix"
    exit 1
  fi

  if ! ruff check servers/; then
    echo -e "\n❌ Ruff found issues. To fix them, run:"
    echo "   ./dev/lint.sh --fix"
    exit 1
  fi
fi
