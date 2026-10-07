#!/usr/bin/env bash
# Минимальная VFS: один файл в корне.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/minimal.xml"
echo ">>> python3 -m src.main --vfs ${VFS}"
exec python3 -m src.main --vfs "$VFS"
