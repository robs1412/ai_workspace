# Morning Automation Reliability Hardening

- Master Incident ID: `AI-INC-20260517-MORNING-AUTOMATION-RELIABILITY-01`
- Date Opened: `2026-05-17`
- Date Completed: `2026-05-17`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Stabilize the morning automation path that covers Vanessa/National Outreach scheduled sends and the Workspaceboard readback surfaces used to judge whether those automations are healthy.

## Symptoms

- Vanessa morning COT messages failed to send until a manual repair was made.
- Workspaceboard showed multiple `Task Flow due worker ...` sessions with multi-hour elapsed times even when the underlying worker sessions were short.
- The National Outreach LaunchDaemon installer reloaded the plist but did not refresh the runtime script bundle, so source/runtime drift was easy to reintroduce.

## Root Cause

- The installed National Outreach runtime still relied on a wrapper script that `require`d the live workspace source copy of `sync_day_of_cot_event_details.php`.
- `nationaloutreach_mail_cycle.py` still hard-coded the workspace source path for `build_mitch_weekly_report.php`.
- `task_flow_due_runner.py` treated daemon-owned scheduled actions as visible worker-routed due items, creating board noise instead of escalating only on failure.
- Workspaceboard closed-session merging allowed proof-state rows to override real session timing, and the Done surface preferred those stale closed-session records over the live managed-session metadata.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260517-MORNING-AUTOMATION-RELIABILITY-01-AI`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Added daemon-owned due-item suppression for National Outreach scheduled actions in `scripts/task_flow_due_runner.py`.
  - Switched National Outreach mail-cycle report generation to resolve `build_mitch_weekly_report.php` from the installed runtime bundle first.
  - Added `tmp/nationaloutreach-launch/sync-runtime.sh` and made the LaunchDaemon install helper refresh runtime scripts before reload.
  - Added direct AI Health follow-through wiring in `scripts/ai_health_check.py` so AI Health can invoke the installed task-flow due runner against queue-mode Task Flow state instead of only sending Task Manager nudges.

### workspaceboard

- Repo Log ID: `AI-INC-20260517-MORNING-AUTOMATION-RELIABILITY-01-WB`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Hardened closed-session merge precedence in `scripts/workspaceboard_db_recorder.php` so proof-state records no longer override authoritative session timing.
  - Corrected Task Flow scheduler totals in `scripts/workspaceboard_db_recorder.php` so queue totals are computed from full packet rows instead of partial row shapes that falsely inflated scheduler-violation counts.
  - Updated `assets/task-management-light.js` to prefer live managed-session records over stale closed-session cache rows in the Done view.
  - Updated `assets/management.js` to use `finished_at` / `closed_at` when present for finished-session history.

## Verification Notes

- National Outreach runtime scripts were synced into `/Users/admin/.nationaloutreach-launch/runtime/scripts/`, including tracked source copies for `run_nationaloutreach_auto.sh`, `sync_day_of_cot_event_details.php`, and `build_mitch_weekly_report.php`.
- Installed runtime syntax checks passed:
  - `python3 -m py_compile` for `/Users/admin/.task-flow-launch/runtime/scripts/task_flow_due_runner.py`
  - `python3 -m py_compile` for `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`
  - `php -l` for `/Users/admin/.nationaloutreach-launch/runtime/scripts/sync_day_of_cot_event_details.php`
  - `php -l` for `/Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_db_recorder.php`
- Installed due-runner behavior check passed: a synthetic Vanessa scheduled-action item now returns `True` for `is_daemon_owned_due_item(...)`.
- LaunchDaemon readback after runtime sync stayed healthy:
  - `launchctl print system/com.koval.nationaloutreach-auto`
  - `runs = 2072`
  - `last exit code = 0`
- Workspaceboard closed-session overview readback is corrected for the previously misleading rows:
  - `89d6ffd6` now reads `2026-05-17T10:34:16-05:00 -> 2026-05-17T10:34:20-05:00`
  - `d91e3385` now reads `2026-05-17T10:33:38-05:00 -> 2026-05-17T10:33:48-05:00`
- Queue truth check now matches live AI Health follow-through behavior:
  - `php /Users/admin/.workspaceboard-launch/runtime/app/scripts/workspaceboard_db_recorder.php task-flow-report` with `{"mode":"queue","limit":500}` now returns `scheduler_violations = 0` and `scheduler_route_candidates = 0`.
  - Manual AI Health run at `/Users/werkstatt/ai_workspace/tmp/ai-health-manager-manual4/latest.json` reports `task_flow_followthrough = none`, `task_flow_followthrough_checked = 0`, matching the queue readback instead of the earlier false `110` scheduler items.
- Frank and Avignon runtime packaging drift was repaired by restoring the shared helper module `scripts/email_worker_threads.py`, syncing it into the Frank/Avignon runtime mirrors, and confirming both `system/com.koval.frank-auto` and `system/com.koval.avignon-auto` returned to `last exit code = 0`.
- Workspaceboard mailbox monitor readback was corrected to use the live automation logs for Frank and Avignon instead of stale stdout assumptions, and the board API now reports both monitors as `runtime_status = live` / `status_label = monitoring`.
- AI Health mailbox canaries now pass after two fixes:
  - the synthetic canary packet includes `closeout_proof_marker`
  - `scripts/task_flow_mysql_recorder.php` now counts `closeout_proof_marker` as valid closeout proof during `validate`
- AI Health standing-role classification was narrowed so only real monitoring sessions count as standing monitors, preventing finished historical `Task Manager ...` rows from surfacing as current standing-monitor failures.
- AI Health stale-session classification now treats old `db-recorded` work rows as stale work to reconcile rather than current runtime failures, and status fetches now retry before declaring the board down. Direct live-function verification after the patch reports:
  - `board_ok = true`
  - `mailbox_canaries = passed`
  - `mailbox_canary_issues = 0`
  - `unhealthy = 0`
  - `stale_working = 11`
  - `standing_attention = 1`
- Follow-up cleanup completed on the same pass:
  - nudged the standing Security Guard and Summary Worker sessions so their live heartbeats advanced again
  - closed the stray `Task Flow due worker 2026-05-17 10:03 nationaloutreach` wrapper session `e4762142`
  - reconciled the orphaned `db-recorded` work-state residue (`052cfb36`, `1897a321`, `41e793f8`, `992308bd`, `ad6c467b`, `bda361f1`, `d21831bb`, `dfd3de48`, `ee72a8f8`, `fa3057f1`) to `closed_with_proof` with explicit board-hygiene proof markers rather than leaving them as active stale work
  - final direct live-function verification now reports:
    - `board_ok = true`
    - `mailbox_canaries = passed`
    - `unhealthy = 0`
    - `stale_working = 0`
    - `standing_attention = 0`
- Remaining management noise after the repair is no longer runtime failure. It is queue hygiene only: `session-sprawl` still reports `39` non-standing open sessions (`31` review-ready, `6` stale-waiting, `2` active working), which needs a separate closure/routing sweep rather than another monitor/runtime fix.
- Final AI Health counting alignment then removed the last false queue-hygiene alarm:
  - `scripts/ai_health_check.py` now classifies `runtime_status = closed` finished rows as `closed_history_sessions` instead of `review_ready_sessions`
  - direct live verification after that change reads `review_ready = 0`, `closed_history = 31`, `active_working = 2`, `stale_waiting = 6`, `non_standing_open_count = 8`, and `management_issues = 0`
  - the remaining open set is now the real current set rather than finished historical residue
- Final follow-through hardening fixed a live packet-regression bug on Avignon direct-owner lanes:
  - root cause: repeated `avignon_previous_message_reconciled` events were weaker blocked-state monitor updates, but `scripts/task_flow_mysql_recorder.php` still allowed them to overwrite stronger packet state such as a visible `workspaceboard_session`, owner-visible blocker/report Message-ID, or stronger `reported` / worker-backed status
  - fix: `task_flow_should_preserve_existing_packet()` now preserves stronger existing packet state when an incoming weaker blocked/captured/routed reconciliation event would drop the session route or erase proof-backed closeout/blocker data
  - live verification after syncing the recorder to the installed runtime copies: the recurring Avignon reconciliation events continued firing, but the packet rows held the stronger state instead of reverting. Current durable readback:
    - `avignon-direct-owner-sonat-CALbLtzw-EqK13wiSMx7sm7YsRYbUDRN-12MGKW-GxQxJ03aERA-mail-gmail-com` keeps `workspaceboard_session = 9d17e682` plus blocker-report Message-ID `<177903869964.23001.6671306499980355206@kovaldistillery.com>`
    - `avignon-direct-owner-robert-approver-CAAtX44aQtnbfHErsuUqK0rUni5Df4m8Nxf18ycVTCTXqJFO-KA-mail-gmail-com` keeps `workspaceboard_session = 717925bb` plus duplicate-completion Message-ID `<177885596689.51762.12536657929911260039@kovaldistillery.com>`
  - same pass queue movement: `21` stale `logged-no-action` packets normalized to `no_action_closed`, one Frank direct-primary packet reconciled from blocked to `reported`, and the routed National Outreach overdue-reports packet now has visible worker session `63069bff`
- Final queue-authority hardening removed the remaining mixed-source stats surface:
  - `workspaceboard/api/stats` and `workspaceboard/server/index.js` now read Task Flow totals from `workspaceboard_db_recorder.php task-flow-report` with `mode = all`, and read queue rows separately from `mode = queue`, instead of inferring global queue counts from a partial runtime/session slice
  - the Workspaceboard runtime copies were synced and the `com.koval.workspaceboard` listener was restarted cleanly so `http://127.0.0.1:17878/api/stats` now reports `source.mode = db-queue-authoritative` and `task_flow_source = workspaceboard_db_direct`
  - live readback now matches the DB report for queue totals: `open = 249`, `blocked = 24`, `waiting = 218`, `scheduler_violations = 0`, `scheduler_route_candidates = 0`

## Rollback Plan

- Revert the three source areas independently if needed:
  - `ai_workspace/scripts/task_flow_due_runner.py`
  - `ai_workspace/scripts/nationaloutreach_mail_cycle.py`
  - `workspaceboard/scripts/workspaceboard_db_recorder.php`
  - `workspaceboard/assets/task-management-light.js`
  - `workspaceboard/assets/management.js`
- Restore the prior installed National Outreach runtime bundle from local backups if the new runtime sync introduces a regression.

## Follow-Ups

- Consider moving the remaining National Outreach PHP helpers fully into the runtime bundle or a versioned install artifact, rather than referencing mutable workspace code.
- Add a health surface for `last_success_at`, `last_error_at`, and `last_send_count` so morning automation health does not have to be inferred from session history.
- Remaining automation debt is now clearly separated from runtime breakage: the live health surface is clean on send path, mailbox canaries, stale-work cleanup, standing-monitor attention, and false sprawl alarms. The next work slice is actual product/task flow: dashboard progress and any true waiting/blocker reconciliation that still matters.
