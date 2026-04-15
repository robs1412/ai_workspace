# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-WERKSTATT-PATHS-01`
- Date Opened: `2026-04-09 09:09:28 CDT`
- Date Completed:
- Owner: `Codex`
- Priority: `High`
- Status: `Open`

## Scope

- Unify local repo roots across Mac mini and MacBook under `/Users/werkstatt`.
- Stop treating `/Applications/MAMP/htdocs` as the primary workspace root.
- Update shared path resolution in `ai_workspace`, shell launchers, and `workspaceboard`.
- Keep this migration focused on local developer/workspace paths, not live-server deployment paths.

## Symptoms

- Mac mini and MacBook currently resolve workspaces from a mix of `/Users/*/Documents/GitHub` and `/Applications/MAMP/htdocs`.
- Some workspaces have dual-path behavior, which creates confusion in `ws`, board launches, and repo-local assumptions.
- `workspaceboard` has already shown that divergent roots and first-run prompts can break session management.

## Root Cause

- Historical module locations were kept under `/Applications/MAMP/htdocs`, while newer git-managed repos and board code moved toward clone-based paths.
- The shared launcher/docs evolved to support both layouts instead of enforcing one canonical root.
- GitHub Desktop, Transmit, localhost Apache docroots, and `ws()` launchers were all still carrying machine-specific path assumptions.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-20260409-WERKSTATT-01`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Track the cross-machine repo-root migration and path-resolution updates.

### workspaceboard

- Repo Log ID: `WORKSPACEBOARD-20260409-WERKSTATT-01`
- Commit SHA:
- Commit Date:
- Change Summary:
  - Update board workspace path resolution to prefer the new `Documents/werkstatt` roots.

## Verification Notes

- Mac mini current state:
  - canonical local roots now resolve from `/Users/werkstatt/<repo>`
  - `http://localhost/workspaceboard/` returns `200 OK`
  - `/Users/admin/Documents/GitHub` is now a single bridge symlink to `/Users/werkstatt`
- MacBook current state:
  - active module paths resolve from `/Users/werkstatt/<repo>`
  - `/Applications/MAMP/htdocs/<module>` bridge symlinks now point to `/Users/werkstatt/<module>`
- Migration target:
  - `/Users/werkstatt/<repo>` as the canonical local repo root

## 2026-04-09 Update

- Confirmed all main local repos now exist under `/Users/werkstatt`: `ops`, `portal`, `login`, `forge`, `salesreport`, `importer`, `lists`, `bid`, `workspaceboard`, `contactreport`, `eventmanagement`, `donations`, `braincloud`.
- Verified the latest AI Workspace Task Manager session was still the older coordinator session `5909d11e`; its history already contains the routed follow-up instruction to continue coordination before the next `/login` task.
- Updated AI Workspace policy/mapping guidance to treat `/Users/werkstatt/<repo>` as canonical and old `Documents/GitHub` or `/Applications/MAMP/htdocs` paths as migration-time compatibility only.
- Updated GitHub Desktop and Transmit shortcuts on both machines to pick up `/Users/werkstatt` paths.
- Updated `~/.bashrc` `ws()` launchers on both machines so module workspaces and `braincloud` resolve from `/Users/werkstatt`.
- Moved the top-level compatibility symlinks `2026_workspace_sync`, `ertc_workspace`, and `robert_workspace` under `/Users/werkstatt`, then re-pointed the local MAMP bridge links to those new locations.

## Rollback Plan

- Keep timestamped backups of moved roots where needed before destructive renames.
- Verify each repo path after move before deleting any old compatibility path.
- If a specific workspace fails after migration, temporarily point `ws` and `workspaceboard` back to the last known-good path while preserving the moved repo.

## Follow-Ups

- Update `~/.bashrc` `ws()` mapping on both machines.
- Update `workspaceboard` path maps and reinstall its LaunchAgent/runtime on both machines.
- Update the AI Workspace policy notes to describe `Documents/werkstatt` as the canonical repo root.
