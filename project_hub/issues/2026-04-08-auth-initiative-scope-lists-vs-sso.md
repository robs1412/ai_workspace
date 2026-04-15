# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260408-AUTH-SCOPE-01`
- Date Opened: `2026-04-08 13:31:44 CDT`
- Date Completed: `2026-04-08 15:17:42 CDT`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`
- Last Updated: `2026-04-08 15:17:42 CDT (Machine: RobertMBP-2.local)`

## Scope

Compare the isolated `/lists/admin` logout/session-loss problem against the broader cross-module session and SSO standardization initiative, decide which should be tackled first, and define the first low-risk investigation steps without changing live auth behavior yet.

## Symptoms

- `TODO.md` still lists `Still getting logged out in /lists/admin`.
- `TODO.md` also lists the larger ecosystem session initiative:
  - unify on `PHPSESSID`
  - remove `KOVALSESSID` alias complexity
  - audit `login/auth_helpers.php`
  - audit `lists/admin/init.php`
  - remove redundant `lists/config/config.php` sync logic
  - verify `Portal -> Lists -> Forge -> OPS` persistence
- Existing login auth diagnostics captured repeated `/lists/admin/?page=pageaction&ajaxed=true&action=keepalive` requests that arrived with a session cookie but no authenticated `/login` session payload.

## Root Cause

Current evidence suggests the `/lists/admin` issue should be treated first as a bounded investigation, not as a trigger for immediate ecosystem-wide auth refactoring.

- `lists/admin/init.php` imports `/login/auth_helpers.php` and calls `ensureSessionStarted()` before phpList continues bootstrapping. This means `/lists` is already downstream of the shared session layer, not independent of it.
- `lists/admin/plugins/KovalEcosystemAuthPlugin.php` forces a redirect back to `/login` whenever shared portal identity is missing, even if phpList had local admin session data. That makes `/lists` more sensitive than other modules to any transient identity gap.
- `login/auth_helpers.php` still contains compatibility behavior for:
  - canonical `PHPSESSID`
  - optional alias cookie from `LOGIN_SESSION_NAME` (historically `KOVALSESSID`)
  - alias-first session recovery
  - retry with incoming `PHPSESSID`
- `/Applications/MAMP/htdocs/login/.env` still sets `LOGIN_SESSION_COOKIE_DOMAIN=.koval-distillery.com`. The same file does not currently expose a `LOGIN_SESSION_NAME` override in the checked lines, but runtime diagnostics still show alias-cookie handling was active when the auth-flow logs were captured.
- The auth-flow log shows `/lists/admin` keepalive requests on `2026-02-23` reaching `ensureSessionStarted()` with cookie fingerprints present but `has_user_authenticated`, `has_myusername`, and `has_userid` all false. That is sufficient evidence to instrument `/lists` and the shared session recovery path first, without yet removing compatibility logic used by `ops`, `portal`, or `forge`.

## Repo Logs

### ai_workspace

- Repo Log ID: `AIWS-2026-04-08-AUTH-SCOPE-01`
- Commit SHA:
- Commit Date: `2026-04-08`
- Change Summary:
  - Added this scoping log and initiative ordering note.

### lists

- Repo Log ID: `LISTS-2026-04-08-AUTH-SCOPE-01`
- Commit SHA:
- Commit Date: `2026-04-08`
- Change Summary:
  - No code changes yet.
  - Relevant current touchpoints identified:
    - `lists/admin/init.php`
    - `lists/admin/plugins/KovalEcosystemAuthPlugin.php`
    - `lists/admin/logout.php`

### login

- Repo Log ID: `LOGIN-2026-04-08-AUTH-SCOPE-01`
- Commit SHA: `6bc921b`, `2f47415`, pushed live at `c4ae963`
- Commit Date: `2026-04-08`
- Change Summary:
  - Hardened shared SSO handoff helpers and claims-based OPS identity recovery.
  - Restricted legacy additional-user fallback to explicit exceptions so active vtiger users cannot silently downgrade into OPS-only auth.
  - Standardized JWT extraction across shared login and 2FA paths.
  - Relevant shared auth/session touchpoints updated:
    - `login/auth_helpers.php`
    - `login/checklogin.php`
    - `login/sso/ops_token.php`
    - `login/sso_helpers.php`
    - `login/twofactor.php`
    - `login/verify_2fa.php`

### ops

- Repo Log ID: `OPS-2026-04-08-AUTH-SCOPE-01`
- Commit SHA: `a961070`, pushed live at `1486bc6`
- Commit Date: `2026-04-08`
- Change Summary:
  - Added non-secret auth diagnostics around credential-state failures.
  - Hardened OPS task detail loading by using CRM fallback reads and local task metadata fallback for `task_info`.

## Verification Notes

- Reviewed current TODO state in `ai_workspace/TODO.md`.
- Confirmed previous related auth work remains open in:
  - `project_hub/issues/2026-02-26-logout-reliability-regression.md`
  - `project_hub/issues/2026-03-12-ops-portal-session-rehydration.md`
- Localhost repro on `2026-04-08`:
  - login through `/login/checklogin.php` succeeded with the local OPS-backed credentials
  - `http://localhost/ops/start.php` returned `200`
  - `http://localhost/lists/admin/` returned `200`
  - `http://localhost/lists/admin/?page=pageaction&ajaxed=true&action=keepalive` returned `200` repeatedly under the same authenticated jar
