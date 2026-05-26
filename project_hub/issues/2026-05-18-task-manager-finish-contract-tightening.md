# Task Manager Finish Contract Tightening

- Master Incident ID: `AI-INC-20260518-TASK-MANAGER-FINISH-CONTRACT-01`
- Date Opened: 2026-05-18
- Date Completed: 2026-05-18
- Owner: Codex / AI Manager
- Priority: High
- Status: completed

## Scope

Tighten Workspaceboard Task Manager enforcement so routed/working Task Flow rows cannot linger without closeout proof.

## Symptoms

The current DB-backed Task Flow report still showed routed and working rows that were not being treated as unfinished closeout gaps aggressively enough.

## Root Cause

The enforcement layer flagged missing finish contracts and stale proof gaps, but it did not explicitly mark all active routed/working rows without closeout proof as unfinished.

## Repo Logs

### workspaceboard

- Repo Log ID: `task-manager-finish-contract-tightening-workspaceboard-2026-05-18`
- Commit SHA: not committed
- Commit Date: 2026-05-18
- Change Summary:
  - Added an `active_without_closeout_proof` enforcement violation for live routed/working Task Flow rows lacking closeout proof.
  - Preserved the existing dead-session reroute priority while making unfinished active rows surface as proof-repair work.
  - Added a regression test covering the new unfinished active-row rule.

## Verification Notes

- `node --check /Users/werkstatt/workspaceboard/server/index.js`
- `node --test /Users/werkstatt/workspaceboard/server/test/session-status.test.js`

## Rollback Plan

Restore the previous Workspaceboard enforcement logic if the broader proof-gap rule proves too noisy in live Task Flow.

## Follow-Ups

- Sync the live Workspaceboard runtime with the updated `server/index.js`.
- Watch Task Flow report noise after deployment and narrow the rule only if it becomes too broad.
