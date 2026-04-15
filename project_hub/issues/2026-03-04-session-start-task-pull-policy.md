# 2026-03-04-session-start-task-pull-policy.md

- Master Incident ID: `AI-INC-20260304-TASK-PULL-POLICY-01`
- Date Opened: `2026-03-04 12:35:00 CST`
- Date Completed: `2026-03-04 12:51:42 CST`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed`

## Scope

Replace background 5-minute task polling with one-shot OPS task intake at session start, and propagate this policy across module `AGENTS.md` files.

## Symptoms

- Open task `362555` requested automated polling.
- Team concern: persistent terminal background poll loop is unnecessary and brittle.

## Root Cause

No explicit cross-module policy existed to define one-shot intake versus continuous polling.

## Repo Logs

### ops

- Repo Log ID: `OPS-20260304-TASK-PULL-POLICY`
- Commit SHA: `06eabc8`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`, updated TODO queue state, removed task from append queue.

### lists

- Repo Log ID: `LISTS-20260304-TASK-PULL-POLICY`
- Commit SHA: `4af82c6`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

### login

- Repo Log ID: `LOGIN-20260304-TASK-PULL-POLICY`
- Commit SHA: `757c0b1`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

### forge

- Repo Log ID: `FORGE-20260304-TASK-PULL-POLICY`
- Commit SHA: `ad64cbe`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `agents.md`.

### salesreport

- Repo Log ID: `SALESREPORT-20260304-TASK-PULL-POLICY`
- Commit SHA: `b635858`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

### importer

- Repo Log ID: `IMPORTER-20260304-TASK-PULL-POLICY`
- Commit SHA: `b0fbaec`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

### bid

- Repo Log ID: `BID-20260304-TASK-PULL-POLICY`
- Commit SHA: `947ba90`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

### contactreport

- Repo Log ID: `CONTACTREPORT-20260304-TASK-PULL-POLICY`
- Commit SHA: `3acc387`
- Commit Date: `2026-03-04`
- Change Summary: Added session-start one-shot pull policy to `AGENTS.md`.

## Verification Notes

- Confirmed policy text exists in all targeted module AGENTS files.
- Confirmed OPS task `362555` status updated to `Completed`.
- Confirmed OPS live server updated to latest commit `06eabc8`.

## Rollback Plan

- Revert AGENTS policy commits in affected repos.
- Restore previous TODO/append state in OPS if needed.
- Re-open OPS task `362555` if policy direction changes.

## Follow-Ups

- None required; policy now standardized.
