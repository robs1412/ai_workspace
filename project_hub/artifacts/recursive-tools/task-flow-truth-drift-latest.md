# Task Flow Truth Drift Check

- Recorded: 2026-05-26 17:20:11 
- Config: `/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json`
- Board ok: `True`
- Managed sessions: `18`
- Task Flow rows scanned: `500`
- Proof rows scanned: `26`
- Drift count: `5`

## Summary

- scheduler_violations: `0`
- scheduler_route_candidates: `0`
- proof_closeout_issues: `1`

## Drift

- active_missing_board_session: `high` Daily 10 PM repo cleanup: inspect /Users/werkstatt git repos, commit/push intentional changes, report exact blockers.
  - detail: active Task Flow row references missing board session start_or_reuse_visible_repo_cleanup_worker_at_2200
  - session_id: `start_or_reuse_visible_repo_cleanup_worker_at_2200`
  - dedupe_key: `daily-codex-repo-cleanup-2200`
- active_missing_board_session: `high` At 7:15, start/reuse visible Workspaceboard cleanup worker if waiting/blocked rows exist; Frank emails Robert after readback.
  - detail: active Task Flow row references missing board session start_or_reuse_visible_cleanup_worker_at_0715_when_rows_exist
  - session_id: `start_or_reuse_visible_cleanup_worker_at_0715_when_rows_exist`
  - dedupe_key: `daily-frank-workspaceboard-task-db-waiting-blocked-0715`
- active_missing_board_session: `high` Square list email-send workflow, not list creation
  - detail: active Task Flow row references missing board session task-mode-chat
  - session_id: `task-mode-chat`
  - dedupe_key: `ops-overdue-ai-worker-363191`
- active_missing_board_session: `high` Follow up on DA and incentive strategy first-plan email and continue Salesreport data pull after scope confirmation
  - detail: active Task Flow row references missing board session task-mode-chat
  - session_id: `task-mode-chat`
  - dedupe_key: `ops-overdue-ai-worker-334481`
- active_missing_board_session: `high` Continue overdue OPS AI-worker cleanup/execution
  - detail: active Task Flow row references missing board session task-mode-chat
  - session_id: `task-mode-chat`
  - dedupe_key: `taskmode-ops-overdue-ai-worker-tasks-2026-05-26`

## Recommendation

- Truth drift exists. Repair should stay targeted to the named contradiction classes, not broad queue mutation.
