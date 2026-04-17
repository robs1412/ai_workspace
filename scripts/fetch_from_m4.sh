#!/bin/zsh
set -euo pipefail

HOST="${AI_TRANSFER_M4_HOST:-kovaladmin@192.168.55.35}"
IDENTITY="${AI_TRANSFER_M4_IDENTITY:-${HOME}/.ssh/id_ed25519_macmini_to_kovaladmin}"
FETCH="/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py"

usage() {
  cat <<'USAGE'
Usage:
  fetch_from_m4.sh <grant_id> <output_path>

Environment overrides:
  AI_TRANSFER_M4_HOST       default: kovaladmin@192.168.55.35
  AI_TRANSFER_M4_IDENTITY   default: ~/.ssh/id_ed25519_macmini_to_kovaladmin
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

GRANT_ID="$1"
OUTPUT_PATH="$2"

if [ ! -x "${FETCH}" ]; then
  echo "Fetch helper not found or not executable: ${FETCH}" >&2
  exit 1
fi

exec "${FETCH}" "${HOST}" "${GRANT_ID}" \
  --identity "${IDENTITY}" \
  --output "${OUTPUT_PATH}"
