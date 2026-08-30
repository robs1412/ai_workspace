# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260830-RECURRING-TASK-COMPLETION-GUARD-01`
- Date Opened: 2026-08-30
- Date Completed: 2026-08-30
- Owner: Robert
- Priority: High
- Status: Pushed; not deployed

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
- Commit SHA: `d62f15d7`
- Commit Date: 2026-08-30
- Change Summary: Replaces the recurring task-detail Status dropdown with read-only status and enforces the no-completion rule in create, update, and bulk-complete API paths.

## Verification Notes

- Live read-only DB audit: 262 non-deleted tasks have `Completed` status with an active recurrence: Monthly 90, Weekly 73, Yearly 66, Quarterly 15, Daily 13, Biweekly 4, and `bi-weekly` 1.
- Of those rows, 19 were modified in 2026; 3 have due dates on or after 2026-08-30. No rows were changed.
- Portal `data_history` confirms 503 Status-to-Completed history entries across 168 currently affected tasks, including 22 entries across 10 tasks in August 2026.
- OPS PHP lint passed for every edited PHP file, and all seven `workflow_task_*` tests passed.
- Portal controller/policy PHP lint passed; direct policy assertions passed; the edited Vue component passed targeted ESLint.
- Full frontend lint remains red on unrelated pre-existing repository errors. Production build reached compilation but is blocked by the existing Node Sass 4.14 unsupported runtime 141 mismatch.
- Authenticated browser QA was not available because no Playwright/Selenium driver is installed and the local pages redirect to login. No security controls or 2FA were changed.

## Rollback Plan

Revert OPS commit `3e85d76` and Portal commit `d62f15d7`, then redeploy through each repository's normal release path. No schema or data rollback is required.

## Follow-Ups

- Decide separately whether and how to repair the 262 existing completed recurring rows. Do not bulk reopen them without source/owner review.
- Deploy Portal and pull OPS live only with the normal production approval and readback steps.
- The OPS-required Google Drive project-hub path was not mounted on this machine; this repo-backed project-hub entry is the available fallback record.
