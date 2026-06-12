#!/usr/bin/env bash
set -euo pipefail

owner="${1:-}"
case "$owner" in
  sonat|Sonat)
    owner="sonat"
    export AI_WORKSPACE_LOGIN_OWNER=sonat
    export CODEX_OWNER_USER_ID=3
    export CODEX_OWNER_LABEL=Sonat
    export CODEX_OWNER_ROLE=ai-manager-sonat
    export CODEX_OWNER_WORKSPACE=ai
    ;;
  robert|Robert)
    owner="robert"
    export AI_WORKSPACE_LOGIN_OWNER=robert
    export CODEX_OWNER_USER_ID=1
    export CODEX_OWNER_LABEL=Robert
    export CODEX_OWNER_ROLE=ai-manager-robert
    export CODEX_OWNER_WORKSPACE=ai
    ;;
  *)
    printf 'Usage: %s {sonat|robert}\n' "$0" >&2
    exit 2
    ;;
esac

if command -v zsh >/dev/null 2>&1; then
  zshdir="$(mktemp -d "${TMPDIR:-/tmp}/ai-owner-shell.XXXXXX")"
  cat > "${zshdir}/.zshrc" <<EOF
if [ -r "\$HOME/.zshrc" ]; then
  source "\$HOME/.zshrc"
fi
source /Users/werkstatt/ai_workspace/scripts/cli_owner_shell.sh
ai_workspace_set_cli_owner ${owner}
EOF
  export ZDOTDIR="${zshdir}"
  exec zsh -l
fi

shell="${SHELL:-/bin/bash}"
exec "$shell" -l
