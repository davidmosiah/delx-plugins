#!/usr/bin/env bash
# Local test runner. Do not wire this to GitHub Actions.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m unittest discover -s tests -t . -v
