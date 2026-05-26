# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260518-OPS-LOGIN-TRUSTED-DEVICE-IP-01`
- Date Opened: `2026-05-18`
- Date Completed: `2026-05-18`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Mirror the Portal trusted-device fingerprint fix into the OPS login path by removing IP from trusted-device acceptance logic while keeping IP stored on the remember-token row for audit/readback.

Linked OPS task: `369822` (`Mirror trusted-device fingerprint IP fix into OPS login path`)

## Symptoms

- Portal fixed a bug where the device identity hash included client IP, which caused routine 5G NAT or ISP DHCP rotation to make known devices look new.
- OPS `config.php` only references `remember_try_silent_login()`, but the real trusted-device implementation lives in the `/login` repo.
- The OPS login path needed the equivalent stability fix in the actual owner code rather than a guess inside `ops/config.php`.

## Root Cause

The local OPS/login stack does not use the same Laravel `DeviceFingerprintService` shape as Portal. Instead, `/login/auth_helpers.php` stores a random trusted-device token and then applies soft acceptance checks against `ua_hash` and `ip_prefix` during `remember_try_silent_login()`. That meant IP still affected whether a known trusted device was accepted, even though it was not part of the token hash itself.

## Repo Logs

### login

- Repo Log ID: `AI-INC-20260518-OPS-LOGIN-TRUSTED-DEVICE-IP-01`
- Commit SHA: `9956992`
- Commit Date: `2026-05-18`
- Change Summary:
  - Updated `auth_helpers.php` so trusted-device acceptance now keys only off `ua_hash`.
  - Kept `ip_prefix` storage and rotation updates for audit/readback only.
  - Simplified context-miss logging into one `remember_miss_context` event with the active mode recorded.
  - Pushed `master` to GitHub and live `/home/koval/public_html/login` fast-forwarded from `8c338d8` to `9956992`.

### ops

- Repo Log ID: `AI-INC-20260518-OPS-LOGIN-TRUSTED-DEVICE-IP-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-05-18`
- Change Summary:
  - Verified OPS is only the caller: `config.php` references `remember_try_silent_login()` but does not own the trusted-device implementation.
  - Created linked OPS task `369822` through the normal session-backed CRM/Portal route with creator/owner/assignee all `1332` and notifications suppressed.
  - Marked OPS task `369822` `Completed` after the live login rollout was verified.

## Verification Notes

- `ops/config.php:430` calls `remember_try_silent_login()` only when the function is defined.
- `login/auth_helpers.php` is the real owner file for the trusted-device flow.
- `php -l /Users/werkstatt/login/auth_helpers.php`
- Live `git log --oneline -n 1` on `/home/koval/public_html/login` returns `9956992 fix(auth): ignore IP in remember-device acceptance`.
- Live `php -l /home/koval/public_html/login/auth_helpers.php`
- Linked OPS task `369822` verified live with creator/owner/assignee all `1332`.
- Linked OPS task `369822` now verifies `Completed` in CRM DB state.
- Behavior change:
  - `ip_prefix` is still written into `koval_additionaluser.remember_tokens`
  - `ip_prefix` is still refreshed on token rotation
  - `ip_prefix` no longer participates in trusted-device accept/reject decisions

## Rollback Plan

- Revert the `remember_try_silent_login()` acceptance change in `login/auth_helpers.php`.
- Keep the linked OPS task `369822` open if rollout or deployment follow-through is still pending.

## Follow-Ups

- If Robert wants exact parity with the Portal commit trail, compare live behavior after deployment against Portal commit `43e16b67`.
