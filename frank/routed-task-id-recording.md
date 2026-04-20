# Frank Routed Task ID Recording

Last Updated: 2026-04-19 16:55 CDT

Frank routed-email work must carry a compact, durable ID block in local TODO/HANDOFF records, task briefs, routed-worker closeouts, and Robert completion reports.

Use real IDs only. Do not invent a Claude task number, bridge ref, OPS/Portal ID, outbound Message-ID, or board session ID when it is not available yet. Write `none created`, `not available`, or `not applicable` instead.

## Canonical ID Block

```text
ID block:
- Source Message-ID: <source-message-id>
- Dedupe key: frank-...
- Local task ID: frank-...
- Board/Codex session ID: ...
- Claude/bridge task ID: task #... / ref:... / not available
- OPS/Portal task ID: ... / none created
- Outbound Message-ID: <message-id> / not sent yet
- Current status: routed | working | blocked | completed | filed
```

## Field Rules

- Source Message-ID: use the original inbound email `Message-ID` when the task came from mail.
- Dedupe key: derive from the local task purpose plus normalized source `Message-ID`; keep it stable for follow-ups.
- Local task ID: use the Frank local task id when no OPS/Portal task exists, or keep it as the Frank route id alongside the OPS/Portal id.
- Board/Codex session ID: record the visible board-managed worker/session id that performed the work.
- Claude/bridge task ID: record Claude's `task #...` and `ref:...` convention only when Claude supplied it or an existing non-secret log already contains it.
- OPS/Portal task ID: prefer the OPS/Portal id as canonical when one is created through the approved path.
- Outbound Message-ID: record each acknowledgement, routed-status note, completion report, or bridge email once sent.
- Current status: update as the task moves through `routed`, `working`, `blocked`, `completed`, and `filed`.

## Reporting Rule

Every Frank completion report for routed email-derived work should include:

1. What was done.
2. What changed.
3. What was not done.
4. Verification performed.
5. Remaining blocker or decision, if any.
6. The ID block above.

For Claude/Codex bridge work, keep Claude's `task #...` / `ref:...` separate from Frank's local task id and the board/Codex session id. If an OPS/Portal task is created later, add it without replacing historical source, local, board, or outbound Message-ID fields.

## Current Task Record

ID block:
- Source Message-ID: `<CAAtX44asa5JXGUhiF7KXuNzCC4dnfFvjGhyAXjFON62Qq=DnbA@mail.gmail.com>`
- Dedupe key: `frank-routed-task-id-recording-CAAtX44asa5JXGUhiF7KXuNzCC4dnfFvjGhyAXjFON62Qq-DnbA`
- Local task ID: `frank-2026-04-19-routed-task-id-recording-workflow`
- Board/Codex session ID: `bff2d116`
- Claude/bridge task ID: not available in local non-secret metadata for this source
- OPS/Portal task ID: none created
- Outbound Message-ID: capture ack `<177663384714.39356.12843538403633616685@kovaldistillery.com>`; completion report `<177663408472.52512.7962573480166008562@kovaldistillery.com>`
- Current status: completed
