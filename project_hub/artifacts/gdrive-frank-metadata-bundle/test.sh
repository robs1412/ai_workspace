#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
SCRIPT="$BUNDLE_DIR/drive.py"
DRIVE_ID="${1:-0AP-Yf32mH4IHUk9PVA}"

exec "$PYTHON" "$SCRIPT" test --drive-id "$DRIVE_ID"
