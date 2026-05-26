# AI Workers Setup Reminder Runner Map

Project: `AI-INC-20260501-AI-WORKERS-SETUP-01`
Date: 2026-05-17 CDT
Scope: non-secret planning/readback only

## Purpose

Document how reminders are created, which runners execute them, how delivery is verified, and where reminder auditing still has gaps.

## Current Reminder Paths

| Reminder path | Current runner / storage | Current behavior | Verification surfaces | Current gap / note |
| --- | --- | --- | --- | --- |
| Shared Task Flow scheduled reminders | Shared MySQL Task Flow tables via `scripts/task_flow_mysql_recorder.php report` and `due` | Stores due items, scheduled actions, upcoming reminders, and packet readback. | Task Flow packet rows; `report`; `due`; Task Flow page. | Current reminder state is auditable. Papers projection is a separate blocked write lane. |
| Frank due-runner follow-through | `frank/runtime-source/frank-launch/scripts/frank_auto_runner.py` invoking `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py` on a 60-second throttle | Checks due reminders, records state, and can route due items into visible Workspaceboard workers instead of silently leaving them due. | `/Users/admin/.task-flow-launch/state/task-flow-due-runner-last.json`; packet `verification_readback`; Task Flow page. | Internal planning reminders suppress owner-visible email when `notification.reason=no_owner_visible_due_items`. |
| National Outreach / Vanessa reminder work | Shared inbox/runtime plus approved queue/send path where applicable | Supports follow-up reminders, routed team reminders, and recurring Outreach flows. | Task Flow rows; runtime source docs; queue/send logs where an approved send path exists. | Do not assume every reminder path is owner-visible email; some remain routed-worker reminders. |
| Calendar-backed reminders | Per approved calendar lane only | Calendar can support reminders when a verified calendar path exists for the worker identity. | Calendar readback only where separately verified; supporting task/scheduled-action row first. | Calendar verification remains separate from reminder execution; use scheduled-action proof first. |
| Mitch Conti weekly overview | Vanessa directive lane only | Defined as a recurring staffed-tastings-only output, but no live send or queue occurred in this setup slice. | Vanessa directive artifact; future approved send log when activated. | Still approval-gated for live cadence/send execution. |

## Verification Checklist

1. Verify the Task Flow packet key, current status, next update, and any `scheduled_action` in `scripts/task_flow_mysql_recorder.php report`.
2. Verify due-runner state in `/Users/admin/.task-flow-launch/state/task-flow-due-runner-last.json`:
   - `checked_at`
   - `due_count`
   - `recorded`
   - `skipped_existing`
   - `actions`
   - `notification`
3. When a due item becomes routed work instead of an email, verify the visible Workspaceboard session id in the runner summary and packet readback.
4. Use the Task Flow page as the operator surface for `Last Runner`, `Notification`, `Actions`, due rows, and upcoming rows.

## Current Readback Snapshot

- On 2026-05-17 09:32 CDT the due-runner state showed:
  - `checked_at=2026-05-17T09:32:47-0500`
  - `due_count=1`
  - `recorded=1`
  - `skipped_existing=0`
  - `notification.reason=no_owner_visible_due_items`
- That due item was routed into visible Workspaceboard session `7dc067f2`.
- Immediate follow-up `due` readback returned `due_count=0`.

## Exact Remaining Gaps

- Calendar-native reminder creation and calendar event id verification remain separate from the current Task Flow reminder path.
- Mitch weekly overview remains defined but not live-activated in this setup slice.
- The due-runner summary reports `watchdog_script_missing` for `/Users/werkstatt/ai_workspace/scripts/automation_health_watchdog.py`; reminder routing still works, but watchdog readback is not part of the active verification path.

## Boundary

- No external email was sent.
- No runtime or LaunchAgent change was performed in this setup slice.
- No mailbox body output was printed.
