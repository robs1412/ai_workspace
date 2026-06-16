# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260616-OPS-STAY-LOGGED-IN-SESSION-COOKIE-01`
- Date Opened: `2026-06-16`
- Date Completed: `2026-06-16`
- Owner: `Codex`
- Priority: `High`
- Status: `Pushed; live pull blocked`

## Scope

Fix the local Login/OPS session persistence path behind Robert's report that OPS dashboard task creation can show `Not authenticated.` after a few hours while the logout page still recognizes a logged-in session.

## Symptoms

- OPS AJAX/auth checks can lose authenticated identity and return `Not authenticated.`
- The login/logout surface can still see enough session state to say the browser is logged in.
- Recent OPS auth logs showed repeated `require_authentication_entry` events with no `myusername`, no `userid`, and no remember-cookie recovery on affected local requests.

## Root Cause

The shared login helper had two ordering/state bugs in the cookie recovery paths:

- `ensureSessionStarted()` retried with the incoming `PHPSESSID` after an empty alias session, but it did not recompute whether the retried session had auth before diagnostics and alias-cookie handling.
- `completeLogin()`, `remember_try_silent_login()`, and `ops_sso_apply_ops_session()` refreshed the canonical/alias session cookies before writing authenticated identity into `$_SESSION`.

Together those paths could preserve or re-emit a stale empty session id even when a later path could recover identity, causing OPS and Login to disagree about whether the browser was authenticated.

## Repo Logs

### login

- Repo Log ID: `AI-INC-20260616-OPS-STAY-LOGGED-IN-SESSION-COOKIE-01`
- Commit SHA: `669b448`
- Commit Date: `2026-06-16`
- Change Summary:
  - Added `login_session_has_auth()` so session auth checks are consistent.
  - Recomputed auth state after the `PHPSESSID` retry in `ensureSessionStarted()`.
  - Only mirrors alias cookies from `ensureSessionStarted()` after the active session has auth.
  - Moved session-cookie refresh in `completeLogin()` and `remember_try_silent_login()` to after authenticated identity is written.
  - Moved OPS SSO cookie refresh in `ops_sso_apply_ops_session()` to after authenticated identity is written.

## Verification Notes

- `php -l /Users/werkstatt/login/auth_helpers.php`
- `php -l /Users/werkstatt/login/sso_helpers.php`
- `php -r 'require "/Users/werkstatt/login/auth_helpers.php"; echo function_exists("login_session_has_auth") ? "helper ok\n" : "missing\n";'`
- `git -C /Users/werkstatt/login diff -- auth_helpers.php sso_helpers.php`
- `git -C /Users/werkstatt/login log -1 --oneline` returned `669b448 fix(auth): refresh session cookies after identity hydration`
- `git -C /Users/werkstatt/login ls-remote origin refs/heads/master` confirmed origin `master` at `669b44860d72...`
- `nc -vz -w 5 ftp.koval-distillery.com 22` succeeded.
- SSH command execution to `ftp.koval-distillery.com` and `koval@ftp.koval-distillery.com` timed out or exited `255` with no remote output before live checkout readback.

## Rollback Plan

- Revert the local changes to `/Users/werkstatt/login/auth_helpers.php` and `/Users/werkstatt/login/sso_helpers.php`.
- No live rollback is required unless this local patch is later committed, pushed, and deployed.

## Deployment State

- Local commit `669b448` pushed to `origin/master`.
- Live pull is blocked by SSH command execution failure before checkout readback.
- No live pull, credential change, password change, session database mutation, or production session mutation performed.
