# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260407-CODEX-DASH-SESSION-01`
- Date Opened: `2026-04-07`
- Date Completed: `2026-04-07`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Restore reliable Codex dashboard session visibility on the Mac mini after the board runtime showed all terminal panes as detached or exited even when tmux sessions were still alive.

## Symptoms

- `http://127.0.0.1:17878/` was intermittently unavailable during LaunchAgent restarts.
- Board API initially marked all tracked sessions as `exited` or detached.
- Browser panes for exited sessions showed `[detached]` instead of useful history.
- Live tmux sessions existed on disk but were missing from the dashboard metadata after runtime restarts.

## Root Cause

- LaunchAgent started the Node server without `TMPDIR`, so Node resolved the tmux socket under `/tmp/...` while interactive tmux sessions lived under the macOS per-user temp root in `/var/folders/...`.
- LaunchAgent and direct starts were writing session metadata to different `tmp/` directories, so live sessions could disappear from the board after a restart.
- The frontend attempted live websocket attachment even for exited sessions, which guaranteed a `[detached]` message instead of showing captured history.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260407-CODEX-DASH-SESSION-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-04-07`
- Change Summary:
  - hardened `scripts/run_codex_dashboard.sh` to require a working Node runtime, export a consistent `TMPDIR`, and use shared machine-local dashboard state
  - made `scripts/start_codex_dashboard.sh` wait for LaunchAgent startup before falling back
  - updated `codex_dashboard/server/index.js` to use shared state and recover existing `codex-board-*` tmux sessions
  - updated `codex_dashboard/assets/app.js` so exited sessions show history instead of opening a dead live terminal

## Verification Notes

- `curl -fsS http://127.0.0.1:17878/api/status` returned the recovered running sessions on Mac mini:
  - `codex-board-b84d4334` (`AI Workspace`)
  - `codex-board-10d9d8d4` (`AI Workspace`)
  - `codex-board-e3aeb4cf` (`OPS`)
- Served `assets/app.js` included the history fallback for non-running sessions.
- Launchd runtime process environment confirmed both `TMPDIR` and `CODEX_DASHBOARD_STATE_DIR` were present.

## Rollback Plan

- Revert the launcher and dashboard source changes in `scripts/run_codex_dashboard.sh`, `scripts/start_codex_dashboard.sh`, `codex_dashboard/server/index.js`, and `codex_dashboard/assets/app.js`.
- Reinstall the LaunchAgent with the reverted source using `./scripts/install_codex_dashboard_launchagent.sh 17878`.

## Follow-Ups

- Reinstall the updated LaunchAgent on the MacBook and verify `http://127.0.0.1:17878/api/status` there once SSH or local access is available.
- Consider reducing the restart race in `install_codex_dashboard_launchagent.sh` so post-install health checks wait until the service is actually reachable.
