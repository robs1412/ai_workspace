# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260407-MEMPALACE-SALESREPORT-01
- Date Opened: 2026-04-07 08:31:40 CDT
- Date Completed: 2026-04-12
- Owner: Codex
- Priority: Medium
- Status: Completed

## Scope

- Evaluate MemPalace as a local memory layer for current `salesreport` work.
- Keep the pilot scoped to one active repo instead of mining all workspaces or all chat history.
- Log setup decisions and initial retrieval results in the policy hub.

## Symptoms

- Current project context is spread across PHP files, specs, and workflow notes.
- Architectural decisions and implementation rationale are searchable only by manual repo grep.
- We want to test whether a local memory/index layer improves recall on active work without adding cloud services.

## Root Cause

- No persistent repo-local semantic memory layer is currently wired into the workflow.
- Existing project context lives in source and markdown docs, but not in a retrieval-oriented structure.

## Repo Logs

### ai_workspace

- Repo Log ID: AI-INC-20260407-MEMPALACE-SALESREPORT-01-AI
- Commit SHA:
- Commit Date:
- Change Summary:
  - Installed MemPalace into a workspace-local virtualenv at `.venvs/mempalace`.
  - Cloned the upstream repo into `external/mempalace`.
  - Patched the local editable MemPalace clone to index `.php` files for PHP-heavy repos.
  - Added this project-hub log and index entry for the pilot.

### salesreport

- Repo Log ID: AI-INC-20260407-MEMPALACE-SALESREPORT-01-SALES
- Commit SHA:
- Commit Date:
- Change Summary:
  - Prepare a local-only MemPalace pilot for current `salesreport` work.
  - Keep generated MemPalace artifacts excluded from normal git status.
  - Indexed a scoped source set for current report-automation and hitlist-optimization files first.
  - Added helper/docs commit `a6b13de` temporarily, then removed those tracked files in follow-up commit `ad1a2d2` so live pulls do not bring MemPalace operator helpers onto the server.

## Verification Notes

- Workspace-local install verified with:
  - `.venvs/mempalace/bin/mempalace --help`
- Throwaway smoke test already succeeded against a temporary sample corpus in `ai_workspace/tmp`.
- Scoped `salesreport` corpus initialized at `salesreport/.mempalace/`.
- Local pilot source set currently includes:
  - `Report-Automation-Spec.md`
  - `Hitlist-Optimization-Technical-Plan.md`
  - `Hitlist-Optimization-Workflow.md`
  - `saved_reports.php`
  - `saved_reports_shared.php`
  - `hitlist_optimization.php`
  - `hitlist_optimization_shared.php`
- Initial finding:
  - upstream MemPalace did not index `.php` files, so the pilot under-indexed implementation files until the local editable clone was patched
- Current pilot result:
  - 8 scoped source files present
  - 235 drawers indexed after the PHP patch
  - retrieval returns both spec-level and implementation-level matches
- Expanded pilot result:
  - full mirrored source corpus built at `salesreport/.mempalace/full-src`
  - source scope excludes `.git`, `.mempalace`, imports/logs noise, `.env`, and the large invoice CSV
  - current mirrored corpus size: 137 files
  - full corpus indexed into `salesreport/.mempalace/full-palace`
  - current full-corpus status after taxonomy cleanup is in the low hundreds and continues to vary during rebuild validation
- Retrieval observations after expansion:
  - focused queries tied to existing feature names/pages return useful matches
  - broad semantic queries across unrelated domains are more mixed than the narrow pilot
  - entity detection remains noisy on this PHP repo, so it should not be treated as authoritative taxonomy without manual cleanup
- Additional setup completed:
  - moved operator-only helper workflow out of `salesreport` repo and into `ai_workspace`
  - active local helper paths now:
    - `ai_workspace/scripts/salesreport_mempalace_search.sh`
    - `ai_workspace/scripts/salesreport_mempalace_reindex.sh`
    - `ai_workspace/salesreport-mempalace.md`
  - added manual room taxonomy for `salesreport` domains:
    - saved reports
    - hitlist optimization
    - national sales agent
    - inventory
    - warehouse reporting
    - barrel program
    - KPI/digest
    - goals/performance
    - shared UI/selects
    - docs/ops
  - registered Codex MCP server `mempalace-salesreport` in `~/.codex/config.toml`
- Current caveat:
  - `saved_reports` routing is still weaker than expected in the expanded corpus and needs another pass if this area becomes the primary usage target
- Git state:
  - `salesreport` remains clean because `mempalace.yaml` and `.mempalace/` artifacts are excluded locally via `.git/info/exclude`
  - live-deploy-safe path restored: MemPalace helper scripts/docs are no longer tracked in `salesreport`

## Rollback Plan

- Remove local MemPalace output directories and repo-local excludes.
- Delete `mempalace.yaml` from `salesreport` if the pilot is not kept.
- Remove the project-hub open entry if the pilot is abandoned.

## Follow-Ups

- Closed by Robert decision on 2026-04-12: do not expand the local Salesreport MemPalace pilot.
- Future memory/retrieval experiments should stay in AI Workspace or a deliberate cross-repo tool, not as ad hoc Salesreport repo-local scripts.
