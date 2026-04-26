# Frank Routed Task ID Recording

Last Updated: 2026-04-20 15:35 CDT

Frank routed-email work must carry a compact, durable ID block in local TODO/HANDOFF records, task briefs, routed-worker closeouts, and Robert completion reports.

Use real IDs only. Do not invent a Claude task number, bridge ref, OPS/Portal ID, outbound Message-ID, or board session ID when it is not available yet. Write `none created`, `not available`, or `not applicable` instead.

Captured/routed acknowledgements for direct Robert work must name the visible work route after prompt delivery. Do not send Robert only generic `Task Manager session` language when a visible session ID and title/task name exist. Do not send this acknowledgement at all for quick-answer items that can be answered directly in the same pass; send the answer instead and log the handled state.

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
- Board/Codex session title: record the visible board-managed worker/session title or task name whenever it exists. Owner-facing captured/routed acknowledgements must include this title with the session ID.
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

Style rule for Robert-facing captured/routed, status, blocker, and closeout replies: start with the point as the first sentence, but do not use the literal opener `Point first:`. The point should read as normal prose, not a label. When the reply has more than one thought, split it into short paragraphs with a blank line between them so the message scans cleanly.

For Claude/Codex bridge work, keep Claude's `task #...` / `ref:...` separate from Frank's local task id and the board/Codex session id. If an OPS/Portal task is created later, add it without replacing historical source, local, board, or outbound Message-ID fields.

## Captured/Routed Acknowledgement Template

Use this shape for direct Robert owner-facing captured/routed acknowledgements only after the visible worker session exists, the prompt has landed, and the 10-minute acknowledgement delay has elapsed with the worker still pending:

Do not use this shape for quick answers. If Frank already has the answer and can safely send it in the same pass, lead with the answer and omit the receipt/routing language. Do not use this shape when the routed worker completes or blocks inside the 10-minute delay; send only the completion or blocker report.

```text
Hi Robert,

Captured: [plain-language subject/request].

I routed it into visible work session [session id] / [session title or task name]. Current status: captured and routed; not complete yet.
Next: I will follow the worker to completion or a real blocker, then send the closeout before the source message is filed to Handled.
```

The runtime wording may compress this to:

```text
Captured and routed: [plain-language subject/request].
I routed it into visible work session [session id] / [session title or task name].
Current status: not complete yet.
Next: ...
```

Requirements:

- Include the visible work session ID and the session title/task name in the acknowledgement.
- If the session title/task name is unavailable, wait and re-check the board/session creation result before sending when the task is routed work.
- Hold the acknowledgement for 10 minutes after route creation; suppress it if a completion or blocker report is sent first.
- Record source `Message-ID`, dedupe key, owner, routed workspace, session ID/title, prompt-delivery state, current status, completion target, and outbound acknowledgement `Message-ID` in TODO/HANDOFF/log state.
- Do not expose session IDs, source `Message-ID`s, TODO/HANDOFF details, or other internal control-surface language to external senders.

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
