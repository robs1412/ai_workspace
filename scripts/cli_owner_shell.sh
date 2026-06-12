#!/usr/bin/env bash
# Source this from an interactive shell that may launch Codex from /Users/werkstatt.
# It keeps owner identity explicit for raw CLI sessions, where browser auth is absent.

ai_workspace_set_cli_owner() {
  case "${1:-}" in
    sonat|Sonat)
      export CODEX_OWNER_USER_ID=3
      export CODEX_OWNER_LABEL=Sonat
      export CODEX_OWNER_ROLE=ai-manager-sonat
      export CODEX_OWNER_WORKSPACE=ai
      ;;
    robert|Robert)
      export CODEX_OWNER_USER_ID=1
      export CODEX_OWNER_LABEL=Robert
      export CODEX_OWNER_ROLE=ai-manager-robert
      export CODEX_OWNER_WORKSPACE=ai
      ;;
    *)
      return 2
      ;;
  esac
}

ai_workspace_cli_owner_prompt() {
  case "${CODEX_OWNER_USER_ID:-}:${CODEX_OWNER_LABEL:-}" in
    3:Sonat)
      printf '%s' "CLI_OWNER_CONTEXT: Sonat is operating this Codex CLI session. CODEX_OWNER_USER_ID=3, CODEX_OWNER_LABEL=Sonat, CODEX_OWNER_ROLE=ai-manager-sonat. Load /Users/werkstatt/ai_workspace/worker_roles/ai-manager-sonat-startup.md, reply exactly READY AI Manager Sonat., and treat this as the AI Manager Sonat control lane. Do not infer Robert ownership from the shared /Users/werkstatt path, SSH host, or Unix account. Route substantive work through Task Manager / visible Workspaceboard workers and report to Sonat by default."
      ;;
    1:Robert)
      printf '%s' "CLI_OWNER_CONTEXT: Robert is operating this Codex CLI session. CODEX_OWNER_USER_ID=1, CODEX_OWNER_LABEL=Robert, CODEX_OWNER_ROLE=ai-manager-robert. Treat this as Robert-owned work unless a task packet says otherwise."
      ;;
    *)
      return 1
      ;;
  esac
}

codex() {
  if [ "$#" -eq 0 ]; then
    local owner_prompt
    if owner_prompt="$(ai_workspace_cli_owner_prompt 2>/dev/null)"; then
      command /usr/local/bin/codex -C "${PWD}" "$owner_prompt"
      return $?
    fi
  fi
  command /usr/local/bin/codex "$@"
}

sonatcodex() {
  ai_workspace_set_cli_owner sonat
  command /Users/werkstatt/ai_workspace/scripts/sonatcodex "$@"
}
