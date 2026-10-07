#!/usr/bin/env bash
# Этап 4: ls/cd/cat/rev/du на unix VFS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/unix.xml"
SCRIPT="${ROOT}/examples/startup_stage4.script"
echo ">>> python3 -m src.main --vfs ${VFS} --script ${SCRIPT}"
exec python3 -m src.main --vfs "$VFS" --script "$SCRIPT"
