# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260414-COMMS-MANAGER-NEWSLETTER-ROUTING-01`
- Date Opened: 2026-04-14
- Date Completed: 2026-04-14
- Owner: Codex OPS worker
- Priority: Medium
- Status: Completed

## Scope

Coordinate Communications Manager task ownership and newsletter/list workflow routing without sending external emails or editing non-OPS repos from the OPS worker session.

Tasks in scope:
- Square task `363191`
- Shopify task `360626`
- Related Forge donations workflow task `363052`

## Symptoms

Initial read-only CRM verification on 2026-04-14 showed:
- `363191` (`Square list`) was still owner/assignee `1`.
- `360626` (`Send out a Shopify newsletter... group hasn't been targeted`) was still owner/assignee `1`.
- `363052` (`Forge task ... donations`) was assigned to Codex user `1332` but still owned by user `167`.

Follow-up repair on 2026-04-14 verified all three now have creator `1`, owner `1332`, and assignee `1332`.

## Root Cause

The normal Codex Portal hydration path still needs separate repair: a clean Codex session-context retry of `crm_hydrate_session_portal_token("Codex")` produced no usable Portal token. The immediate routing gap was resolved by restoring the explicit OPS helper fallback path and forcing the intended CRM metadata without printing secrets.

## Repo Logs

### ops

- Repo Log ID: `OPS-COMMS-MANAGER-NEWSLETTER-ROUTING-20260414`
- Commit SHA: `8964684`
- Commit Date: 2026-04-14
- Change Summary: Restored `scripts/create_codex_task.php`, added explicit `crm_create_task(..., ['allow_service_fallback' => true])` support, and updated OPS TODO with final task registration state.

### ai_workspace

- Repo Log ID: `AI-COMMS-MANAGER-NEWSLETTER-ROUTING-20260414`
- Commit SHA: not committed; documentation/status-only update pending
- Commit Date:
- Change Summary: Updated AI Workspace TODO and added this project-hub coordination log.

## Verification Notes

- No external email/newsletter send was performed.
- No credentials or tokens were printed.
- Explicit OPS helper fallback was used, then CRM metadata was forced and verified for creator/owner/assignee correctness.
- No Forge, lists, or donations repo implementation was edited from OPS.
- Verified `363191`, `360626`, and `363052` as creator `1`, owner `1332`, assignee `1332`.
- Follow-up code review after Robert's clarification confirms the helper now creates TODO-generated Codex tasks silently by default. No new task was created for this check.

## Rollback Plan

If the routing repair needs rollback, use the same explicit helper or a controlled CRM metadata update to restore the prior owner/assignee state from this log: `363191` and `360626` were owner/assignee `1`; `363052` was owner `167`, assignee `1332`. Documentation changes can be reverted from OPS TODO, AI Workspace TODO, and this project-hub log.

## Follow-Ups

- Start a separate Forge/lists worker for the approved `/donations` email pull/list workflow; do not implement that cross-repo work from OPS.
- Continue direct Codex Portal hydration investigation under `AI-INC-20260412-CODEX-PORTAL-AUTH-01`; this routing slice no longer depends on it for the three existing task metadata repairs.
