#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$BUNDLE_DIR/env.sh"

exec "$PYTHON" "$BUNDLE_DIR/chat-test.py"
