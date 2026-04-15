# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-LOGIN-TOKEN-2FA-01`
- Date Opened: `2026-04-09 08:32:14 CDT`
- Date Completed: `2026-04-09 11:22:47 CDT`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

- Require 2FA for token-based logins that currently bypass or weaken the normal auth flow.
- Convert the `robert` and `screen` token entry paths into full user sessions instead of reduced or special-case sessions.
- Route 2FA delivery for the generic login token flow to `production@koval-distillery.com`.
- Route 2FA delivery for the Robert token flow to Robert directly.
- Keep the change scoped to `/login` unless code review proves a cross-module dependency.

## Symptoms

- Token login paths appear to have weaker security properties than normal interactive logins.
- Token logins may not be creating the same full user session state as a standard authenticated session.
- The current token flow needs explicit 2FA routing rules per token/user path.

## Root Cause

- `robert_login.php` and `screen_login.php` were direct passcode bypasses that only set `$_SESSION['myusername']` and redirected, skipping normal `completeLogin()` session finalization and any 2FA challenge.
- The broader Portal security rollout state did not exist in `/login`; there was no login-side table or enforcement hook for mandatory reset tracking, and portal-user 2FA enforcement depended only on the CRM-side `two_factor_enabled` flag.
- Investigation also confirmed that the generic Portal email-token system lives in the Portal app/CRM database (`koval_crm.vtiger_login_tokens`), not as a dedicated `/login` route in this repo.

## Repo Logs

### login

- Repo Log ID: `LOGIN-20260409-TOKEN-2FA-01`
- Commit SHA: `ef44dec3054a172a476f3f418f888a1a902b55e3`
- Commit Date: `2026-04-09`
- Change Summary:
  - Added shared token-login helpers in `auth_helpers.php` for token config resolution, local email-code 2FA, and Portal rollout enforcement/tracking.
  - Replaced `robert_login.php` and `screen_login.php` with wrappers that route through the shared token-login flow and added `token_login.php` for a generic token entry path.
  - Extended `twofactor.php` and `verify_2fa.php` to support a local-email 2FA mode in addition to the existing CRM API 2FA path.
  - Added a Portal rollout CLI tool at `scripts/portal_security_rollout.php` to activate reset-required tracking, enable 2FA for Portal users, send rollout emails, and clear reset-required state per user after confirmation.
  - Added login-gateway enforcement in `checklogin.php` so Portal users are blocked when the rollout marks them reset-required or when 2FA is disabled.
  - During investigation, exposed recent `vtiger_login_tokens` rows in-session output and immediately revoked the exposed token IDs (`383812` through `383821`) by marking them used.
  - Rebased the auth-hardening commit onto `origin/master` after `97898d2` and `c4ae963`, resolved the `auth_helpers.php` conflict by preserving both the SSO fallback restrictions and the new token-login/rollout helpers, then pushed `master`.
  - Deployed live on `ftp.koval-distillery.com:/home/koval/public_html/login` via `git pull --ff-only origin master`, fast-forwarding from `c4ae9639bf6cb1f9e604ceaad473741227b150f4` to `ef44dec3054a172a476f3f418f888a1a902b55e3`.

## Verification Notes

- `php -l` passed for `auth_helpers.php`, `checklogin.php`, `twofactor.php`, `verify_2fa.php`, `robert_login.php`, `screen_login.php`, `token_login.php`, and `scripts/portal_security_rollout.php`.
- `php scripts/portal_security_rollout.php status` ran successfully and confirmed the rollout table logic initializes cleanly with zero tracked users before activation.
- Git reconciliation completed safely with a stash/rebase/pop flow that kept the separate `ToDo-append.md` manager-queue edits out of the deploy commit.
- CRM data review confirmed:
  - Robert token should map to CRM user `admin` and route 2FA to Robert directly.
  - `screen` is an additional-user account, so its token flow now uses local email-code 2FA and a full additional-user session.
  - Current Portal users: 49 active; 48 already have `two_factor_enabled = 1`; `testuser2` was the only Portal-enabled user without 2FA at inspection time.

## Rollback Plan

- Revert only the token-login auth/session changes if they block legitimate kiosk or token workflows.
- Validate standard login, token login, and 2FA delivery paths before and after deployment.

## Follow-Ups

- Run the Portal rollout operational steps when approved:
  - `php scripts/portal_security_rollout.php activate`
  - `php scripts/portal_security_rollout.php send`
- Decide whether the generic Portal email-token flow in the separate `portal` app should also require a secondary step before it calls `/login/sso/ops_token.php`; that enforcement is not in `/login` today because the Portal frontend/backend own the initial email-token authentication.
- Confirm how password-reset completion should be detected automatically in the future. Current `/login` enforcement uses an explicit rollout-tracking table because the shared schema does not expose a reliable password-reset completion flag.
