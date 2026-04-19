# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260417-MACMINI-WORKSPACEBOARD-UNREACHABLE-01`
- Date Opened: 2026-04-17 16:09 CDT
- Date Completed: 2026-04-17 16:25 CDT
- Owner: Codex
- Priority: High
- Status: Completed / mitigated

## Scope

Read-only incident check from the M4 workstation (`Mac.lan`, `192.168.55.35`) after Robert reported that Workspaceboard on the primary AI worker `.17` seemed crashed.

## Symptoms

- `ssh admin-macmini` and direct `ssh admin@192.168.55.17` timed out initially.
- Explicit key SSH with `~/.ssh/id_ed25519_m4_to_macmini` later returned `Host is down`.
- `ping 192.168.55.17` returned 100% packet loss.
- `curl http://192.168.55.17:17878/api/status` timed out.
- Local ARP showed `macmini.lan (192.168.55.17)` as incomplete after retries.
- Wake-on-LAN packet was sent to the last observed `.17` MAC, but `.17` did not return.
- Narrow checks of other likely LAN hosts did not find another Workspaceboard listener on port `17878`.

## Root Cause

Primary confirmed runtime risk: Workspaceboard was running under Node `v25.9.0`, while the terminal attach dependency (`node-pty`) loads cleanly under Node `v24.14.1` on this host. The launch logs contained a prior `node-pty` terminal attach crash and repeated older decision-sweep `command too long` errors. The initial network unreachability cleared after Robert opened Codex locally on the Mac mini, so that specific unreachable symptom remains likely host sleep/hang/network recovery rather than a confirmed router or SSH configuration fault.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260417-MACMINI-WORKSPACEBOARD-UNREACHABLE-01-ai-workspace`
- Commit SHA:
- Commit Date:
- Change Summary: Incident note opened and updated after mitigation; no SSH, router, firewall, or credential changes made.

### workspaceboard

- Repo Log ID: `AI-INC-20260417-MACMINI-WORKSPACEBOARD-UNREACHABLE-01-workspaceboard`
- Commit SHA: `c1c47d1`
- Commit Date: 2026-04-17
- Change Summary: Pinned Workspaceboard runtime back to Node `24` in `.nvmrc`, updated the LaunchAgent installer to honor Homebrew `node@<major>` paths for `.nvmrc` major versions, and reinstalled `com.koval.workspaceboard` on `Macmini.lan`.

## Verification Notes

- M4 local Workspaceboard on `127.0.0.1:17878` is healthy and reports `ok: true`, `board_version: 0.69`, host `Mac.lan`.
- M4 local Workspaceboard is not externally reachable on `192.168.55.35:17878`, consistent with local-only binding.
- Router `192.168.55.1` responded to ping, so the M4 is on the expected `192.168.55.0/24` LAN.
- Direct router SSH was not used because host-key verification stopped the connection; no SSH host-key bypass was performed.
- `macmini.lan` returned to reachability at `192.168.55.17`; SSH via `admin-macmini` works.
- Reinstalled `com.koval.workspaceboard` from `/Users/werkstatt/workspaceboard` on port `17878`.
- Live process now runs `/usr/local/opt/node@24/bin/node /Users/admin/.workspaceboard-launch/runtime/app/server/index.js`.
- Runtime `.node-version` is `v24.14.1`.
- `http://127.0.0.1:17878/api/status` returns `ok: true`, `board_version: 0.69`, host `Macmini.lan`.
- WebSocket terminal attach smoke test returned a `ready` message for live session `3e1329a0`.
- Manual `/api/decision-sweep` returned `ok: true`, `skipped: false`, `3` candidates, and a `7668` byte prompt.
- `server/test/session-status.test.js` passed under Node `v24.14.1` with `23` passing tests.
- LaunchAgent stderr log mtime remained `Apr 17 13:32:50 2026` after reinstall/smoke tests, so the visible `command too long` tail entries are stale, not continuing new errors.

## Rollback Plan

If Node 24 causes a separate regression, restore `.nvmrc` to `25.9.0`, rerun `./scripts/install_codex_dashboard_launchagent.sh 17878`, and verify terminal attach behavior separately. Do not switch back to Node 25 without either rebuilding/verifying `node-pty` for Node 25 or keeping the terminal attach guard confirmed.

## Follow-Ups

- Workspaceboard runtime pin was committed and pushed as `c1c47d1`; unrelated dirty Workspaceboard worktree edits were left untouched.
- If `.17` becomes unreachable again, first distinguish host sleep/network reachability from Workspaceboard process health with ping, SSH, ARP, LaunchAgent state, and local `127.0.0.1:17878/api/status`.
