# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260518-WORKSPACEBOARD-SESSION-STARTUP-01`
- Date Opened: `2026-05-18`
- Date Completed: `2026-05-18`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Repair Workspaceboard live-session startup classification so fresh Codex worker panes do not get marked `finished` and auto-closed before real work begins, then verify the fix against the installed runtime and relaunch a controlled worker batch.

## Symptoms

- AI Manager launched ten visible worker routes, but most disappeared from the live board within minutes.
- Closed-session records showed blank/fast closeouts with no proof summary.
- Fresh live Codex panes were being persisted as `finished` based on reusable composer prompt text instead of actual completion.

## Root Cause

`workspaceboard/server/index.js` treated the reusable Codex composer suggestion as `review-ready` even when a live session had not yet emitted any working, waiting, blocked, or completion marker. That wrote `persisted_status='finished'`, which later triggered the stale-session fast-close path.

## Repo Logs

### workspaceboard

- Repo Log ID: `AI-INC-20260518-WORKSPACEBOARD-SESSION-STARTUP-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-05-18`
- Change Summary:
  - Added a narrow guard in `server/index.js` so a live reusable prompt by itself returns no transcript verdict yet.
  - Added a regression test in `server/test/session-status.test.js` for the live reusable-composer startup case.
  - Copied only the reviewed `server/index.js` into `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js` and restarted only the listener on port `17878`.

### ai_workspace

- Repo Log ID: `AI-INC-20260518-WORKSPACEBOARD-SESSION-STARTUP-01`
- Commit SHA: `uncommitted`
- Commit Date: `2026-05-18`
- Change Summary:
  - Recorded the runtime repair and relaunched worker state in `HANDOFF.md`, `daily-inputs/2026-05-18.md`, and this project-hub note.

## Verification Notes

- `node --check /Users/werkstatt/workspaceboard/server/index.js`
- `node --test /Users/werkstatt/workspaceboard/server/test/session-status.test.js`
  - Passed `64/64`, including the new reusable-prompt startup regression.
- Live smoke worker `9359c1dd`:
  - prompt delivery returned `status=working`, `status_label=working`
  - did not enter `codex-dashboard-closed-session-records.json` as a blank fast-close
  - later closed with proof marker `Smoke pass: overview shows 9359c1dd working/live at 2026-05-18T11:17:24-05:00; node --test server/test/session-status.test.js passed 64/64 including startup/reusable-prompt guards.`
- Controlled relaunch batch stayed live after verification window:
  - `e1179778` National Outreach weekly COT reminder `6147834` follow-through
  - `684811bc` AI Workspace weekly COT follow-through guidance update
  - `f7035d75` Workspaceboard Task Flow blank field sweep
  - `90f9148a` National Outreach recurring-ops hygiene pass

## Rollback Plan

- Restore `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js` from `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js.bak-live-reusable-prompt-20260518-111442`.
- Restart only the Workspaceboard node listener on port `17878` and recheck `/api/status`.

## Follow-Ups

- Watch the four relaunched workers for real proof or exact blockers before opening a larger replacement batch.
- If the remaining failed May 18 lanes need to be relaunched, do them in verified waves instead of one blind burst.
