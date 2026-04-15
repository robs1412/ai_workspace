# AI Workstation And Sync Transition

Master ID: `AI-INC-20260412-AI-WORKSTATION-SYNC-01`
Status: planning approved / 2026-04-14 audit completed / legacy dashboard deleted / M4 board smoke complete
Opened: 2026-04-12
Owner: Robert / Decision Driver

## Summary

Robert approved the near-term direction for the AI workstation setup. Daily workstation activity should move to the Mac Mini M4 2025. The 2018 Mac mini should remain the macOS AI server for now because its 64GB RAM is valuable for concurrent Codex workers and Workspaceboard. Linux on the 2018 Mac mini is a later pilot, not part of the immediate transition.

Detailed plan: `../../AI_WORKSTATION_SYNC_PLAN.md`

AI-Bridge cross-link: `/Users/werkstatt/ai-bridge/WORKSTATION-SYNC-DECISION.md`

## Decision Record

- M4 becomes Robert's daily workstation.
- 2018 Mac mini remains the canonical macOS AI server during the transition.
- MacBook Pro 2019 becomes portable fallback/client, not a second live writer for the same workspaces.
- Raetan/Claude remains server-side analysis/planning support.
- Google Drive `ai_workspace` remains shared planning/intake memory.
- `/Users/werkstatt/<repo>` remains canonical for code and implementation work.
- Git is the default code sync path.
- SSH/rsync is for deliberate handoff artifacts, not constant bidirectional workspace sync.
- Runtime state and secrets remain machine-local.

## Migration Boundary

Keep in Google Drive `ai_workspace`:

- policy, role docs, TODOs, handoffs, project hub notes, append-only intake, non-secret Frank/Avignon planning records

Move or keep in `/Users/werkstatt` repos:

- code, tests, module docs, repo-local TODOs, Workspaceboard source, implementation artifacts that belong with source

Use git-only by default:

- source and deterministic repo changes that need to move across M4, Mac mini, and MacBook

Use SSH/rsync/handoff:

- deliberate non-git transfers, large generated files, or one-time machine handoff packages

Keep machine-local:

- LaunchAgents, installed runtime copies, tmux/session state, caches, dependencies, non-audit logs, secrets, SSH private keys, keychain/OAuth material, `.env` files, and live mailbox automation credentials

## Remaining Follow-Up

- Decide whether M4 should remain a manual/local board control surface or become a formal failover board host.
- Step 4: migrate `ws ai` away from Google Drive into a git-backed `/Users/werkstatt/ai_workspace` coordination repo, after separating secrets/runtime/generated material.
- Review migration/cleanup candidates from the 2026-04-14 audit one-by-one: `screenbox`, `external/mempalace`, `htdocs`, local environment/cache/temp folders, duplicate role-doc folders, recordings/log folders, and `scripts`.
- Private credential storage is explicitly out of scope for ad hoc movement; handle it only through approved credential procedures.

## 2026-04-14 AI Workspace Audit Result

Initial docs-only audit completed from `ai_workspace`; at that point no files were moved, deleted, or sync behavior changed. Robert later approved deleting the legacy dashboard copy; see the deletion record below.

Original recommendation before deletion approval: mark `ai_workspace/codex_dashboard` legacy/read-only. `/Users/werkstatt/workspaceboard` is the active source of truth: it is a git repo with remote `git@github.com:robs1412/workspaceboard.git`, current checked commit `e4e9f0c`, richer/current UI surfaces including task management, phone page, remote access docs, and server `BOARD_VERSION` `0.69`. The older `ai_workspace/codex_dashboard` copy had no local git metadata, last observed non-dependency edits on 2026-04-08, server package version `1.0.0`, legacy workspace path fallbacks to `Documents/GitHub`/MAMP roots, and bundled `server/node_modules` under the Google Drive tree.

Audit categories:

