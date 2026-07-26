# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260704-LOGIN-SESSION-RECOVERY-01
- Date Opened: 2026-07-04
- Date Completed: 2026-07-04
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Restore remembered-browser login recovery for `/login` and OPS so successful 2FA sessions do not require daily phone verification after routine PHP session expiry.

## Symptoms

Robert reported being kicked out daily and needing phone 2FA despite checking "Remember this device" during `/login`.

## Root Cause

Live `/login/.login.env` had `LOGIN_AUTO_RECOVERY_REMEMBER=0`, disabling automatic remembered-session recovery on production. The code default is enabled, but the live override forced recovery off.

## Repo Logs

### login

- Repo Log ID: login-session-recovery-20260704
- Commit SHA: `076b273`
- Commit Date: 2026-07-04
- Change Summary: Tracked `/login/.login.env` now enables automatic recovery and sets `LOGIN_AUTO_RECOVERY_TTL_SECONDS=2592000` so remembered browsers can recover for 30 days.

## Verification Notes

- Local syntax checks passed for `auth_helpers.php`, `index.php`, `checklogin.php`, and `verify_2fa.php`.
- Pushed `076b273` to `origin/master`.
- Live `/home/koval/public_html/login` fast-forwarded to `076b273`.
- Live readback:
  - branch `master`
  - HEAD `076b273`
  - last commit `Keep login sessions recoverable`
  - `auto_recovery=on`
  - `auto_recovery_ttl=2592000`
  - `remember_ttl=2592000`
  - `session_ttl=2592000`
- Live PHP syntax checks passed for `auth_helpers.php`, `index.php`, `checklogin.php`, and `verify_2fa.php`.
- Remaining live dirty file after pull is `logs/sso_ops_token.log`, a runtime log that existed before this deploy.

## Rollback Plan

Set `LOGIN_AUTO_RECOVERY_REMEMBER=0` in `/login/.login.env`, commit, push, and fast-forward pull live. This would restore daily/expiry-driven reauthentication behavior.

## Follow-Ups

- Robert should complete one normal 2FA login on his browser so the new recovery token is issued under the enabled config.
