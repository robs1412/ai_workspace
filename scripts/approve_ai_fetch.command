#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GATE="${SCRIPT_DIR}/ai_transfer_gate.py"

if [ ! -x "${GATE}" ]; then
  echo "Transfer gate not found or not executable: ${GATE}" >&2
  echo
  echo "Press Return to close."
  read -r _ || true
  exit 1
fi

FILE_PATH="${1:-}"
if [ -z "${FILE_PATH}" ]; then
  FILE_PATH="$(osascript <<'APPLESCRIPT'
try
  set chosenFile to choose file with prompt "Choose the file that Macmini.lan may fetch once."
  POSIX path of chosenFile
on error number -128
  return ""
end try
APPLESCRIPT
)"
fi

if [ -z "${FILE_PATH}" ]; then
  echo "No file selected."
  echo
  echo "Press Return to close."
  read -r _ || true
  exit 0
fi

echo "Creating one-time Macmini.lan fetch grant..."
echo
OUTPUT="$("${GATE}" approve "${FILE_PATH}")"
printf '%s\n' "${OUTPUT}"

GRANT="$(printf '%s\n' "${OUTPUT}" | awk '/^Grant:/{print $2}')"
CODE="$(printf '%s\n' "${OUTPUT}" | awk '/^Code:/{print $2}')"

if [ -n "${GRANT}" ] && [ -n "${CODE}" ]; then
  printf 'Grant: %s\nCode: %s\n' "${GRANT}" "${CODE}" | pbcopy
  echo
  echo "Grant id and code copied to clipboard."
  echo "Paste them into the Macmini.lan fetch request only for this transfer."
fi

echo
echo "Press Return to close."
read -r _ || true
