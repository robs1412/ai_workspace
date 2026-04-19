# Logout Reliability Regression (Portal/OPS/Login SSO)

- Master Incident ID: `AI-INC-20260226-LOGOUT-02`
- Date Opened: `2026-02-26`
- Owner: `Codex`
- Priority: `P1`
- Status: `Policy approved; implementation gated`

## Scope

- Resolve persistent re-login/logout failure reported after prior shared-machine logout fix.
- Harden explicit logout so a sign-out from Portal/OPS clears all related SSO artifacts in `/login`.

## Approved Policy

- 2026-04-17 Robert approved the default OPS/Portal persistence policy for the next Security Guard-reviewed implementation slice.
- Explicit logout revokes Login/OPS/Portal artifacts globally.
- Next-day Portal/OPS access requires a fresh Login handoff/user action unless longer app persistence is explicitly approved.
- This approval does not authorize auth/session code changes, production session mutation, deploy, live pull, live credentialed login tests, credential/token/keychain access, or production data/session writes without the normal Security Guard and implementation gates.

## Reported Symptoms

- Users remain effectively signed in (or are silently re-authenticated) after logout attempts.
- Behavior appears tied to `/ops` + `/login` SSO/session interactions.

## Root Cause (Current Findings)

- `ops_sso_revoke_current_session()` only revoked `crm`/`ops` cookies and deleted token rows by current `session_id`.
- Portal handoff/session shapes (`portal:<session_id>` and cookie-referenced one-time tokens) could remain.
- Remember-device token was only cookie-cleared on logout; server-side token row was not explicitly revoked, allowing recovery if cookie persisted.

## Changes In Progress

### LOGIN

- Expanded SSO revocation on logout:
  - delete token rows for `session_id` and `portal:<session_id>`
  - delete token rows matching currently-present SSO cookie hashes
  - clear SSO cookies for `crm`, `ops`, and `portal`
- Added remember-token server-side revoke from current cookie token before cookie clear.
- Hardened remember-cookie clearing by deleting both configured-domain and host-only variants.
- Added portal SSO pause-cookie set on explicit `/login/logout.php?confirm=1` to prevent immediate silent portal re-entry.

## Verification Plan

1. Logout from Portal header dropdown (`global` logout path).
2. Confirm redirect to portal login and no silent re-entry.
3. Visit `/ops/start.php` in same browser and confirm redirect to `/login`.
4. Repeat with hard refresh and incognito.
