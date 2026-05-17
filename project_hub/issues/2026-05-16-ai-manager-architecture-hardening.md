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
