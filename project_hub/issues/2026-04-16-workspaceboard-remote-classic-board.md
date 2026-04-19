# Workspaceboard Remote Classic Board

- Master Incident ID: `AI-INC-20260416-WORKSPACEBOARD-REMOTE-CLASSIC-BOARD-01`
- Date Opened: 2026-04-16
- Date Completed: 2026-04-16
- Owner: Robert / Codex
- Priority: Medium
- Status: Completed

## Scope

Allow Robert to open the full classic Workspaceboard from the Mac mini LAN address at `http://192.168.55.17/workspaceboard/` and launch/attach live tmux sessions remotely, while preserving Portal-session authentication and the Workspaceboard remote allowlist.

## Symptoms

The authenticated Apache management pages were available remotely, but the classic `/workspaceboard/` page iframe depended on the Node runtime at `:17878`. The runtime was installed with `CODEX_DASHBOARD_HOST=127.0.0.1`, so remote browsers could not load the full board iframe or its live WebSocket terminal path.

## Root Cause

The runtime binding was intentionally localhost-only from the earlier narrow-exposure design. That kept the direct Node runtime private but prevented the classic iframe page from working on `192.168.55.17`.

## Repo Logs

### workspaceboard

- Repo Log ID: `WORKSPACEBOARD-REMOTE-CLASSIC-20260416`
- Commit SHA: `841e273c83340067013d5e04b5d08b2b23bbdded`
- Commit Date: 2026-04-16
- Change Summary: allowed `/workspaceboard/` through the remote Apache allowlist, made `index.php` emit the requested LAN host for the classic board iframe, documented the authenticated remote classic-board exception, and recorded Workspaceboard TODO closeout. Runtime was reinstalled with `CODEX_DASHBOARD_HOST=0.0.0.0`.

### ai_workspace

- Repo Log ID: `AI-WORKSPACE-HANDOFF-REMOTE-CLASSIC-20260416`
- Commit SHA: same commit as this project-hub log entry; see `ai_workspace` git history for the current SHA.
- Commit Date: 2026-04-16
- Change Summary: recorded the operational auth/session change in `AGENTS.md`, `HANDOFF.md`, and this project-hub detail log.

## Verification Notes

- Workspaceboard serve mode set to `external`.
- LaunchAgent `com.koval.workspaceboard` reports `CODEX_DASHBOARD_HOST => 0.0.0.0` and `state = running`.
- Local runtime health: `http://127.0.0.1:17878/api/status` returned `ok: true`, host `Macmini.lan`, and `tmux_available: true`.
- Unauthenticated direct LAN runtime check: `http://192.168.55.17:17878/api/status` returned `401 Unauthorized` with a Portal login redirect, confirming direct runtime auth validation is still active.

### 2026-04-17 Relapse Check

- Symptom: Robert reported `http://192.168.55.17/workspaceboard/` and then direct `http://192.168.55.17:17878/` were not serving after a Workspaceboard relaunch/reinstall.
- Cause: the installed LaunchAgent plist had reverted to `CODEX_DASHBOARD_HOST=127.0.0.1`; Node was running but listening only on `127.0.0.1:17878`, so Apache `/workspaceboard/` returned the iframe wrapper while the iframe target on the LAN host was connection-refused.
- Runtime fix: updated `/Users/admin/Library/LaunchAgents/com.koval.workspaceboard.plist` back to `CODEX_DASHBOARD_HOST=0.0.0.0`, then `bootout`/`bootstrap`/`kickstart` reloaded `com.koval.workspaceboard`.
- Verification at 2026-04-17 15:19 CDT: launchd reported `CODEX_DASHBOARD_HOST => 0.0.0.0`, `lsof` showed `TCP *:17878 (LISTEN)`, local and Apache `/workspaceboard/api/status` returned `ok: true`, unauthenticated direct LAN `/api/status` returned `401 Unauthorized`, unauthenticated direct LAN `/` returned `302` to `/login/`, `/workspaceboard/` returned the LAN iframe URL, and `/workspaceboard/task-management-light.html` plus its JS asset returned `200`.

## Rollback Plan

From `/Users/werkstatt/workspaceboard` on Mac mini:

```bash
CODEX_DASHBOARD_HOST=127.0.0.1 ./scripts/install_codex_dashboard_launchagent.sh 17878
php -r 'require "/Users/werkstatt/workspaceboard/workspaceboard_auth.php"; workspaceboard_write_serve_mode("localhost_only");'
curl -fsS http://127.0.0.1:17878/api/status
```

Confirm `launchctl print gui/$(id -u)/com.koval.workspaceboard` shows `CODEX_DASHBOARD_HOST => 127.0.0.1`.

## Follow-Ups

- Keep this exception limited to the Mac mini AI host unless Robert explicitly asks to expose another machine's classic board.
- If direct runtime auth validation, Portal session validation, or allowlist behavior breaks, revert immediately to localhost-only runtime binding.
