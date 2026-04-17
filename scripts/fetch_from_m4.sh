#!/bin/zsh
set -euo pipefail

HOST="${AI_TRANSFER_M4_HOST:-kovaladmin@192.168.55.35}"
IDENTITY="${AI_TRANSFER_M4_IDENTITY:-${HOME}/.ssh/id_ed25519_macmini_to_kovaladmin}"
FETCH="/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py"

usage() {
  cat <<'USAGE'
Usage:
  fetch_from_m4.sh <grant_id> <output_path>
  fetch_from_m4.sh --shared <relative_file_path> <output_path>
  fetch_from_m4.sh --shared-archive <relative_path> <output_tar_gz>
  fetch_from_m4.sh --shared-list [relative_path] <output_json>

Environment overrides:
  AI_TRANSFER_M4_HOST       default: kovaladmin@192.168.55.35
  AI_TRANSFER_M4_IDENTITY   default: ~/.ssh/id_ed25519_macmini_to_kovaladmin
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

if [ ! -x "${FETCH}" ]; then
  echo "Fetch helper not found or not executable: ${FETCH}" >&2
  exit 1
fi

case "${1:-}" in
  --shared)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    exec "${FETCH}" "${HOST}" "shared" --identity "${IDENTITY}" --shared-file "$2" --output "$3"
    ;;
  --shared-archive)
    [ "$#" -eq 3 ] || { usage; exit 2; }
    exec "${FETCH}" "${HOST}" "shared" --identity "${IDENTITY}" --shared-archive "$2" --output "$3"
    ;;
  --shared-list)
    if [ "$#" -eq 2 ]; then
      exec "${FETCH}" "${HOST}" "shared" --identity "${IDENTITY}" --shared-list "." --output "$2"
    elif [ "$#" -eq 3 ]; then
      exec "${FETCH}" "${HOST}" "shared" --identity "${IDENTITY}" --shared-list "$2" --output "$3"
    else
      usage
      exit 2
    fi
    ;;
  *)
    [ "$#" -eq 2 ] || { usage; exit 2; }
    exec "${FETCH}" "${HOST}" "$1" --identity "${IDENTITY}" --output "$2"
    ;;
esac
