# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260830-RECURRING-TASK-COMPLETION-GUARD-01`
- Date Opened: 2026-08-30
- Date Completed: 2026-08-30
- Owner: Robert
- Priority: High
- Status: Completed and live

## Scope

Prevent recurring CRM tasks from being left in `Completed` status through OPS or Portal task controls, while preserving the OPS action that advances a recurring task to its next date. Audit existing non-deleted completed recurring rows without changing them.

## Symptoms

Portal task detail hid the dedicated Complete button for recurring tasks but still exposed `Completed` in the Status dropdown. The Portal update and bulk-complete endpoints accepted the transition. OPS also exposed direct status-edit and silent bulk-complete routes.

## Root Cause

Recurring-task completion was treated as a frontend-only convention in part of Portal. The shared Portal API and several OPS write paths did not enforce the invariant that an active recurrence cannot end in `Completed` status.

## Repo Logs

### ops

- Repo Log ID: `OPS-RECURRING-COMPLETION-GUARD-20260830`
- Commit SHA: `3e85d76`
- Commit Date: 2026-08-30
- Change Summary: Makes recurring status read-only in OPS task detail/list views; blocks direct and silent bulk completion; preserves date advancement and fails safely when the next recurrence cannot be calculated.

### portal

- Repo Log ID: `PORTAL-RECURRING-COMPLETION-GUARD-20260830`
- Commit SHAs: `d62f15d7`, `62de5120`, `cfee7053`
- Commit Date: 2026-08-30
- Change Summary: Replaces the recurring task-detail Status dropdown with read-only status and enforces the no-completion rule in create, update, and bulk-complete API paths. Portal task/project and shared router-mode View/Edit actions are true router links: normal clicks stay in the same window, while browser new-tab choices work.

## Production Deployment

- OPS live checkout: `main` at `3e85d76`; live PHP lint and the recurring completion policy test passed.
- Portal production image tag: `v20260830recurringlinks`.
- Portal live containers: backend and frontend both use `v20260830recurringlinks`; backend nginx remained healthy.
- Independent live readback: Portal frontend and backend returned HTTP 200; live controller/policy PHP lint passed; the controller contains two completion-policy enforcement references; compiled frontend assets contain recurring-status references.

## Verification Notes

- Live read-only DB audit: 262 non-deleted tasks have `Completed` status with an active recurrence: Monthly 90, Weekly 73, Yearly 66, Quarterly 15, Daily 13, Biweekly 4, and `bi-weekly` 1.
- Of those rows, 19 were modified in 2026; 3 have due dates on or after 2026-08-30. No rows were changed.
- Portal `data_history` confirms 503 Status-to-Completed history entries across 168 currently affected tasks, including 22 entries across 10 tasks in August 2026.
- OPS PHP lint passed for every edited PHP file, and all seven `workflow_task_*` tests passed.
- Portal controller/policy PHP lint passed; direct policy assertions passed; the edited Vue component passed targeted ESLint.
- Full frontend lint remains red on unrelated pre-existing repository errors. Targeted ESLint passed for all changed action/task components, and the production Docker build completed successfully with the repository's existing warnings.
- Authenticated browser QA was not available because no Playwright/Selenium driver is installed and the local pages redirect to login. No security controls or 2FA were changed.

## Audit Publication and Send

- AI Cloud document: `https://docs.google.com/document/d/1bgA3L3m8xqbpDYero_GcgKUYJNWxVPYcVMr590gZKvk/edit?usp=drivesdk`.
- Google Docs readback confirmed the 262-row summary and exact priority task IDs `334189` and `360626` in AI Cloud `IT`.
- phpList exact audience list: `192` (`Recurring task audit recipients 2026-08-30`), containing only subscriber IDs `381`, `8174`, and `31812` (Robert, Mark, and Dmytro); all three were confirmed, enabled, and unblacklisted before send.
- phpList campaign: `664` (`Recurring task audit and completion safeguard now live`), status `sent`, processed `3`, with 3 distinct `phplist_usermessage` rows in `sent` status. No other submitted campaign remained after processing.

## Rollback Plan

Revert OPS commit `3e85d76` and Portal commits through `cfee7053`, then redeploy through each repository's normal release path. No schema or data rollback is required.

## Follow-Ups

- Decide separately whether and how to repair the 262 existing completed recurring rows. Do not bulk reopen them without source/owner review.
- Review the three future-due rows first and decide whether to advance, end, or retire each recurrence.
