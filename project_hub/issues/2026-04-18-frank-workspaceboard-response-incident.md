# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260418-FRANK-WB-RESPONSE-01`
- Date Opened: 2026-04-18
- Date Completed: pending iPhone confirmation
- Owner: Robert / AI Workspace
- Priority: High
- Status: Partially recovered; Frank route fixed, Workspaceboard runtime rebound, canonical-host guard tightened, phone path remains blocked on iPhone-specific DNS/TLS/auth behavior

## Scope

Recover two user-visible failures reported by Robert:

- Frank received direct emails but did not respond or visibly route the work.
- `wb.koval.lan/workspaceboard` did not serve on Robert's phone despite VPN.

## Symptoms

- Frank automation log showed direct Robert messages, including `Phone issue`, classified as `primary-input` with decision `logged-local-routing-no-email`.
- Frank sent no acknowledgement for those direct instructions.
- `wb.koval.lan` resolved to `192.168.55.205` and redirected unauthenticated users to `mi.koval.lan` login, but the Mac mini Workspaceboard runtime had drifted back to `127.0.0.1:17878`, so remote relay paths could not reach it.
- After the runtime bind was restored, phone access still failed. Additional unauthenticated checks showed `wb.koval.lan` redirects to `https://mi.koval.lan/login?redirect=https://wb.koval.lan/...`, while the Login app only consumed `referrer=` and the live login response issued a host-only `PHPSESSID`.
- Robert later confirmed `wb.koval.lan` works from MacBook but not iPhone, while direct `192.168.55.17` and `macmini.lan` must not be user-facing Workspaceboard paths.

## Root Cause

- Frank's installed `frank_auto_runner.py` intentionally avoided inbox-review noise for primary-input messages, but stopped after local logging instead of routing to Task Manager and sending the required captured/routed acknowledgement.
- `com.koval.workspaceboard` LaunchAgent environment had `CODEX_DASHBOARD_HOST=127.0.0.1` while serve mode remained `external`.
- The Workspaceboard phone path has an additional auth-gateway issue: `redirect=` from the MI gateway was not recognized by the Login source path, and host-only login cookies do not cross automatically from `mi.koval.lan` to `wb.koval.lan`.
- The remaining phone-only issue is likely not basic Mac mini reachability. Current suspects are iPhone VPN DNS/search behavior for `wb.koval.lan`, iOS/Safari trust of the internal mkcert HTTPS certificate served by `.205`, or an iPhone-specific login cookie/redirect behavior.

## Repo Logs

### ai_workspace / Frank Runtime

- Repo Log ID: `FRANK-RUNTIME-PRIMARY-ACK-20260418`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary:
  - Patched installed machine-local `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`.
  - Future direct Robert primary inputs now post a bounded brief to local Task Manager via `POST /api/task-manager/message`.
  - Future direct Robert primary inputs send a Robert-only captured/routed acknowledgement.
  - The two already-logged emails were manually routed to Task Manager because old runtime had already marked them processed.
  - Sent Robert-only recovery email `Frank and Workspaceboard recovery` with task id `frank-2026-runtime-wb-recovery-2026-04-18`.

- Repo Log ID: `FRANK-RUNTIME-CC-FYI-NOISE-20260418`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary:
  - Robert corrected that Claude-managed/status copies where Robert is already CC'd are for Frank's awareness only.
  - Tightened Frank directive docs and patched installed machine-local `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`.
  - Copied-only messages with no explicit Frank action request now classify as `cc-fyi-no-action` before credential/auth suspicious-keyword escalation.
  - Direct Frank requests and real safety/action blockers still route or escalate under existing gates.
  - No outbound email, credential read, Google OAuth/PubSub work, mailbox body print, or external-system mutation was performed.

### workspaceboard / Mac mini LaunchAgent

- Repo Log ID: `WB-REMOTE-BIND-RECOVERY-20260418`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary:
  - Reinstalled `com.koval.workspaceboard` from `/Users/werkstatt/workspaceboard` with `CODEX_DASHBOARD_HOST=0.0.0.0`.
  - Runtime now listens on `*:17878`.
  - Existing remote-auth guard remains active for nonlocal requests.

### login / Gateway Redirect Compatibility

- Repo Log ID: `LOGIN-WB-REDIRECT-COMPAT-20260418`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary:
  - Patched local Login source so the login page accepts the MI/auth gateway's `redirect=` parameter in addition to legacy `referrer=`.
  - Added a narrow absolute redirect allowlist for `https://wb.koval.lan/workspaceboard...` and `https://workspaceboard.koval.lan/workspaceboard...`.
  - Unapproved absolute redirects still collapse to `/ops/start.php`.
  - No deploy, push, live pull, credential output, production DB write, session mutation, or auth bypass was performed.

### workspaceboard / Canonical Host Guard

- Repo Log ID: `WB-CANONICAL-HOST-GUARD-20260419`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary:
  - `workspaceboard_auth.php` now allows Workspaceboard serving only for internal `localhost` / `127.0.0.1` requests or canonical remote hosts `wb.koval.lan` and `workspaceboard.koval.lan`.
  - Direct page/API hosts such as `192.168.55.17` and `macmini.lan` return `403 Workspaceboard Access Denied` with the approved `wb.koval.lan` URL.
  - No `.205` gateway config mutation or LaunchAgent restart was performed.

