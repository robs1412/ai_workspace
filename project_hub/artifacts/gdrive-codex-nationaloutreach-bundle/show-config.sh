#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_ROOT="/Users/werkstatt/ai_workspace"
source "$BUNDLE_DIR/env.sh"

exec "$PYTHON" "$AI_ROOT/project_hub/artifacts/gdrive-frank-metadata-bundle/authorize_frank_drive.py" \
  --client-file "$GOOGLE_DRIVE_CLIENT_FILE" \
  --token-file "$GOOGLE_DRIVE_LOCAL_TOKEN_FILE" \
  show-config --json
