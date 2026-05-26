# AI Manager Architecture Hardening

- Task Flow anchor: `ai-manager-architecture-hardening-2026-05-16`
- Recorded at: `2026-05-16 19:19:55 CDT`
- Owner workspace: `ws ai`
- Output channel: `AI Manager readback`

## First Deliverable

Reduce the historic handled-but-unproven backlog into one of four durable states only:

1. `closed_with_proof`
2. `no_action_closed` with a real no-action reason
3. `blocked` with exact source, blocker text, and owner question only if a real blocker remains
4. `superseded` by a newer proof-backed result

## Before Counts

Source snapshots:

- `php /Users/werkstatt/workspaceboard/scripts/workspaceboard_db_recorder.php overview`
- `php /Users/werkstatt/workspaceboard/scripts/workspaceboard_db_recorder.php task-flow-report` with JSON stdin `{"mode":"all","limit":2000}`
- `php /Users/werkstatt/ai_workspace/scripts/task_flow_mysql_recorder.php report 2000`

Board / Task Flow baseline:

- Total Task Flow rows in DB: `1349`
- Effective open rows: `297`
- Effective waiting rows: `270`
- Queue-visible rows in current Task Flow report: `340`
- Queue-visible handled-but-unproven proof-gap rows: `41`

Historic handled-but-unproven backlog detail:

- `41` rows currently carry `owner_visible_completion_or_blocker_missing_after_handled_filing`
- All `41` are still status `waiting`
- Owner split: `35 outreach-coordinator`, `4 naomi-stern`, `2 ezra-katz`
- The same queue-visible report also shows `41` handled-filed proof gaps and `79` rows missing a durable `due_or_trigger_or_scheduled_action`

Broader open-no-proof pressure from the Workspaceboard DB sample:

- `156` waiting rows without proof
- `53` blocked rows without proof
- `22` routed rows without proof
- `3` classified rows without proof
- `1` working row without proof

## After Plan

Primary target for lane 5:

- Reduce `owner_visible_completion_or_blocker_missing_after_handled_filing` from `41` to `0`

Expected normalized outcomes for those `41` rows:

- Convert rows with existing owner-visible completion evidence to proof-backed closed states
- Convert true no-action duplicates or FYI remnants to `no_action_closed` with explicit reason
- Convert unresolved real dependency rows to `blocked` with exact blocker/source and one owner question only if needed
- Convert rows already overtaken by a later proof-backed packet to `superseded`

Required secondary cleanup while touching each row:

- Replace vague `waiting` residue with a real `next_check_at` or a terminal state
- Fill `due_or_trigger_or_scheduled_action` when the row remains open
- Preserve proof markers in Task Flow instead of relying on `Handled` filing text

Projected after-state band once this slice is completed:

- Handled-but-unproven proof-gap rows: `0`
- Effective waiting rows: `270` minus however many of the `41` normalize to closed/no-action/superseded
- Remaining waiting rows should all have either a real next check or a real blocker, not `Handled` residue

## Concrete Example Set

Representative rows from the current flagged set:

1. `taskflow-9662e72d353fa5dd`
   - Owner: `outreach-coordinator`
   - Source: `Re: FW: JCYS Event Info Needed`
   - Current residue: `Filed out of INBOX to Handled - AI Workers after durable route logging.`
   - Invalid waiting text: `still waiting for owner-visible completion proof or one exact blocker within 2 minutes`
   - Required normalization: close with proof, exact blocker, or superseded packet

2. `taskflow-01edba3f6d64b5a4`
   - Owner: `outreach-coordinator`
   - Source: `Fwd: KOVAL Inquiry: General Inquiry`
   - Current residue: filed to `Handled` with no owner-visible completion/blocker proof
   - Required normalization: same four-way outcome only

3. `taskflow-62d4de72c6a0f576`
   - Owner: `ezra-katz`
   - Source: `Re: Whiskey and Cigar Social counsel-ready brief`
   - Missing fields: `ops_portal_or_domain_task`, `due_or_trigger_or_scheduled_action`, handled-proof gap
   - Required normalization: add durable task reference if still open, otherwise close/supersede

4. `taskflow-dbb01c24d70cb23f`
   - Owner: `naomi-stern`
   - Source: `Re: Distill America in Wisconsin`
   - Missing fields: `ops_portal_or_domain_task`, `due_or_trigger_or_scheduled_action`, handled-proof gap
   - Required normalization: same as above

5. `taskflow-b08a6bb2051d9086`
   - Owner: `outreach-coordinator`
   - Source: `Re: COI`
   - Current residue: `Handled` filing note without terminal proof
   - Required normalization: exact blocker or proof-backed closeout

## Architecture Notes

The measurable fault is not just stale waiting count. The specific hardening problem is that `Handled` filing text can survive as a pseudo-closeout while Task Flow still reports `waiting` and lacks proof. The cleanup contract for this lane should therefore treat these rows as an architecture-backed normalization queue, not as ordinary follow-up reminders.

Recommended next implementation slice:

1. Add a deterministic repair path for rows flagged with `owner_visible_completion_or_blocker_missing_after_handled_filing`
2. Require the repair to emit one of the four terminal outcomes above instead of leaving `waiting`
3. Keep the queue throttled and owner-silent during routine cleanup unless a real blocker remains

## Due Worker Checkpoint

