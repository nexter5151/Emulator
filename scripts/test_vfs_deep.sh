#!/usr/bin/env bash
# VFS с вложенностью не менее трёх уровней каталогов.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
VFS="${ROOT}/examples/vfs/deep.xml"
SCRIPT="${ROOT}/examples/startup_stage3.script"
echo ">>> python3 -m src.main --vfs ${VFS} --script ${SCRIPT}"
exec python3 -m src.main --vfs "$VFS" --script "$SCRIPT"