- Keep in `ai_workspace`: policy and coordination docs, `TODO.md`, `ToDo-append.md`, `HANDOFF.md`, `worker_roles/`, `project_hub/`, non-secret Frank/Avignon planning records, and small intentional audit records.
- Move to `/Users/werkstatt` or git-managed repo if still active: `screenbox` and `external/mempalace` are embedded git/code clones under Drive. `screenbox` tracks `https://github.com/dklymentiev/screenbox`; `external/mempalace` tracks `https://github.com/milla-jovovich/mempalace.git` and currently has local modifications in `mempalace/entity_detector.py` and `mempalace/miner.py`, so it needs a deliberate commit/stash/handoff before any relocation.
- Treat as machine-local or cleanup candidates after approval: `.venv_pdf`, `.venvs/`, `.playwright-cli/`, `scripts/__pycache__/`, `tmp/`, `tmp-staging/`, `tmp_il_report/`, and `screenbox/.pytest_cache/`. The former `codex_dashboard/server/node_modules/` was removed as part of the deleted legacy dashboard tree.
- Treat as generated or audit artifacts requiring retention decision: `LOG_imapsync/`, `recordings/`, `output/`, and `sync_backups/`. `output/portal-account-passwords-2026-03-27.md` is credential-looking by name and must not be printed; review through the approved secret-handling path before moving or deleting.
- Review before changing: `scripts/` is mixed. Frank/Avignon automation and planning helpers may belong in `ai_workspace`, while Workspaceboard launcher scripts now belong with `/Users/werkstatt/workspaceboard` and installed runtime copies remain machine-local.
- Duplicate review: `worker_roles (1)/` appears older than `worker_roles/`; the canonical `worker_roles/` has additional current docs (`code-and-git-manager.md`, `operating-model.md`, `outreach-coordinator.md`). Do not remove the duplicate until a content diff confirms no unique retained notes.
- Secret boundary: `.env`, `.env.md`, `.private/`, `screenbox/.env`, and similarly named credential files must remain out of normal doc/chat handling. No secret contents were read or printed during this audit.

Next recommended cleanup pass, with explicit approval: decide one-by-one whether `screenbox`, `external/mempalace`, generated output/logs, duplicate role docs, and temp/runtime folders should be migrated, archived, or removed.

## 2026-04-14 Legacy Codex Dashboard Deletion

Robert instructed that the legacy dashboard copy should be deleted rather than kept as read-only history. Checked the target first as a destructive operation.

Deleted only: `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/codex_dashboard`.

Reasoning: the removed path was the synced legacy source copy, 14 MB, no local `.git`, last observed as older than `/Users/werkstatt/workspaceboard`, and had no open file handles. Active Workspaceboard remained served from the machine-local runtime `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js`, backed by source repo `/Users/werkstatt/workspaceboard`; `http://127.0.0.1:17878/api/status` returned `ok: true`, `board_version` `0.69`, host `Macmini.lan` after deletion.

Intentionally left in place: `/Users/werkstatt/workspaceboard`, `/Users/admin/.workspaceboard-launch`, `/Users/admin/.codex-dashboard-launch`, `/Users/admin/Library/LaunchAgents/com.koval.workspaceboard.plist`, `/Users/admin/Library/LaunchAgents/com.koval.codex-dashboard.plist`, `ai_workspace/scripts/*`, and dashboard logs/state under `ai_workspace/tmp/`. The old `com.koval.codex-dashboard` LaunchAgent plist exists but was not loaded by `launchctl print`; it and the old runtime copy were left untouched because this task was scoped to deleting the legacy synced source directory only.

## 2026-04-15 M4 Workspaceboard Runtime Smoke

Robert confirmed M4 already has Mimestream, Evernote, Codex, npm, Homebrew, Google Drive, and werkstatt repos. The setup pass therefore focused on verifying and wiring the already-present M4 runtime pieces rather than installing user apps.

Verified from `Macmini.lan` over the approved Mac mini -> M4 SSH key path:

- M4 identity remains `Mac.lan` at `192.168.55.35`, user `kovaladmin`, home `/Users/kovaladmin`.
- Homebrew Node is available at `/opt/homebrew/bin/node` and `/opt/homebrew/opt/node/bin/node`, version `v25.9.0`.
- npm is available through Homebrew PATH, version `11.12.1`.
- Codex CLI is available through Homebrew PATH, version `0.120.0`.
- Workspace repos are under `/Users/kovaladmin/werkstatt`, not `/Users/werkstatt`.

Workspaceboard M4 runtime actions:

- Preserved the pre-sync M4 workspaceboard local dirty state as git stash `m4-pre-workspaceboard-sync-20260415-093752`.
- Reset the M4 `workspaceboard` repo to Mac mini `origin/main`, then later updated it to commit `a9833a3`.
- Installed LaunchAgent `com.koval.workspaceboard` for `kovaladmin`.
- Initial launch failed because launchd had `com.koval.workspaceboard` marked disabled in the `gui/501` domain. Enabled only that service, then re-ran the installer successfully.
- Verified `http://127.0.0.1:17878/api/status` on the M4 returns `ok: true`, `board_version: 0.69`, and host `Mac.lan`.
- After Google Drive hydrated the project files, verified `http://127.0.0.1:17878/api/digital-office-index` on the M4 returns `63` projects, `25` work items, `61` events, and `61` project-hub artifacts. Papers metadata remains `0` there because no Papers snapshot was installed on the M4.