- Checkpoint time: `2026-05-16 19:29 CDT`
- Due-worker result: `waiting with next check`
- First patch candidate is already present in the dirty `workspaceboard` tree:
  - AI Manager route receipts now carry route state, worker/session id, packet id, model, and first next-check time.
  - Task Light / DB recorder hardening narrows constant-on monitor detection to canonical standing services and exposes DB-cache source state.
  - Default model readback now distinguishes the substantive default (`gpt-5.4`) from the tiny-helper path (`gpt-5.4-mini`).
  - Papers/dashboard work is split into an architecture gate with explicit approval fields instead of being treated as a generic dashboard build.
- Verification run:
  - `node --test server/test/ai-manager-phone.test.js` passed.
  - `node --test server/test/session-status.test.js` passed.
- Residual risk:
  - A combined two-file `node --test server/test/session-status.test.js server/test/ai-manager-phone.test.js` run failed once with a cross-file flake around constant-on classification, then the isolated status suite passed cleanly. Treat combined-run stability as the next verification slice rather than proof of a remaining logic blocker.
- Next check target:
  - Re-run the combined Workspaceboard test slice and either isolate/fix the shared-state flake or promote the current patch set to a proof-backed implementation closeout.

## 2026-05-20 Event-Log Repair

- The AI Manager input recorder now writes both current and legacy audit surfaces again.
- `scripts/ai_manager_input_recorder.php` was updated so each `record` and `update` call appends a matching row to `koval_crm.ai_manager_input_events` while still upserting `koval_crm.ai_manager_inputs`.
- Live smoke through `POST /api/ai-manager/daily-input` returned `db_ok: true`, created `ai_manager_inputs.id=1982`, and advanced the legacy event table to `ai_manager_input_events.id=1995` with `logged_at=2026-05-20 08:56:17`.
- Result: the stale May 16 event-log surface is repaired; future AI Manager input writes should now move both DB surfaces together.
- 2026-05-20 follow-through: backfilled 13 missing legacy rows from `koval_crm.ai_manager_inputs` into `koval_crm.ai_manager_input_events` using the new `backfill-events` command. The event tail now reaches `ai_manager_input_events.id=2008` at `2026-05-20 08:59:46`, and the current post-2026-05-17 missing-event count for inputs is 0.
- 2026-05-20 scheduling follow-through: the input-trail repair is now tracked as a weekly recurring audit in `project_hub/repeating-tasks.json` with Monday checks for both the AI Manager input writer and the legacy event trail. The intent is to catch any future drift between `ai_manager_inputs`, the daily-input Markdown trail, and `ai_manager_input_events` before it sits stale for days again.
- 2026-05-20 OPS follow-through: created silent Codex-owned OPS task `369932` (`Weekly AI Manager input legacy-trail audit`) due `2026-05-25`, creator `1`, owner/assignee `1332`, status `Not Started`. This keeps the weekly audit in the DB-backed task spine as well as the recurring-task JSON.
- 2026-05-20 chat-entry bridge follow-through: added `scripts/ai_manager_chat_entry_adapter.php` as the explicit AI Manager control-lane transport hook. Future AI Manager prompts and durable decisions should go through this bridge so they land in both `koval_crm.ai_manager_inputs` and the daily-input markdown trail instead of staying only in chat history.
- 2026-05-20 Papers write follow-through: created the `papers-write` skill and the local `papers_write_note.py` publisher, but the live Papers MCP still rejects `papers_create` for client `codex`. Sent a Codex-side permission request to Claude (`Codex Papers write permission needed for durable assessment link`, Message-ID `<177929804365.25895.6505397721653286721@kovaldistillery.com>`) and copied Robert so the approved write client/path can be confirmed before the assessment is published.
- 2026-05-21 Papers write recovery is now source-proven complete. The original durability note publish succeeded at Papers GUID `3ee50607-df35-401c-a6c9-6f601127deb3` / path `ai-manager/durability/2026-05-21-ai-manager-durability-rules.md`, and a second live verification write from this shell succeeded at GUID `68a9266a-4563-44e5-ad01-eb6ddf234b81` / path `ai-manager/durability/2026-05-21-codex-papers-write-restored.md` using local source file `project_hub/artifacts/ai-manager-durability/codex-papers-write-restored-2026-05-21.md`. The active state is no longer `papers_create` denied; Codex can use the approved writer path for non-secret durable Papers notes.

## 2026-05-25 Direct Terminal DB Logging Directive

- Robert directive recorded at `2026-05-25 12:43 CDT`: all substantive work must be logged according to Task Flow in the DB-backed task spine. This includes work started from `ai-manager.php`, routed Workspaceboard workers, and approved direct terminal task-mode execution.
- Architecture correction: markdown handoffs, TODO projections, and chat readbacks remain useful proof surfaces, but they are not sufficient as the primary durable record for substantive work. The server-hardened flow must make the work traceable through DB-visible Task Flow rows so route history, proof state, and stats survive across control surfaces.
- Concrete enforcement target:
  1. every substantive direct-terminal task-mode pass must mint or update a Task Flow packet,
  2. AI Manager prompts/corrections/durable decisions must keep landing in `ai_manager_inputs`,
  3. direct-terminal and routed-worker executions should share a common Task Flow reporting contract so stats/counts do not drift by launch surface.
- Immediate proof from the same correction cycle: the `task-db.php` repair pass is now recorded as Task Flow key `taskflow-workspaceboard-task-db-route-repair-2026-05-25`, in addition to the repo-local proof note in `workspaceboard/HANDOFF.md`.
- Next hardening slice: add an explicit direct-terminal recorder path or guardrail so starting work outside a visible Workspaceboard worker still creates the DB-visible Task Flow packet before the work is treated as in progress.
