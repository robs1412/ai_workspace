# Sourced by owner launchers before Codex or the shared-server adapter starts.
# Resolve only the exact tmux pane's personal-terminal name; never infer by title.
if [[ -z "${WORKSPACEBOARD_SESSION_ID:-}" && -n "${TMUX:-}" && -n "${TMUX_PANE:-}" ]]; then
  wb_handoff_tmux_name="$(/usr/local/bin/tmux display-message -p -t "${TMUX_PANE}" '#{session_name}' 2>/dev/null || true)"
  if [[ "$wb_handoff_tmux_name" =~ ^wb-personal-([a-f0-9]{16})$ ]]; then
    export WORKSPACEBOARD_SESSION_ID="${BASH_REMATCH[1]}"
  fi
  unset wb_handoff_tmux_name
fi
