# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260415-LOGIN-PORTAL-SECURITY-ROLLOUT-01`
- Date Opened: 2026-04-15
- Date Completed:
- Owner: Robert / Codex
- Priority: High
- Status: Open

## Scope

Activate the Login-side Portal security rollout for active Portal users using the existing `login` rollout tooling.

## Symptoms

The Login TODO still had the Portal-wide security rollout in progress after implementation because operational activation and user notification had not been run.

## Root Cause

Implementation and operational rollout were intentionally split. The remaining work required explicit approval because it enables Portal-user 2FA and sends staff-visible password-reset/2FA notification emails.

## Repo Logs

### login

- Repo Log ID: `LOGIN-PORTAL-SECURITY-ROLLOUT-20260415`
- Commit SHA: `d2681f4`
- Commit Date: 2026-04-15
- Change Summary: TODO/status documentation only. Runtime rollout executed with `php scripts/portal_security_rollout.php activate` and `php scripts/portal_security_rollout.php send`.

- Repo Log ID: `LOGIN-PORTAL-SECURITY-RESET-SELF-SERVICE-20260415`
- Commit SHA: `73ebb45`
- Commit Date: 2026-04-15
- Change Summary: Added `/login/reset_password.php` as a forced post-auth password update screen. After normal password auth and 2FA, Login redirects reset-required users to choose a new password, updates both legacy and modern CRM password hashes, and clears only the successful user's rollout reset flag. Direct visits to the reset page still require the current password.

### portal

- Repo Log ID: `PORTAL-DIRECT-LOGIN-ROLLOUT-GATE-20260415`
- Commit SHA: `3fc35b6f`
- Commit Date: 2026-04-15
- Change Summary: Direct SPA login now lets users complete password auth and 2FA, then returns a short-lived password-reset token and shows an in-Portal new-password form instead of issuing the normal app JWT while `reset_required=1`.

### ai_workspace

- Repo Log ID: `AI-PORTAL-SECURITY-ROLLOUT-20260415`
- Commit SHA: `8a24178`
- Commit Date: 2026-04-15
- Change Summary: Added this project-hub record and index entry.

### ops

- Repo Log ID: `OPS-PORTAL-PASSWORD-ROLLOUT-REMINDER-20260415`
- Commit SHA: `88000e2`
- Commit Date: 2026-04-15
- Change Summary: Recorded silent OPS reminder task `366807`, due 2026-08-15, for the four-month Portal password-change rollout recommendation.

- Repo Log ID: `OPS-PORTAL-ROLLOUT-FLAG-RECHECK-20260415`
- Commit SHA: `0d88931`
- Commit Date: 2026-04-15
- Change Summary: Recorded silent OPS follow-up task `366809`, due 2026-04-29, to re-check reset flags after 14 days and re-task only users still open.

## Verification Notes

- 2026-04-15 18:25 CDT: Robert approved rollout with "roll out".
- Security Guard session `19370e50` was given a non-secret guardrail note before execution.
- `activate` result: 47 Portal users tracked, 47 reset-required rows, 1 two-factor enablement update.
- `send` result: 47 notification emails sent, 0 failures.
- Final status after send: 47 tracked, 47 reset required, 47 emailed.
- Robert reported he did not receive the rollout email. Created OPS/Portal task `366808` (`Reset Portal password and complete 2FA`), due 2026-04-15, creator `1`, owner `1332`, assigned to 47 active Portal users, with `sendnotification=1`; verified directly from CRM/OPS task tables.
- Robert reported direct Portal login at `https://portal.koval-distillery.com/#/home` could still bypass the Login-side reset gate. Patched Portal direct auth to enforce the same reset flag after password auth and 2FA, before normal app JWT issuance.
- Added Login forced password update page; local HTTP smoke test returned 200 for `/reset_password.php?username=test`.
- Portal frontend lint was attempted but could not run locally because `vue-cli-service` is not installed in `frontend/node_modules`.
- No credentials, tokens, `.env` values, or private key material were printed.
- No `complete <username>` reset-clear actions were run.
- Created silent OPS reminder task `366807`, due 2026-08-15, creator `1`, owner/assignee `1332`, to recommend another Portal password-change rollout email after four months.
- Created silent OPS follow-up task `366809`, due 2026-04-29, creator `1`, owner/assignee `1332`, to re-check reset flags after 14 days and task only users still open.

## Rollback Plan

- Do not bulk-clear reset requirements without confirmed resets.
- If Robert decides the rollout must be paused, use the Login rollout table to identify affected users and choose a targeted policy rollback before changing 2FA or reset-required state.
- Any rollback that disables 2FA or clears reset requirements is a separate security-sensitive approval gate.

## Follow-Ups

- Confirm user password resets through the approved operational process.
- Use OPS/Portal task `366808` as the operational reminder path for the current rollout.
- Use OPS task `366809` on 2026-04-29 to identify users still `reset_required=1` and issue follow-up Portal tasks only to that open set.
- Run `php scripts/portal_security_rollout.php complete <username>` only for users whose reset is confirmed.
- Re-run `php scripts/portal_security_rollout.php status` to track remaining reset-required count.
- On 2026-08-15, review OPS task `366807` and ask Robert for approval before any follow-up password-change rollout email or auth-setting change.
