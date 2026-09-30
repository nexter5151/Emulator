#!/usr/bin/env bash
# Запуск без параметров — значения по умолчанию, отладочный вывод в stderr.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo ">>> python3 -m src.main"
exec python3 -m src.main
