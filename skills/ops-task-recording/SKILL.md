---
name: ops-task-recording
description: Use for `/Users/werkstatt/ops` task creation that must be recorded durably across OPS, Workspaceboard, and Task Flow. Trigger when the user asks to create Codex-owned OPS tasks, assign due/start dates, route a visible Workspaceboard worker, or ensure OPS task packets carry the linked worker/session id.
---

# OPS Task Recording

Use this skill when work needs all of these outcomes together:

- create or update a Codex-owned OPS task
- keep the task silent unless notification is explicitly wanted
- create a visible Workspaceboard worker/session for the task
- record the OPS task id plus Workspaceboard session id in Task Flow

## Workflow

1. Confirm the task packet first.
   - One-line subject.
   - Due date and start date.
   - Notes/instructions.
   - Target workspace for the worker.
   - Creator/owner/assignee intent.

2. Use the normal OPS task helper.
   - Primary helper: `/Users/werkstatt/ops/scripts/create_codex_task.php`
   - Default creator: `1`
   - Default owner/assignee: `1332`
   - Tasks are silent by default unless the user explicitly wants notifications.

3. Create the visible Workspaceboard worker/session.
   - Use the helper script in this skill instead of creating an unlinked OPS task.
   - The worker title should make the OPS task easy to find from the board.
   - The worker brief should include the OPS task id, due date, notes, and proof expectation.

4. Record the Task Flow packet.
   - Store the OPS task id in `ops_portal_or_domain_task`.
   - Store the board session id in `workspaceboard_session`.
   - Use a stable source ref and dedupe key so future follow-up can update the same packet.

5. Verify readback before claiming completion.
   - OPS task id exists with creator `1`, owner `1332`, assignee `1332`, due/start dates, and active state.
   - Workspaceboard session id exists.
   - Task Flow packet exists with both ids linked.

## Entry Point

- Script: `scripts/create_ops_task_with_workspaceboard_route.py`

## Notes

- Prefer the domain helper and recorder paths over direct DB inserts.
- Keep notes non-secret.
- If OPS creation succeeds but Workspaceboard or Task Flow recording fails, stop and report the exact partial state instead of claiming the task is fully recorded.
