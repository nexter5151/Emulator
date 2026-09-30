#!/usr/bin/env bash
# Только --vfs: имя VFS берётся из последнего компонента пути.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/sample-vfs"
mkdir -p "$VFS"
echo ">>> python3 -m src.main --vfs ${VFS}"
exec python3 -m src.main --vfs "$VFS"
