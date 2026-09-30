#!/usr/bin/env bash
# Только --script: выполнение стартового скрипта при открытии окна.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SCRIPT="${ROOT}/examples/startup_ok.script"
echo ">>> python3 -m src.main --script ${SCRIPT}"
exec python3 -m src.main --script "$SCRIPT"
