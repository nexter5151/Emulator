#!/usr/bin/env bash
# Ошибка: неверный XML VFS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/invalid.xml"
echo ">>> python3 -m src.main --vfs ${VFS}"
exec python3 -m src.main --vfs "$VFS"
