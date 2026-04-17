# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260417-OPS-DASHBOARD-TASK-CREATE-SESSION-CREDS-01`
- Date Opened: 2026-04-17
- Date Completed: 2026-04-17
- Owner: Codex / OPS
- Priority: High
- Status: Recurrence diagnosed; OPS fallback fix committed, pushed, and live-pulled

## Scope

Create a durable OPS issue/task for Robert's 2026-04-17 report that OPS dashboard task creation failed while he appeared logged in.

This slice registered the issue and then performed non-secret investigation of the dashboard task-create path, CRM/Portal credential detection, session-to-Portal-token hydration, and recurrence logs. It did not change credentials, mutate production session data, or create a test task. A local OPS code fix was prepared after recurrence diagnostics, then committed, pushed, and live-pulled after Robert approval.

## Symptoms

Robert reported that he logged in on the morning of 2026-04-17 and was in the OPS dashboard, but when creating a task he received:

`CRM API credentials are not configured.`

Affected surface: OPS dashboard / task creation.

Likely area: SSO/session handling or session-to-CRM identity hydration versus actual CRM API credential configuration.

Expected behavior: a logged-in OPS user with task-create permission can create a task without backend CRM credential/config errors.

Actual behavior: dashboard/task creation returns the CRM API credential configuration error.

## Root Cause

The exact live request state was not mutated or replayed during the first pass, so the original failure could not be proven from request state alone. Follow-up read-only live diagnostics after recurrence confirmed the failure shape: OPS had a valid local user identity, but no usable Portal JWT in the request session; SSO-table rehydration returned false; then the service credential fallback failed because live has `CRM_API_USERNAME` and `CRM_API_PASSWORD` empty. This surfaced the misleading credential error instead of the correct Portal re-login requirement.

Current local config discovery does not reproduce a missing `.env`/config condition: the CRM/Portal API base URL, username, and password constants are defined and non-empty without printing values.

Current session hydration also succeeds for Robert's CRM identity when the OPS session identity is present: CRM user id `1` resolves to username `admin`, active and not deleted; active SSO token metadata exists for `admin` for both `crm` and `ops`; and a simulated local OPS session with `myusername=admin` and `userid=1` can hydrate a non-expired Portal JWT matching that identity from the SSO table.

Follow-up note: live evidence shows Robert/admin reached `/ops/ajax.php?action=create_standalone_task` at `2026-04-17 15:37:08` and `2026-04-17 17:43:47` Central with `user=admin` and `userid=1`, but `had_token=false`, `session_token_rehydrate_attempt success=false`, then `write_fallback_service_token_failed` with `CRM API credentials are not configured.` A non-secret live config probe showed the API base URL defined/non-empty, but the service username/password booleans false. No secret values were printed.

## Repo Logs

### ops

- Repo Log ID: OPS task `367115`
- Commit SHA: `2d5fba6038b27f7a8093c891b3ca23cbedf33f1d`
- Commit Date: 2026-04-17
- Change Summary: Created silent Codex-owned OPS/Portal task `367115` (`Investigate OPS task creation SSO/session credential error`), due `2026-04-18`, priority `High`, creator `1`, owner/assignee `1332`, status `Not Started`, `sendnotification=0`; later recurrence diagnostics identified the live missing-service-credential fallback and `crm_integration.php` was updated to convert that fallback failure into the existing Portal auth-required response.

## Verification Notes

- Verified final OPS/Portal task metadata directly after creation:
  - task ID `367115`
  - creator `1`
  - owner `1332`
  - assignee `1332`
  - status `Not Started`
  - priority `High`
  - due date `2026-04-18`
  - `sendnotification=0`
  - `deleted=0`
- Initial helper attempt returned no task ID because the service fallback path hit the known mandatory password-reset gate. The successful create used a session-backed Codex identity and final metadata enforcement.
- No secrets were printed or requested.
- Dashboard task creation path reviewed: `start.php` add-task form posts to `ajax.php?action=create_standalone_task`; the AJAX action calls `crm_request_with_fallback('PUT', '/tasks', ...)`.
- Non-secret local config verification: `ops_crm_credentials_snapshot()` and `crm_credentials_configured()` both report the Portal API config constants as present/non-empty.
- Non-secret local session verification: `crm_hydrate_session_portal_token('admin')` succeeds in a simulated local OPS session for CRM user id `1`, with the resulting token present, non-expired, and identity-matching. Token values were not printed.
- Non-secret live config verification after recurrence: live `CRM_API_USERNAME` and `CRM_API_PASSWORD` are empty while `CRM_API_BASE_URL` is present; `crm_credentials_configured()` returns false.
- Local code verification after patch: `php -l crm_integration.php` passed, and a synthetic no-network write request with session identity but empty CRM service credentials now returns `Portal session expired. Please sign in again.` with auth-required state instead of `CRM API credentials are not configured.`
- Deployment verification after approval: OPS commit `2d5fba6038b27f7a8093c891b3ca23cbedf33f1d` was pushed to `origin/main` and live `/home/koval/public_html/ops` was fast-forwarded to that SHA with `git pull --ff-only origin main`; live `php -l crm_integration.php` passed and the new `write_fallback_service_credentials_unavailable_auth_required` branch is present.
- Not verified: a real dashboard task-create write, because that would create/mutate an OPS/Portal task. Final live confirmation should be Robert retesting or an explicitly approved controlled create test.

## Rollback Plan

If this task was created in error, close or cancel OPS/Portal task `367115` through the approved silent task-update path with notifications disabled. Do not delete task history unless Robert explicitly requests that cleanup.

## Follow-Ups

- Robert can retest dashboard task creation while logged into OPS.
- If a controlled verification write is needed, perform an explicitly approved real task-create test with notifications controlled, then close/update OPS task `367115` through the approved silent path.
- If the error recurs, capture only non-secret request diagnostics: session username/user id presence, whether `api_token` is present/expired, credential snapshot booleans, and the `crm_request_with_fallback` branch reached. Do not print token values, passwords, hashes, or session IDs.
