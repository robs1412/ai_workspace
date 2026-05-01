# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260430-OPS-PROJECT-TASK-AUTOSAVE-01`
- Date Opened: `2026-04-30`
- Date Completed: `2026-04-30`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Fix the live OPS project task-detail page autosave failure for top editable task fields.

## Symptoms

Robert reported that `/ops/projects/task.php?id=367074` showed:

`Unable to save task fields. Please reload the page and sign in again if needed.`

This appeared after re-login, so the immediate evidence pointed to the save request returning non-JSON instead of the normal OPS AJAX payload.

## Root Cause

The new project task-detail autosave initially depended on the shared `/ops/action_handler.php` JSON path. That path could return HTML to this page, causing the browser-side JSON parser to fail and show the generic save error. The first mitigation changed the request from `FormData` multipart to URL-encoded AJAX; the second fix moved this header-editor save onto the task-detail page itself.

Robert's browser still failed after that because the JavaScript used `fetch(form.action)`. The hidden input named `action` shadowed the form's `action` URL property in Chrome, so the browser posted to `/ops/projects/[object HTMLInputElement]` and received a 404 HTML page. The final live fix reads the action URL from `form.getAttribute('action')` before calling `fetch`.

## Repo Logs

### ops

- Repo Log ID: `OPS-20260430-PROJECT-TASK-AUTOSAVE`
- Commit SHAs: `b89896c`, `b0f5caa`
- Commit Date: `2026-04-30`
- Change Summary:
  - Added a same-page `POST action=update_task_metadata` JSON handler to `projects/task.php`.
  - The handler validates task name, status, priority, dates, recurring type, account link, and selected assignees.
  - It updates task metadata, account relation, and `activity2user` assignees directly, with notifications disabled.
  - Changed the metadata form action to post back to the current task-detail URL instead of `/ops/action_handler.php`.
  - Preserved the URL-encoded AJAX request body and same-origin credentials.
  - Fixed the browser save URL so the hidden `action` input cannot shadow the form action URL.

## Verification Notes

- Local `php -l /Users/werkstatt/ops/projects/task.php` passed.
- Pushed `b89896c` to `origin/main`.
- Live `/home/koval/public_html/ops` fast-forwarded to `b0f5caa`.
- Live `php -l projects/task.php` passed.
- Live source grep confirms the same-page `update_task_metadata` handler is present, the metadata form posts to the current task-detail URL, and the JavaScript uses `saveUrl` from the form attribute.
- Apache access logs showed the failing browser POSTs as `/ops/projects/[object%20HTMLInputElement]`.
- Codex-authenticated server-side save tests returned `{"success":true,"message":"Task fields updated."}` for task `367074` after deployment.

## Rollback Plan

On live, revert only this commit if needed:

`cd /home/koval/public_html/ops && git revert b0f5caa b89896c`

## Follow-Ups

- Robert should reload the task-detail page before retesting so the browser uses the fixed inline JavaScript.
