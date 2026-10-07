#!/usr/bin/env bash
# Этап 5: mkdir и help на unix VFS.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/unix.xml"
SCRIPT="${ROOT}/examples/startup_stage5.script"
echo ">>> python3 -m src.main --vfs ${VFS} --script ${SCRIPT}"
exec python3 -m src.main --vfs "$VFS" --script "$SCRIPT"
