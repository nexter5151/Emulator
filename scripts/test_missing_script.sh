#!/usr/bin/env bash
# Несуществующий стартовый скрипт — сообщение об ошибке при запуске.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MISSING="${ROOT}/examples/no_such_script.script"
echo ">>> python3 -m src.main --script ${MISSING}"
exec python3 -m src.main --script "$MISSING"