Workspaceboard source follow-up completed:

- Commit `a9833a3` in `/Users/werkstatt/workspaceboard` adds M4 path fallbacks for `/Users/kovaladmin/Library/CloudStorage/.../ai_workspace` and `/Users/kovaladmin/werkstatt/<repo>`.
- The same commit updates Project Management append-queue indexing labels so they are not hard-coded to `/Users/werkstatt`.
- Commit `a9833a3` was pushed to GitHub and installed into the M4 runtime.

Current caution:

- GitHub fetch from the M4 clone failed before this pass because the GitHub host key was not yet trusted there. The Mac mini remote path `admin-macmini:/Users/werkstatt/workspaceboard` did work for this sync.

## 2026-04-15 M4 `/Users/werkstatt` And GitHub Remote Alignment

Robert created `/Users/werkstatt` on the M4. The existing clones were moved from `/Users/kovaladmin/werkstatt` into `/Users/werkstatt`, then `/Users/kovaladmin/werkstatt` was replaced with a compatibility symlink to `/Users/werkstatt`.

Workspaceboard was reinstalled from `/Users/werkstatt/workspaceboard`; the M4 LaunchAgent `com.koval.workspaceboard` is running and `http://127.0.0.1:17878/api/status` returns `ok: true`, `board_version: 0.69`, host `Mac.lan`. The important workspace paths now resolve to `/Users/werkstatt/<repo>`.

GitHub SSH setup:

- Created dedicated local M4 GitHub SSH key `~/.ssh/id_ed25519_github_robs1412`.
- Public fingerprint: `SHA256:jxIhzrI8ifFDsmyoj/fyCF5AfWbsXl7QkplxHFDpT+A`.
- Configured M4 `~/.ssh/config` `Host github.com` to use that key.
- Copied the public key to the M4 clipboard for GitHub account registration.
- Robert added the public key to GitHub; `ssh -T git@github.com` now authenticates as `robs1412`.

Repo remote alignment:

- GitHub-backed repos now use `origin=git@github.com:robs1412/<repo>.git`.
- The prior Mac mini remote is preserved as `macmini=admin-macmini:/Users/werkstatt/<repo>` where it existed.
- GitLab-backed repos and local-only repos were left unchanged.
- Dry-run fetch checks through `origin` worked for `workspaceboard`, `ops`, `portal`, `salesreport`, `lists`, and `login`.
- `lists/TODO.md` and `login/logs/auth_flow.log` were already dirty locally and were left untouched.

GitHub Desktop state:

- GitHub Desktop is signed in as `robs1412`.
- GitHub Desktop accepted 20 local GitHub-backed repos under `/Users/werkstatt`: `workspaceboard`, `ops`, `portal`, `salesreport`, `lists`, `login`, `forge`, `bid`, `importer`, `donations`, `eventmanagement`, `contactreport`, `database`, `newsite`, `playwright-scraper`, `rezepte`, `automation`, `automation_files`, `Gmailconnector`, `_birnecker.com`, and `braincloud`.
- Existing dirty local states visible after import: `lists` dirty `1`, `login` dirty `1`, `forge` dirty `3`, and `braincloud` dirty `10`. These were not changed or cleaned.

Git alignment follow-up:

- Mac mini and M4 have the same 25 repo names under `/Users/werkstatt`.
- All 25 repo HEAD commits now match between Mac mini and M4.
- M4 `lists`, `login`, and `salesreport` were fast-forwarded to the Mac mini/GitHub commits.
- Prior M4 local changes in `lists` and `login` were preserved as stashes `m4-pre-git-align-20260415-lists` and `m4-pre-git-align-20260415-login`.
- Remaining differences are local dirt only: Mac mini has dirty `lists` and `ops`; M4 is clean for those after alignment. Existing non-transition dirt in `ai-bridge`, `braincloud`, `forge`, and `robert_workspace` remains outside this alignment pass.

## 2026-04-15 Transition Step 2 Backend Check

The 2018 Mac mini remains the backend/canonical worker host during this transition.

Verified on `Macmini.lan`:

- Workspaceboard LaunchAgent `com.koval.workspaceboard` is running on port `17878`.
- `http://127.0.0.1:17878/api/status` returns `ok: true`, `board_version: 0.69`, host `Macmini.lan`, and `26` managed sessions.
- Frank LaunchAgent `com.koval.frank-auto` is loaded on a 300-second interval with last exit code `0`.
- Avignon LaunchAgent `com.koval.avignon-auto` is loaded on a 300-second interval with last exit code `0`.

Verified on M4 `Mac.lan`:

