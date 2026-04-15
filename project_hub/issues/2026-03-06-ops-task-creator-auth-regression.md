- Master Incident ID: `AI-INC-20260306-OPS-TASK-CREATOR-01`
- Date Opened: `2026-03-06`
- Date Completed:
- Owner: `Codex`
- Priority: `High`
- Status: `In Progress`

## Scope

Investigate OPS CRM task creation failures after fallback hardening, where task writes should no longer fall back to `Default System` and instead preserve the authenticated CRM creator identity.

## Symptoms

- User reports task creation failure despite an active session showing roughly `29d 23h 59min` remaining.
- Error seen in OPS UI:
  - `CRM login failed: Login details provided does not exist or access denied.`
- Prior regression context:
  - task writes could silently fall back to the service-account path and create tasks under `Default System`.

## Root Cause

- `/tasks*` write fallback was still willing to trust `$_SESSION['myusername']` as the impersonation username.
- In some authenticated sessions, especially alias/additional-user style flows, `myusername` can be a valid portal/login identity but not a valid CRM `vtiger_users.user_name`.
- That caused service-account impersonated CRM login attempts like `service_user:bad_alias`, which fail with:
  - `Login details provided does not exist or access denied.`
- Upstream commit `f3c7787` prevented silent downgrade to non-impersonated service-account task creates, but the username resolver still needed to reject non-CRM aliases and prefer canonical CRM usernames derived from valid session user-id fields.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-03-06-TASK-CREATOR-AUTH`
- Commit SHA: `d18ffc1` + local uncommitted patch in `crm_integration.php`
- Commit Date: `2026-03-06`
- Change Summary:
  - Pulled latest `main`, which includes:
  - `f3c7787` `Fix task creator identity fallback for CRM task writes`
  - prior creator-fallback hardening in `6d2b4ff`
  - added local follow-up hardening in `crm_integration.php` so task-write impersonation usernames are validated against CRM first, then resolved from canonical CRM user-id fields (`user_id`, `userid`, `authenticated_user_id`) before any `/tasks*` write fallback.

## Verification Notes

- Read workspace handoff before resuming work.
- Confirmed latest OPS code contains targeted fix for task-write impersonation fallback.
- `php -l /Applications/MAMP/htdocs/ops/crm_integration.php` passed.
- Direct resolver verification:
  - invalid session alias + valid `userid=1` resolves to canonical CRM username `admin`
  - invalid session alias + invalid user-id resolves to `null` instead of attempting a bad CRM impersonation login
- Browser repro is still desirable, but the specific username-resolution failure mode is now covered locally.

## Rollback Plan

- Revert the specific OPS auth/task-write hardening commit if it causes broader CRM write regressions.
- As a temporary mitigation, disable only the strict task-write impersonation guard and keep creator enforcement logging in place.

## Follow-Ups

- Reproduce in Chromium against `http://localhost/ops` with an affected user/session if available.
- If any task-create failures remain, add precise logging around impersonation source selection without logging secrets.