## Verification Notes

- `python3 -m py_compile /Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`
- Synthetic classifier check for a Claude `Password for ... Drive API setup` message with Frank only CC'd now returns `cc-fyi-no-action`, not `suspicious`.
- Frank dry-run with explicit launchd credential/log paths returned `[]`.
- Frank sent-log contains task id `frank-2026-runtime-wb-recovery-2026-04-18`.
- `launchctl print gui/501/com.koval.workspaceboard` shows `CODEX_DASHBOARD_HOST => 0.0.0.0`.
- `lsof -nP -iTCP:17878 -sTCP:LISTEN` shows `TCP *:17878`.
- `curl http://192.168.55.17:17878/api/status` returns `401 Unauthorized` without a valid session.
- `curl http://wb-direct.koval.lan:17878/api/status` returns `401 Unauthorized` without a valid session.
- `curl http://wb.koval.lan/workspaceboard/task-management-light.html` redirects unauthenticated users to `https://mi.koval.lan/login?...`.
- `curl -k https://wb.koval.lan/workspaceboard/task-management-light.html` returns a `307` to MI login with a `redirect=https://wb.koval.lan/...` query.
- `curl -k https://mi.koval.lan/login?...` returns `200` but currently sets a host-only `PHPSESSID` with no `Domain=.koval.lan`.
- `php -l /Users/werkstatt/login/index.php` and `php -l /Users/werkstatt/login/auth_helpers.php` passed.
- Local redirect tests preserve approved Workspaceboard redirect targets and collapse unapproved absolute redirects to `/ops/start.php`.
- `php -l /Users/werkstatt/workspaceboard/workspaceboard_auth.php` passed.
- `curl http://127.0.0.1/workspaceboard/task-management-light.html` and `curl http://localhost/workspaceboard/task-management-light.html` return `200`.
- `curl http://192.168.55.17/workspaceboard/task-management-light.html` and `curl http://macmini.lan/workspaceboard/task-management-light.html` return `403 Workspaceboard Access Denied`.
- `curl -k https://wb.koval.lan/workspaceboard/task-management-light.html` resolves to `192.168.55.205` and returns `307` to MI login when unauthenticated.

## Rollback Plan

- Frank runtime: restore the previous `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py` from backup/source history or edit the primary-input branches back to local logging only.
- Workspaceboard: rerun `/Users/werkstatt/workspaceboard/scripts/install_codex_dashboard_launchagent.sh 17878` without `CODEX_DASHBOARD_HOST=0.0.0.0` to bind back to localhost.
- Login source: revert the local `LOGIN-WB-REDIRECT-COMPAT-20260418` edits in `index.php` and `auth_helpers.php`.

## Follow-Ups

- Confirm Robert's phone can load `https://wb.koval.lan/workspaceboard/task-management-light.html` after MI login over VPN.
- On iPhone, distinguish the remaining failure: DNS/server-not-found, certificate/trust/secure-connection error, or redirect/login cookie loop.
- Route the approved Google OAuth / Gmail push work through Security Guard and a dedicated implementation worker before credential/OAuth operations.
- Decide whether the source Frank runtime should be moved from machine-local patching into a versioned repo path so this fix survives future runtime reinstalls.

## 2026-04-19 18:53 CDT Update — Phone Send UX Slice

- Source: Frank-routed Robert direct request, Message-ID `<CAAtX44ZRicy+8Rap2oNq9pqjZN7F1YwLzUspNw-k0F2CDeAuhw@mail.gmail.com>`, subject `Fix send in phone page`.
- Local Workspaceboard source fix: `task-manager-phone.html` now loads `assets/task-manager-phone.js?v=11`; the phone client clears the composer immediately into a queued/sending state, disables Send/template buttons while sending, blocks duplicate sends, shows progress copy for long requests, restores failed messages for retry, sends with `wait_ms: 0`, and defers summary refresh.
- Local timing did not reproduce a 15s backend send delay: Task Manager history was about `0.13s`, Task Manager summary was about `0.11s`, and management overview was about `5.09s` during read-only checks.
- Current auth/serving split remains: local runtime is healthy at Workspaceboard `v0.76`; direct `.17`/`macmini.lan` page hosts intentionally return `403`; direct LAN runtime API returns `401`; unauthenticated `wb.koval.lan` redirects to MI login; the redacted MI login response still showed a host-only `PHPSESSID` with no `.koval.lan` domain attribute.
- Guardrails: no `.205`, Traefik/proxy, DNS, LaunchAgent, service runtime, OAuth/auth credential, live session/cookie, production, deploy, live pull, commit, push, or restart action was performed.
- Verification: JS/PHP syntax checks, `npm test` in Workspaceboard `server` (`25` passing), local source Apache checks, and a non-mutating DOM/fetch harness with delayed mocked send passed. Chrome headless crashed before screenshot capture.
- Remaining approvals: Code/Git Manager closeout before commit/push/deploy/reinstall; Security Guard/Login/.205 owner approval before any auth-cookie, proxy, certificate/DNS, or service-runtime mutation.
