# Shared Captured/Routed Receipt Parity Note

Status: active non-secret comparison note
Created: 2026-04-20
Updated: 2026-04-22
Source Message-IDs:
- `<CAAtX44bCjzkXSKDa9sYc8ZP7qfvvRQ5gUxteLJ2aMJh7HnVfOg@mail.gmail.com>`
- `<CAAtX44b5Y=gPoaF+KifBOf048XzmG+bOnqiQ8baLK4dFmwk9Kw@mail.gmail.com>`
Worker sessions:
- `00d4fd0c` / `Frank vs Avignon captured/routed receipt template parity check`
- `220cf4d4` / `Frank response template session-name parity`
Related shared-memory session: `0a741b92` / `Shared email-worker how-to memory path`

## Finding

Avignon's newer captured/routed receipt is better because Avignon received a direct-owner follow-through runtime patch on 2026-04-20. The patch added a dedicated direct-owner path for Sonat and Robert-as-Avignon-approver work:

- Create a visible Avignon workspace session.
- Inject the direct-owner task brief.
- Record source Message-ID, dedupe key, owner, session id/title, current state, completion target, report target, and prompt-delivery metadata.
- Send a concise captured/routed acknowledgement that names the visible session id/title.
- Hold pending direct-owner work out of `Handled` until completion or blocker closeout.

The Activity-check incident was related but not the general template source. It exposed a direct-Robert Avignon runtime send bug and created repeated Activity-check worker sessions. The reusable improvement is the direct-owner runtime path above, not private Activity-check content.

The 2026-04-20 Frank follow-up session `220cf4d4` confirmed the same template standard for Frank docs: owner-facing captured/routed acknowledgements should name the visible work session id and title/task name after prompt delivery, not only say that the request was routed to a generic Task Manager session.

Robert's 2026-04-21 quick-answer correction applies to both Frank and Avignon. Direct primary-owner items that can be answered safely in the same pass should be answered directly and should not receive a separate captured/routed receipt. Captured/routed acknowledgements are for work that will take a moment, is otherwise invisible to the owner, or is not immediately answerable.

Robert's 2026-04-22 acknowledgement-noise correction adds a timing rule for direct primary-owner routed work: hold captured/routed acknowledgements for 10 minutes. If the routed worker completes or blocks before that delay expires, send only the task-specific completion or blocker report and file the source after logging. If the worker is still pending after 10 minutes, send one captured/routed acknowledgement that names the visible session id/title, then continue monitoring to completion or blocker closeout. This is a shared mechanic; persona and recipient routing remain Frank- or Avignon-specific. The 2026-04-22 source slice applies the behavior to Frank runtime-source only; Avignon runtime is unchanged in that slice.

## Frank Parity

Frank's policy docs already require the same direct-owner mechanics for Robert. The installed Frank runtime is not fully at parity with the newer Avignon implementation.

Current Frank installed path inspected:

- `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`

The current Frank acknowledgement path routes direct Robert input through Task Manager and sends a captured/routed acknowledgement, but it records and reports only the Task Manager session id returned by `/api/task-manager/message`. It does not preserve the visible session title, prompt-delivery metadata, direct-owner current state, completion target, report target, or monitor pending direct-owner sessions to completion/blocker before filing the source.

Exact Frank runtime functions needing review if parity is required:

- `route_to_task_manager()`
- `compose_primary_ack()`
- direct-primary classification branches that set `routed-primary-*-ack-sent`
- previously logged INBOX residue handling for direct-primary pending work

Because those are installed mailbox/runtime behaviors under `/Users/admin/.frank-launch/`, parity is not a docs-only change.

## Safe Template Standard

For internal primary-owner captured/routed acknowledgements, use this non-secret shape only when a separate acknowledgement is needed, after the visible worker exists and the prompt has landed, and the applicable acknowledgement delay has elapsed while the worker is still pending:

```text
Hi [Owner],

Captured: [plain-language subject/request].

I routed it into visible work session [session id] / [session title]. Current status: captured and routed; not complete yet.
Next: I will follow the worker to completion or a real blocker, then send the closeout before the source message is filed to Handled.
```

Worker-specific persona and owner routing still apply:

- Frank reports to Robert by default.
- Avignon reports to Sonat by default and reports to Robert when Robert is acting as Avignon workflow owner/approver.
- Quick answers should be answered directly in the same pass without a separate captured/routed receipt.
- Routed-work acknowledgements should be held for 10 minutes and suppressed if the completion or blocker report is ready first.
- External senders must not receive internal captured/routed/control-surface receipts.

## Required Route If Runtime Parity Is Approved

Route through Code/Git Manager with Security Guard review because the work changes installed mailbox automation behavior and can send owner acknowledgements or affect handled-mail filing. The implementation should be narrow:

- Patch `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`.
- Add or identify a git-backed source mirror for the Frank installed runner before commit/push.
- Preserve current Frank duplicate protection, Robert-only send guard, and existing no-action/FYI behavior.
- Add visible session id/title, prompt-delivery/current-state metadata, completion target/report target, and pending direct-owner closeout monitoring only for direct Robert work.
- Verify with `python3 -m py_compile` and synthetic non-mailbox tests first.
- Do not run a live mailbox cycle, send mail, move mailbox state, reload/restart LaunchAgents, change cadence, deploy, commit, push, or touch credentials/OAuth without the separate approval for that step.