- M4 Workspaceboard LaunchAgent `com.koval.workspaceboard` is running as a local board/control surface.
- M4 does not have Frank or Avignon LaunchAgents loaded.
- M4 `/api/status` returns `ok: true`, `board_version: 0.69`, host `Mac.lan`.

Conclusion: M4 is ready as a foreground workstation/control surface, while Mac mini remains the backend worker/automation host.

## 2026-04-15 Transition Step 3 Google Drive Check

Google Drive is active on both Mac mini and M4 for the AI Workspace planning layer.

Verified matching SHA-256 hashes between Mac mini and M4 for:

- `AGENTS.md`
- `HANDOFF.md`
- `TODO.md`
- `ToDo-append.md`
- `project_hub/INDEX.md`
- `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md`

Boundary check:

- Code and implementation repos remain outside Drive under `/Users/werkstatt/<repo>`.
- Installed runtime copies remain machine-local, including `~/.workspaceboard-launch`, `~/.frank-launch`, and `~/.avignon-launch`.
- Drive `ai_workspace` still contains cleanup/retention candidates: `.env`, `screenbox/.env`, `.venv_pdf`, `.venvs`, `tmp`, and `tmp-staging`.
- Secret-looking files were not read. These should be handled only in step 4 after an explicit folder-limits decision.

Conclusion: Google Drive is correctly acting as the shared planning/handoff layer, not the code/runtime source of truth. Step 4 should define and enforce the AI folder limits so Drive does not keep accumulating runtime, cache, generated, or secret-adjacent material.

## 2026-04-15 Step 4 Proposed Direction: Replace Google Drive Sync

Robert proposed removing Google Drive as the Mac mini `ws ai` sync layer and moving `ws ai` outside Drive, because the AI Workspace needs a better three-machine sync model across Mac mini, MacBook, and M4.

Inventory result without reading secret-looking contents:

- `ai_workspace` is not currently a git repo.
- Total size is about `331M`, dominated by generated/runtime material rather than core planning docs.
- Large or machine-local candidates include `.venvs` (`299M`), `.playwright-cli`, `tmp`, `tmp-staging`, `tmp_il_report`, `output`, `recordings`, `LOG_imapsync`, and `sync_backups`.
- Embedded git/code candidates include `screenbox` and `external/mempalace`.
- Secret/private candidates include `.env`, `.env.md`, `.private`, `screenbox/.env`, and `output/portal-account-passwords-2026-03-27.md`. Contents were not read.

Recommended replacement sync model:

1. Create `/Users/werkstatt/ai_workspace` as the canonical `ws ai` path on Mac mini, M4, and MacBook.
2. Make that directory a private git-backed coordination repo for safe text artifacts only:
   - `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `ToDo-append.md`, `project_hub/`, `worker_roles/`, Frank/Avignon non-secret planning docs, and small policy/planning/runbook docs.
3. Keep secrets out of git and out of Google Drive:
   - `.private`, `.env*`, OAuth tokens, app passwords, VPN/router secrets, key material, mailbox credentials, and password-like output files must move to approved secure storage or machine-local private paths.
4. Keep runtime/generated/cache material machine-local or archived outside the coordination repo:
   - virtualenvs, caches, logs, temp folders, recordings, generated output, local dependency folders, LaunchAgent runtime copies, tmux/session state.
5. Keep implementation code in each `/Users/werkstatt/<repo>` git repo:
   - do not nest active implementation clones inside `ai_workspace`.
6. Use GitHub private repo or another explicit git remote as the cross-machine sync mechanism:
   - Mac mini remains backend worker/automation host.
   - M4 and MacBook pull/push planning changes through git, with normal branch/commit history and conflict visibility.
7. Leave the current Google Drive `ai_workspace` in read-only/archive mode until the new repo is verified on all three machines.
8. Only after verification, update the `ws ai` alias/mapping to `/Users/werkstatt/ai_workspace` and stop using the Google Drive path for active AI coordination.

Do not remove Google Drive from Mac mini or delete/move `.private` until the safe subset has been created, pushed, cloned on all machines, and the secure-storage decision for secret material is explicit.

## 2026-04-15 Step 4 Start: Safe Git-Backed AI Workspace

Created `/Users/werkstatt/ai_workspace` on Mac mini as the new git-backed coordination repo.

Initial repo state:

- Branch: `main`
- Initial commit: `19c4e58` (`Create safe AI workspace coordination repo`)
- Size: about `1.1M`
- Tracked files: `143`
- M4 clone: `/Users/werkstatt/ai_workspace`, cloned from `admin-macmini:/Users/werkstatt/ai_workspace`

Included in the first safe subset:

- core coordination docs: `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `ToDo-append.md`, `README.md`, and selected top-level policy/planning docs
- `project_hub` markdown records
- `worker_roles` markdown records
- non-secret Frank and Avignon planning docs

