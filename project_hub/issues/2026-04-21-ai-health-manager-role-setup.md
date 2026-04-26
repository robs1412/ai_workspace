# AI Health Manager Role Setup

- Master Incident ID: `AI-INC-20260421-AI-HEALTH-MANAGER-ROLE-SETUP-01`
- Date Opened: 2026-04-21 CDT
- Date Completed: 2026-04-21 CDT
- Owner: AI Workspace / Task Manager
- Priority: Medium
- Status: Completed

## Scope

Robert approved installing an AI Health Manager role and adding it to the organigram. The role monitors AI Workspace board/session health, identifies stale sessions, safely nudges visible stale workers when Task Manager has not acted, verifies standing monitors, and watches Task Manager, Frank, Avignon, and future email workers.

Visible AI Workspace sessions seen during closeout:

- `c4a31aeb` / `AI Health Manager role and organigram setup` / `working` + `live`;
- `a3b9518c` / `AI Health Manager setup verification` / `working` + `live`.

Approved scope for this slice:

- create the role definition;
- register the role in AI Workspace role docs and operating model;
- add the role to the Workspaceboard organigram source/feed;
- record TODO/HANDOFF/project state;
- document the future 15-minute cadence target without activating any live scheduler.

## Symptoms

Robert wanted a dedicated worker to check whether other sessions are stale or unhealthy, kickstart safe stale work, and ensure Frank, Avignon, Task Manager, and other email workers remain healthy.

## Root Cause

Health/liveness review was previously implicit in Task Manager, Decision Driver, Summary Worker, and ad hoc checks. There was no dedicated role doc or organigram entry for operational health checks, stale-session classification, duplicate nudge tracking, or stricter standing-monitor liveness expectations.

## Repo Logs

### ai_workspace

- Repo Log ID: `ai-health-manager-role-docs-20260421`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary: Added `worker_roles/ai-health-manager.md`; updated role README and operating-model registration; recorded TODO/HANDOFF/project-hub state.

### workspaceboard

- Repo Log ID: `ai-health-manager-organigram-source-20260421`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary: Added `AI Health Manager` to `worker-organigram.php` role feed so Workspaceboard can display the new role from the AI Workspace `worker_roles` source.

## Operating Rules Recorded

- Default cadence target is every 15 minutes if/when activated.
- No live scheduler, daemon, LaunchAgent, runtime cadence, service restart, or polling process was activated.
- Health Manager checks and reports; it does not implement business work.
- It may inspect `/api/status`, visible session metadata/history, TODO/HANDOFF metadata, role docs, project-hub notes, and approved non-secret logs.
- It may prompt a stale visible worker once with a focused continuation when the next step is obvious and safe.
- It records last nudge/session id/time/reason to avoid duplicate nudges.
- It distinguishes stale-but-safe-to-nudge from waiting-on-human, review-ready, blocked, and standing-monitor states.
- It must not close standing monitors, mutate mailboxes, send emails, start or alter daemons/LaunchAgents/services/schedulers, commit/push/deploy/reset/clean, expose secrets, touch OAuth/auth/Keychain, or mutate production.
- Any 15-minute scheduled activation requires a separate Code/Git Manager and Security Guard reviewed implementation slice.

## Verification Notes

- Read current TODO/HANDOFF, append queue, role docs, operating model, project-hub index, and Workspaceboard organigram source.
- Checked both `ai_workspace` and `workspaceboard` worktrees before editing; both already had unrelated dirty files.
- Planned checks: Markdown/source text search, `php -l /Users/werkstatt/workspaceboard/worker-organigram.php`, and `git diff --check` on touched repos.

## Rollback Plan

If Robert rejects the role, remove `worker_roles/ai-health-manager.md`, remove the role from `worker_roles/README.md`, `worker_roles/operating-model.md`, `TODO.md`, `HANDOFF.md`, `project_hub/INDEX.md`, this project note, and remove the `ai-health-manager` entry from `/Users/werkstatt/workspaceboard/worker-organigram.php`. Do not reset or clean unrelated dirty files.

## Follow-Ups

- Task Manager may create a visible `AI Health Manager` session for manual/on-demand checks.
- A 15-minute scheduled monitor remains a future approval-gated implementation slice requiring Code/Git Manager and Security Guard review.
