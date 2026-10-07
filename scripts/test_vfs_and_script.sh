#!/usr/bin/env bash
# VFS + стартовый скрипт с ошибочными командами.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/deep.xml"
SCRIPT="${ROOT}/examples/startup_with_errors.script"
echo ">>> python3 -m src.main --vfs ${VFS} --script ${SCRIPT}"
exec python3 -m src.main --vfs "$VFS" --script "$SCRIPT"
