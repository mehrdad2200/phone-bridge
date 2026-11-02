#!/usr/bin/env bash
# Phone Bridge launcher for Linux/macOS: creates ./.venv on first run, installs deps, starts the app.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q -r requirements.txt
fi
exec .venv/bin/python phone_bridge.py "$@"
