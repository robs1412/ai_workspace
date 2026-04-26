#!/usr/bin/env bash
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
SCRIPT="$BUNDLE_DIR/drive.py"

JSON_FLAG=""
FOLDER_ARG=""

for arg in "$@"; do
    case "$arg" in
        --json) JSON_FLAG="--json" ;;
        *) FOLDER_ARG="$arg" ;;
    esac
done

if [[ -n "$FOLDER_ARG" ]]; then
    if [[ "$FOLDER_ARG" == http* ]]; then
        FOLDER_ID=$("$PYTHON" "$SCRIPT" folder-id "$FOLDER_ARG")
    else
        FOLDER_ID="$FOLDER_ARG"
    fi
    exec "$PYTHON" "$SCRIPT" list --folder-id "$FOLDER_ID" $JSON_FLAG
else
    exec "$PYTHON" "$SCRIPT" list $JSON_FLAG
fi
