# Logout Reliability / Shared Machine

- Master Incident ID: `AI-INC-20260226-LOGOUT-01`
- Date Opened: `2026-02-26`
- Date Completed: `2026-02-26`
- Owner: `Codex`
- Priority: `P1`
- Status: `Completed`

## Scope

- Fix logout failures/regressions across:
  - `ops`
  - `login`
  - `portal`
- Ensure explicit sign-out paths work again.
- Improve shared-machine behavior by ensuring portal logout also clears shared `/login` auth session.

## Reported Symptoms

- Users could not reliably log out from OPS/login-linked surfaces.
- Portal users appeared unable to fully log out on shared machines.
- Issue was not a permission-denied state.

## Root Cause

- `login/logout.php` requires explicit logout confirmation (`POST` or `?confirm=1`).
- Legacy/linked logout URLs still pointed to plain `GET /login/logout.php`, which no longer completed logout directly.
- Portal frontend logout only cleared frontend token storage and did not trigger shared `/login` session logout.

## Repo Logs

### OPS

- Repo Log ID: `OPS-LOGOUT-20260226-01`
- Commit SHA: `fdb76e2`
- Commit Date: `2026-02-26T09:33:32-06:00`
- Change Summary:
  - Updated OPS header logout link to explicit confirmation URL: `/login/logout.php?confirm=1`.

### LOGIN

- Repo Log ID: `LOGIN-LOGOUT-20260226-01`
- Commit SHA: `c782986`
- Commit Date: `2026-02-26T09:33:35-06:00`
- Change Summary:
  - Added safe `return` handling in `logout.php` for allowed internal KOVAL URLs.
  - Preserved explicit-confirm behavior while enabling redirect back to caller after successful logout.
  - Updated forced logout meta-refresh links (`access_*`) to include `?confirm=1`.

### PORTAL

- Repo Log ID: `PORTAL-LOGOUT-20260226-01`
- Commit SHA: `a1b295e3`
- Commit Date: `2026-02-26T09:33:39-06:00`
- Change Summary:
  - Updated portal dropdown logout to perform global `/login` logout with:
    - `confirm=1`
    - `return=<portal login hash URL>`
  - Updated legacy reporting logout link to explicit confirm URL.

## Verification Notes

- PHP lint checks passed for edited `login` PHP files.
- Diff review confirms all targeted logout links now use explicit logout URL.
- Portal logout flow now clears local token and then navigates to shared global logout endpoint.

## Rollback Plan

- Revert repo commits:
  - `ops`: `fdb76e2`
  - `login`: `c782986`
  - `portal`: `a1b295e3`
- Validate old behavior in staging before production rollback.

## PM Follow-Ups

- Add a standing smoke-test checklist for auth/logout after any session/cookie changes.
- Keep a single canonical logout helper URL and consume it from all apps.
- Add weekly review in this hub for auth/session incidents and preventive tasks.
