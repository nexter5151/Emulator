#!/usr/bin/env bash
# VFS с несколькими файлами и каталогом.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/multi.xml"
echo ">>> python3 -m src.main --vfs ${VFS}"
exec python3 -m src.main --vfs "$VFS"
