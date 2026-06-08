#!/usr/bin/env bash
set -euo pipefail

AI_ROOT="/Users/werkstatt/ai_workspace"
CALLBACK_FILE="$AI_ROOT/.private/google-oauth/nationaloutreach-chat-callback-url.txt"

callback="$(cat)"
callback="${callback//$'\r'/}"
callback="${callback//$'\n'/}"

if [[ -z "$callback" ]]; then
  echo "No callback URL received on stdin." >&2
  exit 2
fi
if [[ "$callback" != http://127.0.0.1:58080/oauth2callback* ]]; then
  echo "Callback URL did not match the expected localhost OAuth redirect." >&2
  exit 2
fi

umask 077
printf '%s\n' "$callback" > "$CALLBACK_FILE"
echo "Callback received."