- Localhost repro therefore did **not** reproduce the current failure report directly.
- During localhost repro, `lists` and keepalive continued to use a stable `PHPSESSID`, so the old production symptom from `2026-02-23` is not presently occurring in this local path.
- Key code references:
  - `lists/admin/init.php` starts the shared `/login` session bootstrap.
  - `lists/admin/plugins/KovalEcosystemAuthPlugin.php` redirects to `/login` when portal identity is absent.
  - `login/auth_helpers.php` still carries alias-cookie and session-recovery compatibility logic.
  - `lists/admin/logout.php` intentionally sends users to `/login/index.php` for re-auth, while explicit global sign-out is handled through `/login/logout.php`.
- New low-risk diagnostics added on `2026-04-08`:
  - `lists/admin/plugins/KovalEcosystemAuthPlugin.php` now logs auth-state snapshots for redirect/profile-miss cases to `lists/admin/logs/auth_debug.log`
  - `ops/config.php` now exposes a non-secret credential-state snapshot helper
  - `ops/bootstrap.php`, `ops/ajax.php`, and `ops/action_handler.php` now log credential-state context whenever they emit a `credentials are not configured` error
- OPS task-path repro on `2026-04-08`:
  - local signed-in session loaded `ajax.php?action=workflow_tasks_list` successfully
  - the same session failed on `ajax.php?action=task_info&id=365940` with `CRM login failed: Login details provided does not exit.`
  - this isolates the current OPS-task regression to the task-detail read path rather than the base signed-in task list
  - `ops/ajax.php` was updated so `task_info` first uses the shared CRM fallback helper and then degrades to local CRM DB task metadata when the portal/API read fails
  - localhost verification after the change returned `success: true` for `task_info` with `source: local_fallback`
- SSO investigation findings on `2026-04-08`:
  - `login/auth_helpers.php` still canonicalizes on `PHPSESSID` but also performs alias-cookie recovery with `LOGIN_SESSION_NAME`, so session identity is intentionally dual-path today
  - `login/sso/crm_token.php` already expects the CRM one-time handoff cookie to be missing frequently and falls back first to the live `/login` session JWT and then to a recent `ops_sso_tokens` row
  - `login/logs/sso_crm_token.log` shows repeated `token_cookie_miss` events for `ops_sso_crm`, confirming the CRM SSO cookie is often absent when consumers request it
  - `login/logs/sso_ops_token.log` shows repeated `/user/profile` responses with status `404`, after which `login/sso/ops_token.php` succeeds only by decoding JWT claims and doing a fallback user lookup
  - taken together, the current SSO design behaves as a layered recovery chain rather than a clean single handoff, which explains intermittent cross-module behavior
- Shared SSO fixes implemented on `2026-04-08`:
  - `login/sso_helpers.php` now mirrors newly-issued SSO cookies into `$_COOKIE` in-request so immediately-following logic can observe the same token value
  - `login/sso_helpers.php` now tolerates CRM-token session-id mismatch when the authenticated user still matches the token user, reducing false negatives after same-user session rotation
  - `login/sso/ops_token.php` now resolves identity from JWT claims first and only falls back to the brittle `/user/profile` path when claims are insufficient
- Verification after the shared-layer changes:
  - `php -l` passed on `login/sso_helpers.php` and `login/sso/ops_token.php`
  - localhost login + `http://localhost/ops/start.php` still returned `200`
  - localhost `http://localhost/login/sso/crm_token.php` still returned `204`, so the deeper CRM-token availability gap is not fully resolved by this pass
- Verification after the vtiger-vs-additional-user policy fix:
  - active `vtiger_users` are now forced through the real CRM/2FA path instead of silently falling back to additional-user auth
  - `screen` remains the only intended additional-user exception for `/automation`
  - the local fallback test account `testuser2` no longer degrades into OPS-only login when CRM auth is unavailable
  - a real local vtiger user was tested successfully on `2026-04-08`, including local OPS access and cross-module behavior
- Deploy completion on `2026-04-08`:
  - `ops` was pushed and live-pulled to `1486bc6`
  - `login` was pushed to `origin/master` and live-pulled to `c4ae963`
  - live `login` had a pre-existing local modification to `sso_helpers.php`; it was preserved non-destructively in `stash@{0}` with message `pre-pull-login-sso-2026-04-08` before the fast-forward pull

## Rollback Plan

Rollback is limited to reverting the targeted `ops/ajax.php` `task_info` fallback change, the shared SSO helper changes in `login/sso_helpers.php` and `login/sso/ops_token.php`, and the earlier non-secret diagnostics.

## Follow-Ups

1. If `/lists/admin` logout behavior reappears, use the existing `lists/admin/logs/auth_debug.log` and `login/logs/auth_flow.log` instrumentation first before reopening shared-session refactors.
2. Keep `screen` as the explicit additional-user-only exception unless `/automation` policy changes.
3. Any future ecosystem session cleanup should build on this completed vtiger-auth/SSO hardening baseline rather than reintroducing broad additional-user fallback.
