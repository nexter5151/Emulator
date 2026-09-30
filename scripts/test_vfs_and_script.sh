#!/usr/bin/env bash
# Оба параметра: VFS + стартовый скрипт с ошибочными командами.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/my-vfs-root"
SCRIPT="${ROOT}/examples/startup_with_errors.script"
mkdir -p "$VFS"
echo ">>> python3 -m src.main --vfs ${VFS} --script ${SCRIPT}"
exec python3 -m src.main --vfs "$VFS" --script "$SCRIPT"
