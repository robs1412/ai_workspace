#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$BUNDLE_DIR/env.sh"

export PYTHONPATH="$BUNDLE_DIR${PYTHONPATH:+:$PYTHONPATH}"
exec "$PYTHON" "$BUNDLE_DIR/chat-task-router.py" "$@"
