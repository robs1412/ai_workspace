# Server overload and token runaway mitigation - 2026-05-27

## Live mitigation

- Closed 172 orphaned `codex-board-*` tmux sessions.
- Reduced tmux-backed Codex board sessions from 181 to 9.
- Restarted Workspaceboard Node server after stale-session cleanup caused high CPU.
- Stopped active Frank and Avignon mailbox cycles.
- Added pause sentinels to:
  - `/Users/admin/.frank-launch/runtime/scripts/run_frank_auto.sh`
  - `/Users/admin/.avignon-launch/runtime/scripts/run_avignon_auto.sh`
- Created pause files:
  - `/Users/admin/.frank-launch/state/automation-paused`
  - `/Users/admin/.avignon-launch/state/automation-paused`
- Sent Frank report to Robert:
  - Message-ID: `<177988873175.66012.5393782947166836216@kovaldistillery.com>`
  - task_id: `server-overload-token-runaway-2026-05-27`

## Evidence

- Local history since 2026-05-26 21:00 CDT showed 531 prompt entries.
- 256 were `Avignon direct-owner intake task`.
- 259 were `Workspaceboard worker lifecycle contract`.
- 267 Codex session JSONL files existed since 2026-05-26 21:00 CDT.
- 266 included the full `AGENTS.md` startup context.
- Repeated `AGENTS.md` rehydration accounted for roughly 8.8M chars of session content.

## Remaining build

1. Add a Workspaceboard automation circuit breaker for max new sessions per source thread and per mailbox cycle.
2. Add Task Flow duplicate-route enforcement: one active `workspaceboard_session` per `dedupe_key`.
3. Add load-aware overload mode: when load or live tmux count is high, pause mailbox fan-out and report one blocker.
4. Replace full `AGENTS.md` worker startup injection for duplicate/residue checks with a compact role contract.
5. Add a cleanup endpoint or script that closes orphaned tmux sessions not present in the managed-session read model.

## Done

- 2026-05-27 09:51 CDT: recorded host-level Workspaceboard tmux orphan detection in `scripts/ai_health_check.py`. The health report now logs unmanaged `codex-board-*` tmux sessions to `tmp/ai-health-manager/host-tmux-orphans.jsonl`, includes `host_tmux_orphan_check` in `latest.json`, adds a `Host Tmux Orphans` section to `latest.md`, and includes the orphan count in the canonical status line. Cleanup is opt-in through `AI_HEALTH_ENABLE_HOST_TMUX_ORPHAN_CLEANUP=1`; default behavior is record-only. First live readback reported `1` host tmux orphan, below threshold `5`.
- 2026-05-27 10:01 CDT: added metadata-only token-usage monitoring to AI Health and Frank's morning report. `scripts/ai_health_check.py` now records `token_usage_check` in `latest.json`, writes `tmp/ai-health-manager/token-usage-checks.jsonl`, includes a `Token Usage` section in `latest.md`, and adds recent Codex session volume to the canonical status line. `frank/scripts/frank_daily_report.py` now adds a separate `Token usage, past 24 hours` section to morning reports from the AI Health latest JSON. First live readback showed `344` Codex session files, `281.77` MB of session transcripts, `803` prompt entries, and status `attention` for the past 24 hours.
- 2026-05-27 12:29 CDT: converted Frank's 08:32 recommendations from report-only health visibility into active fan-out controls. `scripts/task_flow_due_runner.py` now has a Workspaceboard worker-session circuit breaker, max new sessions per run/source, duplicate active `workspaceboard_session` suppression, and overload mode using 1-minute load average plus live tmux session count. Guard events are written to `/Users/admin/.task-flow-launch/state/automation-circuit-breakers.jsonl`. `scripts/ai_health_check.py` now reads that guard log into `task_flow_fanout_guard`, includes it in `latest.json`, `latest.md`, the canonical status line, and management issues when launches are blocked. Validation: Python compile passed for both scripts; due-runner dry run reported zero due items and overload inactive (`load_1m=3.15`, `live_tmux_sessions=16`); AI Health dry run completed and reported `task_flow_fanout_guard=not-recorded`, `blocked=0`, `token_usage_status=attention`, `342` session files, and `285.9` MB over 24h.
