# Frank and Codex Send Behavior Hardening

Date: 2026-05-27

## Requested Task

Robert asked for a shared Robert + Codex OPS task to harden outbound send behavior:

- clarify who sends outbound messages,
- separate Frank owner/email behavior from Codex implementation/task behavior,
- define approval gates for sends,
- use the regular OPS route,
- send the normal OPS notification,
- do not create a silent task.

Requested title:

`Harden Frank and Codex outbound send behavior and lane separation`

Requested due date used for attempted create: `2026-05-28`.

## Regular OPS Create Attempts

Attempt 1:

- Command path: `/Users/werkstatt/ops/scripts/create_codex_task.php`
- Assignees: Robert `1` and Codex `1332`
- Notification: `--notify=1`
- Result: `CRM API error: HTTP 500` on the Codex impersonation path.

Attempt 2:

- Same task packet, retry with `--impersonate=admin`
- Notification: `--notify=1`
- Result: `Portal session expired. Please sign in again`; service login reported access denied for `testuser2:admin`.

Readback:

- Exact-title CRM DB readback returned no matching task rows.

Retry after Robert's `re-create` instruction:

- Command path: `/Users/werkstatt/ops/scripts/create_codex_task.php`
- Assignees: Robert `1` and Codex `1332`
- Notification: `--notify=1`
- Result: OPS task `370301` created.
- Readback: subject `Harden Frank and Codex outbound send behavior and lane separation`, status `Not Started`, `due_date=2026-05-28`, `date_start=2026-05-28`, `smcreatorid=1`, `smownerid=1`, `assigned_user_ids=1,1332`, `deleted=0`.

## Boundary

No raw direct OPS task insert was performed because Robert explicitly requested the regular route with notification.

## Durable State

- Task Flow source ref: `chat-robert-send-behavior-hardening-ops-task-2026-05-27`
- AI Manager input recorder row: `2348`
- OPS task: `370301`
- Current state: OPS task created; implementation remains pending.

## Next Step

Use OPS task `370301` as the shared Robert + Codex lane for the send-behavior hardening implementation.
