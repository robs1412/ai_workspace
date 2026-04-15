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

## Verification Notes

- 2026-04-15 18:25 CDT: Robert approved rollout with "roll out".
- Security Guard session `19370e50` was given a non-secret guardrail note before execution.
- `activate` result: 47 Portal users tracked, 47 reset-required rows, 1 two-factor enablement update.
- `send` result: 47 notification emails sent, 0 failures.
- Final status after send: 47 tracked, 47 reset required, 47 emailed.
- Robert reported he did not receive the rollout email. Created OPS/Portal task `366808` (`Reset Portal password and complete 2FA`), due 2026-04-15, creator `1`, owner `1332`, assigned to 47 active Portal users, with `sendnotification=1`; verified directly from CRM/OPS task tables.
- No credentials, tokens, `.env` values, or private key material were printed.
- No `complete <username>` reset-clear actions were run.
- Created silent OPS reminder task `366807`, due 2026-08-15, creator `1`, owner/assignee `1332`, to recommend another Portal password-change rollout email after four months.

## Rollback Plan

- Do not bulk-clear reset requirements without confirmed resets.
- If Robert decides the rollout must be paused, use the Login rollout table to identify affected users and choose a targeted policy rollback before changing 2FA or reset-required state.
- Any rollback that disables 2FA or clears reset requirements is a separate security-sensitive approval gate.

## Follow-Ups

- Confirm user password resets through the approved operational process.
- Use OPS/Portal task `366808` as the operational reminder path for the current rollout.
- Run `php scripts/portal_security_rollout.php complete <username>` only for users whose reset is confirmed.
- Re-run `php scripts/portal_security_rollout.php status` to track remaining reset-required count.
- On 2026-08-15, review OPS task `366807` and ask Robert for approval before any follow-up password-change rollout email or auth-setting change.
