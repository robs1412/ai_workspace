#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_ROOT="/Users/werkstatt/ai_workspace"
source "$BUNDLE_DIR/env.sh"

exec "$PYTHON" "$AI_ROOT/project_hub/artifacts/gdrive-frank-metadata-bundle/drive.py" list --folder-id "$GOOGLE_DRIVE_TEST_DRIVE_ID" "$@"
