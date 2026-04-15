# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260228-TODO-WORKFLOW-01`
- Date Opened: `2026-02-28 15:20:00 CST`
- Date Completed: `2026-02-28 15:34:23 CST`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed`

## Scope
Standardize TODO workflow across active module repos and deploy updates:
- Add/align `AGENTS.md` TODO workflow instructions.
- Ensure `TODO.md`, `ToDo-append.md`, and `TODO-append.md` presence.
- Ensure `.htaccess` blocks direct web access to AGENTS/TODO/append docs where `.htaccess` exists.
- Commit and push module changes, then perform live pulls.

## Symptoms
Workflow handling was inconsistent across modules (missing TODO files, missing append queue, inconsistent AGENTS instructions, uneven `.htaccess` protection).

## Root Cause
Historical drift and per-repo divergence without one enforced template.

## Repo Logs

### ops
- Repo Log ID: `OPS-20260228-TODO-STD-01`
- Commit SHA: `34cbfab`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md`; add standardized TODO workflow section to `AGENTS.md`.

### bid
- Repo Log ID: `BID-20260228-TODO-STD-01`
- Commit SHA: `848a71d`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md` + `ToDo-append.md`; add workflow section in `AGENTS.md`; add `.htaccess` workflow-doc deny rules.

### portal
- Repo Log ID: `PORTAL-20260228-TODO-STD-01`
- Commit SHA: `2afdca04`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md` + `ToDo-append.md`; add standardized workflow section in `AGENTS.md`.

### login
- Repo Log ID: `LOGIN-20260228-TODO-STD-01`
- Commit SHA: `b87b062`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md`; add standardized workflow section in `AGENTS.md`.

### salesreport
- Repo Log ID: `SALESREPORT-20260228-TODO-STD-01`
- Commit SHA: `b5d4a26`
- Commit Date: `2026-02-28`
- Change Summary: Add `ToDo-append.md`; add standardized workflow section in `AGENTS.md`.

### importer
- Repo Log ID: `IMPORTER-20260228-TODO-STD-01`
- Commit SHA: `4d3cbe8`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md` + `ToDo-append.md`; add workflow section in `AGENTS.md`; add `.htaccess` workflow-doc deny rules.

### lists
- Repo Log ID: `LISTS-20260228-TODO-STD-01`
- Commit SHA: `fcd9d53`
- Commit Date: `2026-02-28`
- Change Summary: Add `TODO.md` + `ToDo-append.md`; add standardized workflow section in `AGENTS.md`.

### contactreport
- Repo Log ID: `CONTACTREPORT-20260228-TODO-STD-01`
- Commit SHA: `f26bd68`
- Commit Date: `2026-02-28`
- Change Summary: Add `AGENTS.md`, `TODO.md`, `ToDo-append.md`; add `.htaccess` workflow-doc deny rules.

## Verification Notes
- Local push complete for updated repos.
- Live pull scope excludes `bid` and `portal` (they are deployed elsewhere per operator instruction).
- Live pull complete for: `ops`, `login`, `forge` (no change), `salesreport`, `importer`, `lists`, `contactreport`.

## Rollback Plan
For each updated repo, revert to previous commit SHA and redeploy with `git pull --ff-only` on live host where attached.

## Follow-Ups
1. Keep `bid` and `portal` in a separate deploy runbook reflecting their non-default live location.
2. Consider central reusable AGENTS TODO-workflow snippet or script to prevent drift.
