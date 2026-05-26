# TODO Archive Migration

- Master Incident ID: `AI-INC-20260518-TODO-ARCHIVE-MIGRATION-01`
- Date Opened: 2026-05-18
- Date Completed: 2026-05-18
- Owner: Codex / AI Manager
- Priority: Medium
- Status: completed

## Scope

Archive legacy `TODO.md`, `ToDo.md`, and `ToDo-append.md` surfaces across `/Users/werkstatt` so they no longer function as live queues.

## Symptoms

The workspace still contained markdown TODO and append-queue files that could be mistaken for active task management even after DB-backed task state was established.

## Root Cause

Legacy queue files remained on disk as active-looking projections after the DB-backed Task Flow / OPS / project-hub spine became the authoritative execution source.

## Repo Logs

### ai_workspace

- Repo Log ID: `todo-archive-migration-ai_workspace-2026-05-18`
- Commit SHA: not committed
- Commit Date: 2026-05-18
- Change Summary:
  - Replaced `TODO.md` files under `ai_workspace` workspaces with archive stubs.
  - Replaced `ToDo-append.md` surfaces under `ai_workspace` workspaces with archive stubs.

### ops

- Repo Log ID: `todo-archive-migration-ops-2026-05-18`
- Commit SHA: not committed
- Commit Date: 2026-05-18
- Change Summary:
  - Replaced `TODO.md` and `ToDo-append.md` with archive stubs.

### portal

- Repo Log ID: `todo-archive-migration-portal-2026-05-18`
- Commit SHA: not committed
- Commit Date: 2026-05-18
- Change Summary:
  - Replaced `TODO.md`, `ToDo-append.md`, and the nested MetaModels controller `TODO.md` with archive stubs.

### workspaceboard

- Repo Log ID: `todo-archive-migration-workspaceboard-2026-05-18`
- Commit SHA: not committed
- Commit Date: 2026-05-18
- Change Summary:
  - Replaced `TODO.md` and `ToDo-append.md` with archive stubs.

## Verification Notes

- Verified no active sections remain in the `TODO.md` files touched.
- Verified the `ToDo-append.md` files touched are archive stubs only.

## Rollback Plan

Restore the prior markdown projections from git history if a legacy queue must be temporarily re-enabled.

## Follow-Ups

- Keep new work in DB-backed task records only.
- Do not reintroduce active markdown TODO or append queues.
