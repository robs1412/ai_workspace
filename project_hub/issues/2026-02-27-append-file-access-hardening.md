# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260227-APPEND-LOCKDOWN-01
- Date Opened: 2026-02-27
- Date Completed: 2026-02-27
- Owner: Codex + Robert
- Priority: Medium
- Status: Completed

## Scope

- Ensure `ToDo-append.md`/`TODO-append.md` are blocked from direct web access in OPS and related modules with append queues.
- Validate current localhost behavior for OPS/login/bid paths.

## Symptoms

- OPS had append queue files present and the existing root `.htaccess` deny list did not include append filenames.
- Other modules had similar internal-doc allow/deny rules but missing append filenames.
- `bid` MAMP path had append files and no root `.htaccess`.

## Root Cause

- Internal-doc deny lists were standardized around `AGENTS.md`/`TODO.md` but were not extended to include append queue files.
- One active module path (`/Applications/MAMP/htdocs/bid`) lacked root access-control rules.

## Repo Logs

### ops

- Repo Log ID: OPS-20260227-APPEND-LOCKDOWN
- Commit SHA: `5bc6f41` (HEAD before new commit)
- Commit Date: 2026-02-27
- Change Summary: Extended internal-doc deny rule to include `ToDo-append.md` and `TODO-append.md`.

### login

- Repo Log ID: LOGIN-20260227-APPEND-LOCKDOWN
- Commit SHA: `ba1ef7f` (HEAD before new commit)
- Commit Date: 2026-02-27
- Change Summary: Extended both Apache 2.4 and legacy deny blocks for append filenames.

### forge

- Repo Log ID: FORGE-20260227-APPEND-LOCKDOWN
- Commit SHA: `dd0fea3` (HEAD before new commit)
- Commit Date: 2026-02-27
- Change Summary: Extended internal-doc deny rule to include append filenames.

### salesreport

- Repo Log ID: SALESREPORT-20260227-APPEND-LOCKDOWN
- Commit SHA: `616b9d1` (HEAD before new commit)
- Commit Date: 2026-02-27
- Change Summary: Extended internal-doc deny rule to include append filenames.

### lists

- Repo Log ID: LISTS-20260227-APPEND-LOCKDOWN
- Commit SHA: `340acb4` (HEAD before new commit)
- Commit Date: 2026-02-27
- Change Summary: Extended internal-doc deny rule to include append filenames.

### bid (MAMP path, non-git)

- Repo Log ID: BID-20260227-APPEND-LOCKDOWN
- Commit SHA: n/a (path is not a git working tree)
- Commit Date: 2026-02-27
- Change Summary: Added new root `.htaccess` with internal-doc deny rules including append filenames.

## Verification Notes

- Local HTTP checks:
  - `http://localhost/ops/ToDo-append.md` -> `403`
  - `http://localhost/ops/TODO-append.md` -> `403`
  - `http://localhost/login/ToDo-append.md` -> `403`
  - `http://localhost/bid/ToDo-append.md` -> `404` (not served directly)
- File-level checks confirmed append filename deny patterns exist in updated `.htaccess` files.

## Rollback Plan

- Revert `.htaccess` edits in affected repos/paths.
- Re-test the same localhost URLs.

## Follow-Ups

- After commits/pushes, run live `git pull --ff-only` only on explicit approval.
- Optionally add a shared baseline deny include for all modules to avoid per-repo drift.
