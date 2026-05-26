#!/bin/zsh
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 YYYY-MM-DD"
  exit 1
fi

DATE_DIR="$1"
ROOT="/Users/werkstatt/ai_workspace/recordings/trainual/ops-project-management/$DATE_DIR"
MANIFEST="$ROOT/manifest.md"

mkdir -p "$ROOT"

if [[ ! -f "$MANIFEST" ]]; then
  cat > "$MANIFEST" <<EOF
# OPS Project Management Recording Manifest

- date: $DATE_DIR
- owner:
- workspace: /Users/werkstatt/ops
- storage_class: local-only
- location:
- media_type: screen-recording
- environment: local authenticated OPS
- demo_data_status:
- save_action_status:
- review_status:
- related_manual:
  - /Users/werkstatt/ops/docs/project_management_manual.php
- notes:
EOF
fi

echo "$MANIFEST"
