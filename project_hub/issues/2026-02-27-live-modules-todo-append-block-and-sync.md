# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260227-LIVE-MODULES-02
- Date Opened: 2026-02-27
- Date Completed: 2026-02-27
- Owner: Codex + Robert
- Priority: High
- Status: Completed

## Scope

- Multi-repo commit/push/live-pull cycle.
- Ensure `ToDo-append` files are not web-accessible on live modules.
- Process `lists/template-add.html` into DB template storage, then remove source file.
- Normalize `.DS_Store` ignore behavior across active module repos.

## Symptoms

- `ToDo-append.md` existed in live module paths (`forge`, `login`) and needed web access blocked.
- Template source file existed in `lists` repo and needed DB import + cleanup.
- Untracked `.DS_Store` files recurring in multiple repos.

## Root Cause

- No global web deny rule for `ToDo-append*`.
- One-off template handoff file was left in repo root.
- `.DS_Store` ignore was inconsistent across module `.gitignore` files.

## Repo Logs

### forge

- Repo Log ID: FORGE-20260227-PLANNER-PHLIST
- Commit SHA: `daaccf8`
- Commit Date: 2026-02-27
- Change Summary: Planner stale-audience handling, linked audience refresh, PHPList sync/count improvements, UI updates.

- Repo Log ID: FORGE-20260227-DSSTORE
- Commit SHA: `dd0fea3`
- Commit Date: 2026-02-27
- Change Summary: Added `.DS_Store` ignore.

### importer

- Repo Log ID: IMPORTER-20260227-ROBUST-SYNC
- Commit SHA: `dbad83e`
- Commit Date: 2026-02-27
- Change Summary: Import robustness updates (account/contact linking, `account_no` support).

- Repo Log ID: IMPORTER-20260227-DSSTORE
- Commit SHA: `4136201`
- Commit Date: 2026-02-27
- Change Summary: Added `.DS_Store` ignore.

### lists

- Repo Log ID: LISTS-20260227-TEMPLATE-ASSET
- Commit SHA: `2252e65`
- Commit Date: 2026-02-27
- Change Summary: Added `template-add.html` source asset.

- Repo Log ID: LISTS-20260227-TEMPLATE-CLEANUP
- Commit SHA: `340acb4`
- Commit Date: 2026-02-27
- Change Summary: Removed `template-add.html` after DB import, added `.DS_Store` ignore.

### ops

- Repo Log ID: OPS-20260227-AGENTS-WORKFLOW
- Commit SHA: `273a17f`
- Commit Date: 2026-02-27
- Change Summary: AGENTS workflow clarification (commit/test before push/live pull).

### portal

- Repo Log ID: PORTAL-20260227-DSSTORE
- Commit SHA: `98174db3`
- Commit Date: 2026-02-27
- Change Summary: Added `.DS_Store` ignore.

## Verification Notes

- Live root `.htaccess` updated with deny rule:
  - `<FilesMatch "(?i)^todo-append(\\..*)?$"> Deny from all </FilesMatch>`
- HTTP verification (all returned `404`):
  - `/forge/ToDo-append.md`
  - `/login/ToDo-append.md`
  - `/importer/ToDo-append.md`
  - `/lists/ToDo-append.md`
  - `/ops/ToDo-append.md`
- `lists/template-add.html` inserted into DB:
  - `phplist_template.id = 77`
  - title: `Noelle O'Saben Explores When Friction Aides Creation`

## Rollback Plan

- Revert specific repo commits and redeploy via standard git pull workflow.
- Restore previous live root `.htaccess` from timestamped backup if needed.

## Follow-Ups

- Optional: set upstream tracking on live `importer`, `lists`, and `contactreport` to avoid explicit branch pulls.
- Optional: add centralized deny for other workspace note filenames (`TODO*.md`, `AGENTS.md`) on live.
