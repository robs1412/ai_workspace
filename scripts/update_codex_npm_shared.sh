#!/usr/bin/env bash
set -euo pipefail

PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH
umask 0002

LOG_DIR="/Users/werkstatt/ai_workspace/runtime"
LOG_FILE="${LOG_DIR}/codex-npm-auto-update.log"
mkdir -p "${LOG_DIR}"

log() {
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$*" | tee -a "${LOG_FILE}"
}

normalize_tree() {
  local tree="$1"
  [ -e "${tree}" ] || return 0
  chgrp -R staff "${tree}" 2>/dev/null || true
  find "${tree}" -type d -exec chmod 2775 {} + 2>/dev/null || true
  find "${tree}" -type f -perm -111 -exec chmod 775 {} + 2>/dev/null || true
  find "${tree}" -type f ! -perm -111 -exec chmod 664 {} + 2>/dev/null || true
  find "${tree}" -type l -exec chmod -h 775 {} + 2>/dev/null || true
}

normalize_link() {
  local link="$1"
  [ -e "${link}" ] || [ -L "${link}" ] || return 0
  chgrp -h staff "${link}" 2>/dev/null || true
  chmod -h 775 "${link}" 2>/dev/null || true
}

log "starting codex/npm shared update"

mkdir -p /usr/local/lib/codex-cli-current
chgrp staff /usr/local/bin /usr/local/lib /usr/local/lib/node_modules /usr/local/lib/codex-cli-current 2>/dev/null || true
chmod 2775 /usr/local/bin /usr/local/lib /usr/local/lib/node_modules /usr/local/lib/codex-cli-current 2>/dev/null || true

# Update npm directly. Do not run a broad `npm update -g`: a legacy
# Sonat-owned @openai/codex global package may still exist under the old npm
# prefix and can block package replacement on macOS ACLs.
npm install -g npm@latest >>"${LOG_FILE}" 2>&1

# Update the shared Codex install used by /usr/local/bin/codex and Sonat's
# launcher without touching the legacy npm-global @openai/codex directory.
npm install --prefix /usr/local/lib/codex-cli-current @openai/codex@latest >>"${LOG_FILE}" 2>&1

normalize_tree /usr/local/lib/node_modules/npm
normalize_tree /usr/local/lib/codex-cli-current
find /usr/local/lib/node_modules/npm/bin -maxdepth 2 -type f -exec chmod 775 {} + 2>/dev/null || true
normalize_link /usr/local/bin/npm
normalize_link /usr/local/bin/npx
normalize_link /usr/local/bin/codex

if [ -x /usr/local/lib/codex-cli-current/node_modules/@openai/codex/bin/codex.js ]; then
  chmod 775 /usr/local/lib/codex-cli-current/node_modules/@openai/codex/bin/codex.js 2>/dev/null || true
fi

if [ -x /usr/local/bin/codex ]; then
  codex_version="$(/usr/local/bin/codex --version 2>&1)"
else
  codex_version="missing /usr/local/bin/codex"
fi
npm_version="$(npm -v 2>&1)"

log "completed codex=${codex_version} npm=${npm_version}"