Excluded from the first safe subset:

- `.private`
- `.env*`
- `screenbox/.env`
- virtualenvs and caches
- `tmp`, `tmp-staging`, `tmp_il_report`
- `output`, `recordings`, `LOG_imapsync`, `sync_backups`
- embedded implementation clones such as `screenbox` and `external`
- operational `scripts`
- Frank/Avignon drafts, sent logs, task JSON, automation logs, and private work artifacts

Mapping update:

- Mac mini `/Users/admin/.bashrc` now prefers `/Users/werkstatt/ai_workspace` for `ws ai`, with the Google Drive path as fallback/archive.
- M4 `/Users/kovaladmin/.bashrc` now prefers `/Users/werkstatt/ai_workspace` for `ws ai`, with the Google Drive path as fallback/archive.
- `frank` and `avignon` aliases prefer the new repo's planning directories on both machines.

Remaining before Google Drive can be retired:

1. Clone/verify the new repo on MacBook. Current Mac mini -> MacBook SSH check to `robert@192.168.55.38` still times out, so this is pending restored MacBook SSH/LAN reachability or manual GitHub clone on the MacBook.
2. Decide the secure storage path for `.private`, `.env`, OAuth, password, VPN/router, and mailbox credential material.
3. Decide whether any excluded generated/audit artifacts should be archived elsewhere.
4. Once verified on all three machines, stop using the Google Drive `ai_workspace` for active coordination and keep it read-only or archive it.

GitHub remote status:

- Robert created private repo `robs1412/ai_workspace`.
- Mac mini pushed `main` to `git@github.com:robs1412/ai_workspace.git`.
- Mac mini and M4 now use GitHub as `origin`.
- M4 also keeps `macmini=admin-macmini:/Users/werkstatt/ai_workspace` as a fallback remote.

## 2026-04-15 Step 4 Move Out Of Google Drive

Mac mini active AI coordination has moved out of Google Drive.

Completed:

- Active `ws ai` resolves to `/Users/werkstatt/ai_workspace`.
- Workspaceboard source and live runtime resolve AI Workspace, Frank, Avignon, and worker-role paths through `/Users/werkstatt/ai_workspace` first.
- Frank and Avignon LaunchAgents now use `AI_WORKSPACE_ROOT=/Users/werkstatt/ai_workspace`; Avignon uses `AVIGNON_WORKSPACE_ROOT=/Users/werkstatt/ai_workspace/avignon`.
- The old Google Drive `ai_workspace` folder was moved to `/Users/werkstatt/ai_workspace_google_drive_archive_20260415`.
- The original Google Drive path no longer exists on Mac mini.
- M4 pulled the new `ai_workspace` and `workspaceboard` commits and its local Workspaceboard now resolves AI Workspace, Frank, and Avignon to `/Users/werkstatt/ai_workspace`.
- M4 old Google Drive `ai_workspace` path is now gone; no M4 archive copy remains. Active M4 `ws ai` and Workspaceboard continue to resolve to `/Users/werkstatt/ai_workspace`.
- MacBook is now verified at `192.168.55.44` / `MacBookPro.lan`: `/Users/werkstatt/ai_workspace` is cloned at the current GitHub commit, `ws ai` resolves there, Workspaceboard `0.69` resolves AI/Frank/Avignon to `/Users/werkstatt/ai_workspace`, and the old Drive AI folder was moved to `/Users/werkstatt/ai_workspace_google_drive_archive_20260415_macbook`.

Archive handling:

- The archive is a legacy source/retention bundle, not an active workspace.
- Secret-looking and credential-bearing paths inside the archive must not be read, printed, synced, or copied into git during normal work.
- Future extraction from the archive should be task-specific: copy only approved non-secret records into `/Users/werkstatt/ai_workspace`, then commit through git.

Large-file rule:

- Git is the index and audit trail, not bulk storage.
- Large non-secret artifacts should live in an explicit local/NAS/artifact location with a committed manifest containing location, owner, size, SHA-256 checksum, retention, and share scope.
- Papers can be used for curated human-readable shared work records, but Claude/Codex should not both write the same Papers document until single-writer or locking rules are approved.
- Secrets, OAuth material, private keys, password-like files, and mailbox credentials stay out of git, Papers, and normal artifact manifests.

## Decision Driver Questions

1. Should M4 remain a local/manual board control surface, or should it become a formal Workspaceboard failover host?
2. Which remaining `ai_workspace` subfolder should be audited first for migration out of Drive?
