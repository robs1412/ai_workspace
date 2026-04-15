# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260312-OPS-SESSION-REHYDRATE-01`
- Date Opened: `2026-03-12 12:19:56 CDT`
- Date Completed:
- Owner: `Codex`
- Priority: `High`
- Status: `In Progress`
- Last Updated: `2026-03-23 19:01:44 CET (Machine: RobertMBP-2.local)`

## Scope

Stabilize OPS task/session behavior when OPS still has a local authenticated PHP session but has lost the corresponding Portal API JWT. Scope includes the shared login/SSO handoff path and OPS CRM token rehydration for task writes.

## Symptoms

- OPS shows the user as logged in and session indicators remain active.
- Task actions still fail with `CRM login failed: Login details provided does not exist or access denied.`
- The failure occurs even though the service account credentials themselves are valid.
- On `2026-03-13`, `ops/start.php` task move-down actions could return `Portal session expired. Please sign in again.` even though the task due date was updated.
- On `2026-03-13`, the OPS sidebar logout link still routed through the shared confirmation page because it used a GET request instead of the explicit POST logout flow.
- On `2026-03-23`, Mark reported that opening/editing a task from OPS could launch Portal as `Erik Johnson` instead of the currently signed-in OPS user.

## Root Cause

OPS `crm_hydrate_session_portal_token()` attempted recovery by requesting a fresh impersonated service-account login (`serviceuser:username`). That impersonation login path is currently rejected by the Portal API for real users such as `admin`, even while valid real-user JWTs are still present in `ops_sso_tokens`. As a result, OPS could not restore `$_SESSION['api_token']` and surfaced a misleading CRM login error instead of a portal-auth/session problem.

The remaining `2026-03-13` symptom was a second-order effect in OPS action fallbacks: task actions such as `shift_task_due_date`, `postpone_task`, and `complete_task` could successfully update local `vtiger_activity` rows after Portal auth failed, but the request-level `_ops_portal_auth_required` flag was left set, so the AJAX response was overwritten to `401 need_login`. Separately, the OPS sidebar logout entry still used `/login/logout.php?confirm=1`, which intentionally lands on the confirmation page rather than executing logout.

The `2026-03-23` cross-user login symptom came from a separate identity-validation gap in the same handoff chain. OPS `crm_hydrate_session_portal_token()` treated any non-expired `$_SESSION['api_token']` as valid before checking whether it matched the currently signed-in OPS user. `/login/sso/portal_launch.php` then reused that same cached JWT blindly when issuing the Portal SSO handoff. If a stale token from another user remained in session state, OPS could launch Portal as that other user.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-03-12-SESSION-REHYDRATE-01`
- Commit SHA: `d18ffc1`, `7bf9029`
- Commit Date: `2026-03-12`, `2026-03-23`
- Change Summary:
  - Added JWT claim helpers in `crm_integration.php`.
  - Added SSO-table JWT recovery using `ops_sso_tokens` before impersonated service login.
  - Changed failed impersonation-login fallback for write requests to surface portal auth required instead of the raw CRM login error.
  - On `2026-03-13`, updated `action_handler.php` so successful local task fallbacks clear the transient portal-auth-required flag instead of returning a false expired-session error.
  - On `2026-03-13`, updated `header.php` so OPS logout submits the shared POST + CSRF logout flow directly.
  - On `2026-03-23`, updated `crm_hydrate_session_portal_token()` so an existing session JWT is only reused when it matches the current OPS username/user id; mismatched cached tokens are discarded instead of being treated as valid.

### login

- Repo Log ID: `LOGIN-2026-03-12-SESSION-REHYDRATE-01`
- Commit SHA: `cd36ed5`
- Commit Date: `2026-03-23`
- Change Summary:
  - No code change in this slice.
  - Existing `ops_sso_tokens` data path was reused by OPS for JWT recovery.
  - On `2026-03-23`, updated `/login/sso/portal_launch.php` so it refuses a cached `$_SESSION['api_token']` when the JWT identity does not match the current `/login` session user, then falls back to a user-matched recent SSO JWT.

## Verification Notes

- `php -l /Users/admin/Documents/GitHub/ops/crm_integration.php` passed.
- Runtime check confirmed `crm_lookup_recent_sso_jwt('admin', 1)` now returns a JWT from `ops_sso_tokens`.
- Runtime check confirmed `crm_hydrate_session_portal_token('admin')` repopulates `$_SESSION['api_token']` successfully.
- Direct service-account login without impersonation still works.
- Direct impersonated service login for `admin` still fails, confirming the old fallback path was invalid.
- `php -l /Applications/MAMP/htdocs/ops/action_handler.php` passed on `2026-03-13`.
- `php -l /Applications/MAMP/htdocs/ops/header.php` passed on `2026-03-13`.
- Browser reproduction was not run in this slice; follow-up verification should confirm that task move-down no longer shows a login-expired message when the local fallback path succeeds, and that OPS logout signs out immediately.
- `php -l /Applications/MAMP/htdocs/ops/crm_integration.php` passed on `2026-03-23`.
- `php -l /Applications/MAMP/htdocs/login/sso/portal_launch.php` passed on `2026-03-23`.
- Synthetic JWT sanity checks on `2026-03-23` confirmed:
  - a fake `Erik` JWT in a `Mark` OPS session is now discarded by `crm_hydrate_session_portal_token('mark')`
  - a fake matching `Mark` JWT is still accepted
- Full browser reproduction of the Mark/Erik handoff was not completed in this turn because a fresh authenticated browser session and, if enforced, current 2FA code were not available.
- Live deployment:
  - `2026-03-23 19:01:44 CET`
  - host: `ftp.koval-distillery.com`
  - path: `/home/koval/public_html/ops`
  - `git pull --ff-only origin main` fast-forwarded cleanly to `7bf90291b6395e73cacf086ba3afc3dba334a384`
  - path: `/home/koval/public_html/login`
  - `git pull --ff-only origin master` fast-forwarded cleanly to `cd36ed578218c34af8b5ae16f0ff427101b8b00a`

## Rollback Plan

- Revert the `ops/crm_integration.php` changes.
- Restore previous behavior where OPS only tried cached impersonation tokens and fresh impersonated service logins.

## Follow-Ups

- Validate the fix through a real browser flow in OPS using a refreshed admin session and a task write.
- Consider moving shared JWT recovery helpers out of `login/sso/crm_token.php` into reusable helper code to avoid duplicate logic.
- Revisit whether `ops_sso_tokens` TTL should be extended or refreshed more intentionally for long-lived OPS sessions.
