# Codex Session Handoff

Last Updated: 2026-04-15 11:15:00 CDT (Machine: Macmini.lan)

Use this file for cross-machine/session handoffs.

## Current Workflow Handoff

- Frank/Avignon follow-through correction at `2026-04-15 10:52 CDT` on `Macmini.lan`.
  - Problem addressed: 300-second LaunchAgent polls could exit `0` and report inbox zero while open email-derived decisions stayed parked in local/mailbox state and were not re-routed to visible work.
  - Source changes only: added `scripts/email_decision_watchdog.py`; wired `scripts/avignon_inbox_cycle.py` and `scripts/frank_auto_runner.py` to run a watchdog after inbox classification; updated `scripts/install_avignon_launchagent.sh` and `scripts/install_frank_launchagent.sh` so the next deliberate reinstall copies the watchdog into the runtime and de-duplicates Task Manager queue entries into `ToDo-append.md`.
  - Watchdog behavior: each open non-secret decision item is classified as `route-visible-worker`, `blocked-approval-gate`, `blocked-stale-open-record`, or `escalate-to-task-manager`; results are logged to runtime watchdog JSONL and included in cycle JSON. No mailbox bodies, credentials, mailbox content mutation, production writes, LaunchAgent reinstall, or live runtime restart were performed in this correction pass.
  - Source tracker cleanup: `avignon/EMAIL_DERIVED_DECISIONS.md` no longer lists the already-handled LJ Hospitality / Jamie Gilmore item under `Open`; `frank/EMAIL_DERIVED_DECISIONS.md` was added as the source tracker scaffold.
  - Manual approval still needed to activate in live 300-second workers: reinstall/restart `com.koval.frank-auto` and `com.koval.avignon-auto` from the updated source on the approved Mac mini automation host, then verify launchd status, recent stdout JSON `decision_watchdog_open_count`, and no duplicate queue spam.

- AI Workspace TODO reconciliation at `2026-04-14 21:57 CDT` from `Macmini.lan`.
  - Scope was AI Workspace coordination files only; no external sends, production writes, secrets, router/network changes, or Papers body reads were performed.
  - Board status before reconciliation: AI Workspace TODO `open_count=14`, append queue `6`; whole-board total `open_items=87` across all workspaces.
  - Reconciled completed/review-ready AI items: Communications Manager task routing, Earth Day Forge/lists workflow, OpenWrt/LuCI evaluation closeout, Heritage un-blacklist, Trainual first-module narrowing, and `/lists/` phpList CRM activity logging.
  - Cleared duplicate workstation append entries into the existing workstation/sync transition record instead of creating new architecture tasks. Remaining workstation questions stay in `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md`.
  - Remaining AI Workspace decisions after this pass: OpenWrt flash/reboot approval or deferral, and Mitch Donohue archive verification/rerun approval or park decision.

- M4 workstation handoff at `2026-04-14 13:08 CDT` from `Macmini.lan`.
  - M4 identity: `Mac.lan`, LAN IP `192.168.55.35`, user `kovaladmin`, home `/Users/kovaladmin`.
  - Synced AI workspace on M4: `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace`.
  - 2026-04-15 update: Workspaceboard now runs on the M4 as user `kovaladmin` via LaunchAgent `com.koval.workspaceboard` and serves `http://127.0.0.1:17878/api/status` with `ok: true`, `board_version: 0.69`, host `Mac.lan`.
  - 2026-04-15 update: M4 Project Management endpoint `http://127.0.0.1:17878/api/digital-office-index` returns `63` projects after Google Drive hydrates `project_hub`; Papers metadata is still `0` on M4 because no Papers snapshot was installed there.
  - 2026-04-15 update: M4 Homebrew, Node `v25.9.0`, npm `11.12.1`, and Codex CLI `0.120.0` are available under `/opt/homebrew/bin` when the shell PATH includes Homebrew. Non-login SSH still has a minimal PATH, so scripts should set PATH explicitly.
  - 2026-04-15 update: Robert created `/Users/werkstatt` on the M4. Moved the existing M4 clones from `/Users/kovaladmin/werkstatt` into `/Users/werkstatt` and replaced `/Users/kovaladmin/werkstatt` with a compatibility symlink to `/Users/werkstatt`.
  - 2026-04-15 update: Workspaceboard commit `a9833a3` path fallbacks remain installed; after the repo-root move, the M4 LaunchAgent was reinstalled from `/Users/werkstatt/workspaceboard` and `/api/status` resolves module workspaces to `/Users/werkstatt/<repo>`.
  - 2026-04-15 update: Created a dedicated local M4 GitHub SSH key at `~/.ssh/id_ed25519_github_robs1412` with public fingerprint `SHA256:jxIhzrI8ifFDsmyoj/fyCF5AfWbsXl7QkplxHFDpT+A` and configured `Host github.com` to use it. Robert added the public key to GitHub; `ssh -T git@github.com` now authenticates as `robs1412`.
  - 2026-04-15 update: GitHub-backed M4 repos now use `origin=git@github.com:robs1412/<repo>.git`; the previous Mac mini remote remains as `macmini=admin-macmini:/Users/werkstatt/<repo>` where applicable. GitLab-backed and local-only repos were not converted.
  - 2026-04-15 update: M4 dry-run fetch checks through `origin` worked for `workspaceboard`, `ops`, `portal`, `salesreport`, `lists`, and `login`. `lists/TODO.md` and `login/logs/auth_flow.log` were already dirty locally and were left untouched.
  - 2026-04-15 update: GitHub Desktop on the M4 is signed in as `robs1412` and has accepted 20 local GitHub-backed repos under `/Users/werkstatt`: `workspaceboard`, `ops`, `portal`, `salesreport`, `lists`, `login`, `forge`, `bid`, `importer`, `donations`, `eventmanagement`, `contactreport`, `database`, `newsite`, `playwright-scraper`, `rezepte`, `automation`, `automation_files`, `Gmailconnector`, `_birnecker.com`, and `braincloud`.
  - 2026-04-15 update: GitHub Desktop imports exposed existing dirty local states on M4: `lists` dirty `1`, `login` dirty `1`, `forge` dirty `3`, and `braincloud` dirty `10`. These were not changed or cleaned.
  - 2026-04-15 update: Mac mini and M4 now have the same 25 repo names under `/Users/werkstatt` and all 25 repo HEAD commits match. M4 `lists`, `login`, and `salesreport` were fast-forwarded to match Mac mini/GitHub; prior M4 `lists` and `login` local changes were preserved as stashes `m4-pre-git-align-20260415-lists` and `m4-pre-git-align-20260415-login`.
  - 2026-04-15 update: Remaining git differences are local dirt only: Mac mini has dirty `lists` and `ops`; M4 is clean for those after alignment. Existing non-transition dirt in `ai-bridge`, `braincloud`, `forge`, and `robert_workspace` remains outside this alignment pass.
  - 2026-04-15 transition step 2 check: 2018 Mac mini remains the backend/canonical worker host. `Macmini.lan` runs Workspaceboard LaunchAgent `com.koval.workspaceboard` on port `17878` with `ok: true`, `board_version: 0.69`, host `Macmini.lan`, and `26` managed sessions. Mac mini also owns Frank and Avignon LaunchAgents (`com.koval.frank-auto`, `com.koval.avignon-auto`) on 300-second intervals with last exit code `0`. M4 runs only local Workspaceboard; it does not have Frank or Avignon LaunchAgents loaded.
  - 2026-04-15 transition step 3 check: Google Drive is active on Mac mini and M4 for the AI Workspace planning layer. SHA-256 hashes match between Mac mini and M4 for `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `ToDo-append.md`, `project_hub/INDEX.md`, and `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md`.
  - 2026-04-15 transition step 3 boundary: code/runtime remains outside Drive (`/Users/werkstatt/workspaceboard`, `~/.workspaceboard-launch`, `~/.frank-launch`, `~/.avignon-launch`). The Drive folder still contains cleanup/retention candidates such as `.env`, `screenbox/.env`, `.venv_pdf`, `.venvs`, `tmp`, and `tmp-staging`; do not read or move secret-looking files without an explicit step 4 cleanup decision.
  - 2026-04-15 step 4 proposed direction: stop using Google Drive as active `ws ai` sync, create a safe git-backed `/Users/werkstatt/ai_workspace` coordination repo, keep secrets/runtime/generated material out of that repo, verify Mac mini/M4/MacBook clones, then update `ws ai` away from the Drive path. Current Drive tree is about `331M`, dominated by `.venvs` (`299M`) and other runtime/generated material; secret-looking contents were not read.
  - 2026-04-15 step 4 start: created `/Users/werkstatt/ai_workspace` as a git repo from a conservative safe subset of the Drive AI Workspace. Initial commit `19c4e58` contains `143` files and about `1.1M` of policy/TODO/handoff/project-hub/worker-role/non-secret Frank/Avignon planning docs. Excluded `.private`, `.env*`, virtualenvs, caches, temp folders, generated output, logs, drafts, embedded clones, and operational scripts. Cloned the repo to M4 at `/Users/werkstatt/ai_workspace` from `admin-macmini:/Users/werkstatt/ai_workspace`.
  - 2026-04-15 step 4 mapping: Mac mini `/Users/admin/.bashrc` and M4 `/Users/kovaladmin/.bashrc` now prefer `/Users/werkstatt/ai_workspace` for `ws ai`, with the Google Drive path left as fallback/archive during migration. `frank` and `avignon` mappings also prefer the new repo's planning directories.
  - 2026-04-15 step 4 blocker: `git ls-remote git@github.com:robs1412/ai_workspace.git` returns `Repository not found`, `gh` is not installed/authenticated on Mac mini, and the available GitHub connector cannot create repositories. Added future `github` remote `git@github.com:robs1412/ai_workspace.git` on Mac mini and M4. Once Robert creates a private empty GitHub repo named `ai_workspace`, push with `git push -u github main`.
  - 2026-04-15 step 4 MacBook blocker: SSH from Mac mini to `robert@192.168.55.38` timed out, so MacBook clone/verification is pending either private GitHub remote availability or restored MacBook SSH/LAN reachability.
  - Current M4 implementation/runtime state: canonical repo root is now `/Users/werkstatt`; `/Users/kovaladmin/werkstatt` is only a compatibility symlink.
  - Current M4 planning state: the synced AI workspace is present and contains `AGENTS.md`, `TODO.md`, `ToDo-append.md`, and this `HANDOFF.md`; use it as the policy/planning layer, not as the runtime source for code repos.
  - SSH verified: Mac mini -> M4 works with `/Users/admin/.ssh/id_ed25519_macmini_to_kovaladmin`, fingerprint `SHA256:F+eXrJ3kVmBB3K33Ey3Cq2S8jv98FDJIZZ2DQGP2W7E`, target `kovaladmin@192.168.55.35`.
  - SSH verified: M4 -> Mac mini works with `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macmini`, fingerprint `SHA256:LL73S8ka7ElnRPZz5L+Y49Tpy7doLdEshcGHkLHVmXw`, target `admin@192.168.55.17`. M4 has `~/.ssh/config` alias `admin-macmini` for this path.
  - SSH verified: M4 -> MacBook works with `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macbook`, fingerprint `SHA256:aJPvnNKu4jIRW6Vk0fz8MUhcrTj5Dk1j7ftwEI+F9HA`, target `robert@192.168.55.38`.
  - SSH verified: MacBook -> M4 works with `/Users/robert/.ssh/id_ed25519_macbook_to_m4`, fingerprint `SHA256:r7IG11t0+bo4XbJr6CGXja1HVjglMHwLX1MOzwgwC1w`, target `kovaladmin@192.168.55.35`.
  - SSH backups created during setup: M4 `/Users/kovaladmin/.ssh/authorized_keys.bak.20260414124930` and `/Users/kovaladmin/.ssh/authorized_keys.bak.20260414125130`; MacBook `/Users/robert/.ssh/authorized_keys.bak.20260414125129`; Mac mini `/Users/admin/.ssh/authorized_keys.bak.20260414125247`.
  - Detailed audit: `project_hub/issues/2026-04-14-macmini-m4-ssh-key-exchange.md`. Private key contents were not printed or moved.
  - Useful smoke commands:

```bash
# From Mac mini to M4
ssh -i ~/.ssh/id_ed25519_macmini_to_kovaladmin -o IdentitiesOnly=yes kovaladmin@192.168.55.35 hostname

# From M4 to Mac mini
ssh -i ~/.ssh/id_ed25519_m4_to_macmini -o IdentitiesOnly=yes admin@192.168.55.17 hostname

# From M4 to MacBook
ssh -i ~/.ssh/id_ed25519_m4_to_macbook -o IdentitiesOnly=yes robert@192.168.55.38 hostname
```

  - Next transition path: Robert creates private empty GitHub repo `robs1412/ai_workspace`, then push `/Users/werkstatt/ai_workspace` with `git push -u github main` and clone/verify it on MacBook. After that, decide where `.private`/`.env`/password-like material should live. Do not remove Google Drive from Mac mini or delete/move `.private` until the safe git repo is verified on all three machines and the secure-storage decision is explicit.

- Workspaceboard Node 25 runtime / Codex model fallback at `2026-04-14 12:58 CDT` on `Macmini.lan`.
  - Live LaunchAgent `com.koval.workspaceboard` is serving port `17878` from `/Users/admin/.workspaceboard-launch/runtime/app/server/index.js` with `/usr/local/opt/node/bin/node`; current PID verified as `28368` at closeout.
  - Root cause of the pasted smoke error was not Workspaceboard source or Node: current Codex CLI `0.120.0` remote compaction under `gpt-5.4` returns `Unknown parameter: prompt_cache_retention`.
  - `/Users/werkstatt/workspaceboard` now supports a board-only Codex model override via `WORKSPACEBOARD_CODEX_MODEL` / `CODEX_DASHBOARD_CODEX_MODEL`; `/api/status` reports the active override.
  - Reinstalled the Mac mini LaunchAgent with `WORKSPACEBOARD_CODEX_MODEL=gpt-5.3-codex ./scripts/install_codex_dashboard_launchagent.sh 17878`, so newly launched board sessions use `gpt-5.3-codex medium` while the global Codex config remains otherwise untouched.
  - First smoke session hit the one-time GPT-5.4 migration prompt; selected `Use existing model`. A second fresh smoke session opened directly as `gpt-5.3-codex medium`; both smoke sessions were closed.
  - Verification: `node --check server/index.js`, `zsh -n` for launcher scripts, live `/api/status`, LaunchAgent PID/Node path check, and tmux pane smoke. `npm install` under Node `v25.9.0` still warns that `@homebridge/node-pty-prebuilt-multiarch@0.13.1` declares `<25`, but the runtime had already verified the pty module loads under Node 25.

- Digital Office read-only Workspaceboard prototype implemented at `2026-04-14 12:40 CDT` on `Macmini.lan`.
  - `/Users/werkstatt/workspaceboard` commit `68df99c` (`Add Digital Office read-only prototype`) pushed to `origin/main`.
  - Live URL: `http://localhost/workspaceboard/digital-office.html`; live endpoint: `http://127.0.0.1:17878/api/digital-office-index`.
  - Scope stayed read-only and on-demand: indexes AI Workspace `project_hub/INDEX.md`, selected `project_hub/issues/*.md`, AI Workspace `TODO.md`, and Workspaceboard status/session metadata. No generated durable data is written.
  - Current endpoint totals after verification: `62` projects, `27` work items, `61` events, `61` artifacts, `149` relationships.
  - Verification: `node --check server/index.js`, `node --check server/digital-office-index.js`, `node --check assets/digital-office.js`, `php -l` for `api/digital-office-index`, `api/digital-office-index.php`, and `digital-office.html`, `git diff --check`, live curls for `/api/status`, `/api/management/overview`, `/api/digital-office-index`, Apache relay, and page smoke.
  - LaunchAgent was reinstalled/restarted with `./scripts/install_codex_dashboard_launchagent.sh 17878` so the live runtime serves the new route. Playwright was unavailable locally, so browser smoke was limited to served-page/API checks.
  - Forbidden-source boundary held: no Papers, `.205`, OPS/Portal schema or production DB, notification/email body, MCP, secret, `.env`, key file, or mailbox content access for this slice.
  - Follow-up candidate: separate Workspaceboard Node 25 migration task. Do not mix it into this committed prototype; native `pty.node` dependencies need rebuild/launcher verification under Node 25.

- Task Manager cleanup correction at `2026-04-14 12:10 CDT` on `Macmini.lan`.
  - Robert pointed out that session cleanup became too aggressive after the closeout sweep; the Digital Office planning worker `5129bf96` had been closed after its docs were copied into durable notes, removing the visible review surface.
  - Policy corrected in `AGENTS.md`: completed board-managed task sessions should be parked for Robert review by default. Cleanup sweeps must ask before closing review-ready sessions, except for obvious duplicate placeholders that never started real work or broken/crashed sessions after a replacement is created with visible handoff.
  - Standing monitors and constant-on email workers remain non-closeable by default.
  - Replacement review surface: create a visible AI Workspace session for Digital Office proposal review if continued discussion is needed; source documents remain `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md`, `ai-digital-office.md`, and `project_hub/INDEX.md`.

- Frank/Avignon independence clarification at `2026-04-14 12:10 CDT` on `Macmini.lan`.
  - Robert clarified that Frank and Avignon should act more independently, not just escalate routine clear internal requests.
  - Updated `frank/AGENTS.md`, `frank/WHAT_TO_DO.md`, and `avignon/AGENTS.md`: clear Robert/Sonat-originated low-risk internal requests such as daily overviews, status notes, task summaries, routing actions, reminders, completion updates, local task records, and handled-mail filing should be handled directly after duplicate checks unless an approval gate blocks them.
  - Approval gates remain for external-sensitive sends, finance/legal/security/auth, credentials, production-impacting work, destructive operations, unusual vendor/payment instructions, suspicious email, ambiguous ownership, or unclear recipient intent.

- Codex daily check-in reminder notification fix completed at `2026-04-14 12:05 CDT` on `Macmini.lan`.
  - Source confirmed: live Portal `ops:checkin-reminder` sends `checkins.reminder`; dry-run before mutation listed `Daily reminder -> Codex Agent (1332)`.
  - Targeted live DB change only: `notifications_user_settings.id=7981`, `user_id=1332`, `notification_type=checkins.reminder` changed from `channel_email=1`, `is_enabled=1` to `channel_email=0`, `is_enabled=0`, `updated_by=1332`.
  - Verification: active subscriber count for Codex `checkins.reminder` remained `0`; global `notifications_rules.checkins.reminder` stayed active for humans with `channel_email=1`, `is_active=1`; Portal repo had no code changes.
  - Audit: project log `project_hub/issues/2026-04-14-codex-daily-checkin-notifications.md`; OPS TODO bookkeeping commit pushed to `/Users/werkstatt/ops` as `7a5ffc9` (`Record Codex daily reminder preference fix`).
  - Follow-up: passively monitor the next scheduled daily reminder run for absence of Codex/Robert-routed `checkins.reminder` attempts.

- Heritage distributor un-blacklist backlog closeout at `2026-04-14 21:56 CDT` on `Macmini.lan`.
  - Reviewed Salesreport TODO, empty Salesreport append queue, Salesreport audit doc `doc/heritage-rndc-contact-link-update-2026-04-14.md`, AI Workspace TODO/HANDOFF, and current Workspaceboard overview.
  - Closed the AI Workspace backlog lines `Distributor un-blacklist people at Heritage` and `Check if emails need to switch to RNDC domain` because Salesreport commit `8281602` already recorded the completed Robert-approved Path A: link seven active RNDC replacement contacts to Heritage account `11884` and preserve all old Heritage Wine Cellars blacklist/suppression state.
  - No CRM/phpList mutations, list sync, emails, or external communication were performed in this closeout pass.

- Digital Office project/task/work-record proposal completed at `2026-04-14 11:58 CDT` on `Macmini.lan`.
  - Created docs-only project note `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md` and linked it from `project_hub/INDEX.md`, `ai-digital-office.md`, and `TODO.md`.
  - Source-of-truth recommendation: `project_hub` owns cross-workspace project/decision/approval records; workspace `TODO.md` files remain short action queues; OPS/Portal remains the business/staff task source of truth; Workspaceboard remains live execution/session source of truth; Papers is only a document/work-record projection until approved inspection proves otherwise.
  - First implementation route to ask Robert to approve: `ws workspaceboard` -> Code and Git Manager preflight -> Workspaceboard implementation worker for a read-only project/task/work-record index and dashboard prototype from project-hub, TODO, and board/session metadata.
  - Approval gates remain closed for Papers writes, `.205` access, OPS/Portal schema or production DB changes, notifications/emails, background daemons, MCP exposure, and secret-bearing content.

- Standing email-worker correction at `2026-04-14 11:58 CDT` on `Macmini.lan`.
  - Robert clarified that Frank and Avignon email workers are constant-on monitor/control-surface roles and must not be closed during finished-worker cleanup or auto-close sweeps.
  - Corrective action: recreated Frank as board session `1794c370` (`Frank email worker - inbox and task flow`) and Avignon as board session `09af6d70` (`Avignon email worker - inbox and task flow`).
  - Verification: Frank monitor reported LaunchAgent `com.koval.frank-auto` loaded/running in draft-only mode with last launchd exit `0`; Avignon monitor ran an installed-environment cycle with inbox start/end `0`, archived `0`, decision items `0`, and LaunchAgent `com.koval.avignon-auto` last exit `0`.
  - Policy update: `AGENTS.md` now explicitly excludes standing monitors and Frank/Avignon constant-on email workers from auto-close cleanup.

- Task Manager worker closeout sweep at `2026-04-14 11:48 CDT` on `Macmini.lan`.
  - Closed 19 finished or superseded board sessions after reviewing their latest output. The remaining visible board sessions are standing AI monitors plus two real business-decision assessment sessions: RNDC domain clarification and Heritage distributor un-blacklist approval.
  - Resolved the two dirty repo clusters instead of leaving workers parked on "dirty repo": `/Users/werkstatt/workspaceboard` is clean on `main...origin/main` after commit/push `af631f4` (`Coordinate workspaceboard worker updates`), and `/Users/werkstatt/bid` is clean on `main...origin/main` after commit/push `8e1bc80` (`Add BID import preflight and cadence tracking`).
  - Workspaceboard checks run before commit: `node --check` on `server/index.js`, `assets/app.js`, `assets/management.js`, `assets/task-management-light.js`; `php -l` on `task-management.html`, `worker-organigram.php`, `worker-organigram.html`; and `git diff --check`.
  - BID checks run before commit: `php -l tools/import_preflight.php`, `php -l docs_settings.php`, `git diff --check`, CSV width validation for `data-management/templates/source-inventory.csv`, and a scan confirming `tools/import_preflight.php` does not include DB/write SQL behavior.
  - The Workspaceboard API recovered after the cleanup and returned `ok: true`, board version `0.69`, host `Macmini.lan`.

- Digital Office routing closeout at `2026-04-14 11:25 CDT` on `Macmini.lan`.
  - Robert/Task Manager directed that the current Claude at work / Codex integration follow-up belongs under the larger Digital Office initiative, not as a standalone AI-Bridge open item.
  - Updated `ai_workspace/ai-digital-office.md`, `ai_workspace/TODO.md`, `/Users/werkstatt/ai-bridge/README.md`, `/Users/werkstatt/ai-bridge/TODO.md`, and `/Users/werkstatt/ai-bridge/CLAUDE-CODEX-NEXT-STEPS.md`; added AI-Bridge closeout trace `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-14-digital-office-routing-closeout.md`.
  - Remaining owner: Digital Office / AI Workspace. Next follow-up is to create a sanitized AI-Bridge trace for Claude's Frank reply, then classify recommendations before any implementation.
  - Approval gates remain: no `.205` SSH, credential probing, authenticated papers inspection, MCP exposure, bridge code implementation, OPS/Portal task creation, or production-impacting work without explicit approved routing. No secrets were read or printed in this closeout.

- OpenWrt/LuCI validation session closeout at `2026-04-13 21:32 CDT` on `Macmini.lan`.
  - Task Manager routed Robert's reminder request to Frank email worker `ec85e0c1` to email Robert tomorrow at `2026-04-15 09:00` local time.
  - Evaluation-only work is complete: official image validation passed earlier; custom package-preserving image was built, staged to `/tmp/codex-openwrt-20260414-custom-validation/openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`, staged SHA256 matched `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`, and `sysupgrade -T` returned `0`.
  - No firmware flash, reboot, firewall/VPN reload, StrongSwan/WireGuard restart, live-router package install, router config change, or secret output occurred.
  - Next required approval before any upgrade: Robert must explicitly approve flashing the staged custom image and accept the reboot/connectivity-risk window after rollback prerequisites are reviewed. This OpenWrt board session can be closed.

- Security hardening review docs-only closeout completed at `2026-04-13 21:22 CDT` on `Macmini.lan`.
  - Project log `project_hub/issues/2026-03-07-security-hardening-review.md` is marked completed for the current docs-only review; AI Workspace TODO moved the item from Backlog to Done.
  - No client SSH config, server SSHD config, key material, credential material, or live deploy flow was changed.
  - Robert-reported MacBook check confirms MacBook -> `admin-macmini` publickey-only access succeeds at `192.168.55.17`.
  - Live `koval@ftp.koval-distillery.com` publickey access works, but server still advertises `password` and reports OpenSSH `8.0p1` with non-PQ `curve25519-sha256`.
  - Silent Codex OPS follow-up task `366581` is due `2026-04-22` to review client-side SSH hardening only across Mac mini, M4 Mac mini, and MacBook.

- OPS task registration audit completed at `2026-04-14` from `/Users/werkstatt/ops`.
  - Restored `/Users/werkstatt/ops/scripts/create_codex_task.php` and the explicit `crm_create_task(..., ['allow_service_fallback' => true])` task-creation path so Robert-originated Codex tasks can be created/repaired without substituting Robert/admin/test owners. The helper prints non-secret task metadata only.
  - Verified existing BID refs `366460` and `366486` already had creator `1`, owner `1332`, and assignee `1332`.
  - Repaired Communications Manager workflow refs: Square `363191`, Shopify `360626`, and Forge donations `363052` now verify as creator `1`, owner `1332`, and assignee `1332`. No external email/newsletter send, Forge/lists repo edit, or donation/list pull was performed.
  - Repaired Trainual task `366499`: creator `1`, owner `1332`, assignees `1,144,1332`, due/start `2026-05-01`.
  - Created OpenWrt/LuCI tracking task `366563` and Workspaceboard tracking tasks `366564` (email decision board workers), `366565` (Latest Output height), and `366566` (session file attachments); each verifies as creator `1`, owner `1332`, assignee `1332`.
  - Remaining auth caveat: a direct `crm_hydrate_session_portal_token('Codex')` probe still returned no usable token, and the service impersonation warning still appears for the configured fallback login. Task registration succeeded only through the explicit helper fallback plus forced CRM metadata. No secrets were printed.
  - Robert clarified the silent TODO-task rule after this audit: Codex tasks generated from TODOs must not send task creation or completion emails/notifications because those go to Robert's inbox. `/Users/werkstatt/ops/scripts/create_codex_task.php` now disables creation notifications by default; only pass `--notify=1` when Robert explicitly asks for notification side effects. Completion/update scripts for TODO-generated Codex tasks must likewise disable notification side effects; use a silent completion path such as OPS `complete_tasks_silent` or an update payload with notification flags off.
  - Urgent correction after task `366583`: Robert still received a `tasks/assigned` email. Final CRM row for `366583` verifies creator `1`, owner/assignee `1332`, and `sendnotification=0`, but the email had already been sent during Portal API creation. Root cause: Portal `TaskController::create()` sent `sendNotification('tasks','assigned', ...)` whenever `assigned_to` was present, ignoring false notification flags, and `TaskController::update()` likewise sent completion/status notifications on status changes without checking false notification flags. Code/Git Manager reviewed the narrowed fix and the DataHistory decision. OPS commit `555972f` was pushed to `origin/main` and Portal dev commit `cf6b217c` plus merge `a582ce6a` were pushed to `origin/dev`: Portal now honors false notification flags and OPS complete_task suppresses Robert-created/Codex-owned task notifications. The OPS helper remains on the Portal create path so Portal keeps its normal `DataHistory::create` side effect; deploy Portal before any further silent TODO task creation through that API path. The delivered `366583` email cannot be unsent; its current CRM notification flag is already corrected for future checks. No OPS live pull or Portal production deploy has been performed.

- Workspaceboard three-worker merge completed at `2026-04-13 19:21 CDT` on `Macmini.lan`.
  - Merged compatible worker outputs from `58828a01` (email decision board expansion), `5804ae97` (Latest Output height stabilization), and `a634a15d` (new-session file attachment hardening) in `/Users/werkstatt/workspaceboard`.
  - Ownership reviewed before merge: `58828a01` touched `server/index.js` and `assets/task-management-light.js`; `5804ae97` touched `assets/management.css` and `task-management.html`; `a634a15d` touched attachment hardening in `server/index.js`.
  - Live panes for those sessions were idle at reusable prompts with no attached clients during merge; their AI Workspace TODO items were moved from In Progress to Done.
  - Runtime source changes are compatible and validated in the workspaceboard repo before commit/restart.

- AI workstation/sync transition audit completed at `2026-04-13 19:21 CDT` on `Macmini`.
  - 2026-04-14 11:24 CDT update: Robert approved deletion rather than read-only retention. Deleted only `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/codex_dashboard` after checking it was the synced legacy source copy, had no `.git`, and had no open file handles.
  - Evidence: `/Users/werkstatt/workspaceboard` is the active git-backed source of truth with newer Workspaceboard/Task Manager/phone work, dedicated README/TODO, remote `git@github.com:robs1412/workspaceboard.git`, and machine-local runtime reinstall flow. After deleting the legacy synced source copy, `http://127.0.0.1:17878/api/status` still returned `ok: true`, `board_version: 0.69`, host `Macmini.lan`.
  - Intentionally left in place: `/Users/werkstatt/workspaceboard`, `/Users/admin/.workspaceboard-launch`, `/Users/admin/.codex-dashboard-launch`, Workspaceboard and old codex-dashboard LaunchAgent plists, `ai_workspace/scripts/*`, and dashboard logs/state under `ai_workspace/tmp/`.
  - Keep in `ai_workspace`: policy/planning docs, project hub, TODO/HANDOFF, worker role docs, Frank/Avignon non-secret planning and draft records, and intentional audit logs.
  - Move or re-home after explicit approval: `screenbox` as an external git clone outside Drive if still useful; `external/mempalace` only after preserving its two local modified files or deliberately discarding the closed pilot; generated/temp/runtime material such as `.venvs`, `.venv_pdf`, `.playwright-cli`, `tmp*`, `output`, `recordings*`, `LOG_imapsync`, and old Workspaceboard handoff package(s) should be machine-local or archived only when no longer needed as audit evidence.
  - Specific cleanup candidates found: `worker_roles (1)` is byte-identical to `worker_roles` and can be removed after Robert approves cleanup; `htdocs/braincloud` is an empty/broken symlink and should not be treated as an implementation root; `output/portal-account-passwords-2026-03-27.md` is credential-sensitive and should be handled through approved credential-retention/rotation policy rather than casual Drive cleanup.
  - Current caution: `/Users/werkstatt/workspaceboard` had active uncommitted changes at audit time, so do not clean/commit/restart it from this AI planning note alone; coordinate with the active Workspaceboard worker/session first.

- Earth Day Forge/lists workflow completed at `2026-04-13 16:18 CDT` in `/Users/werkstatt/forge`.
  - phpList draft `#550` is the account-send copy for bars/restaurants/accounts and remains `draft`; no external campaign was sent.
  - Las Vegas distributor `Magnum Wine and Spirits` was verified on legacy `Distributors - US` (`#38`) and Forge `Distributors` (`#105`).
  - `Johnson Brothers - Minnesota` was verified as `Old Distributor` and not present in distributor send lists `#38/#78/#82/#84/#85/#105`.
  - Forge-owned phpList lists were eligible-only replace-synced: `#105`, `#141`, `#142`, `#143`.
  - Detail handoff: `/Users/werkstatt/forge/handoff.md`.
  - Approval gate remains: do not send draft `#550` or any external newsletter without Robert approval.

## Coordination Reminder

- Important AI Workspace workflow/policy/session changes should be noted in both `AGENTS.md` and `HANDOFF.md` when they affect cross-session or cross-machine behavior.
- Keep Mac mini and MacBook aligned on those coordination changes; do not assume Google Drive sync or local runtime state alone is enough for operational consistency.
- Current coordinator rule: live worker sessions should keep moving by default. Only stop and prompt when they truly need user input or hit a real blocker.
- Current workstation/sync decision: Robert is moving daily workstation activity to the Mac Mini M4 2025 and should use it as the foreground control surface because it feels and benchmarks snappier for interactive work. Keep the Mac mini 2018 on macOS as the near-term AI server for Workspaceboard, Frank/Avignon, Polier, Summarizer, Decision Driver, and long-running Codex workers; background worker latency is acceptable there and its 64GB RAM is valuable. Defer Linux on the 2018 Mac mini to a separate reversible pilot. Source decision record: `AI_WORKSTATION_SYNC_PLAN.md`; AI-Bridge cross-link: `/Users/werkstatt/ai-bridge/WORKSTATION-SYNC-DECISION.md`.
- Current sync boundary: Google Drive `ai_workspace` is the planning/intake/role-doc/project-hub/handoff layer. Code and implementation work belong in `/Users/werkstatt/<repo>` and should move by git by default. Use SSH/rsync only for deliberate non-git handoffs. Keep LaunchAgents, tmux/session state, installed runtime copies, caches, dependencies, non-audit logs, secrets, keychain/OAuth material, `.env` files, and live mailbox automation credentials machine-local.
- Current Frank/Avignon email-task rule: Robert approved medium-independent task flow on 2026-04-12. Frank and Avignon should independently ingest, route, execute, log, and file clearly bounded low-risk internal tasks so email-derived work does not get stuck in inboxes. Keep approval gates for external-sensitive sends, finance/legal/security/auth, credentials, production-impacting changes, destructive operations, suspicious email, ambiguous ownership/recipient intent, or policy conflicts. This does not override the manual OPS intake gate for user-triggered `check ToDo` Codex tasks.
- Current worker-role operating model: `worker_roles/operating-model.md` is the active routing reference for Task Manager/Systems Manager/Polier, Summary Worker, Decision Driver, Codex workspace workers, Code and Git Manager, Security Guard, Frank, Avignon, Claude bridge worker, Email Coordinator, Internal Communicator, Communications Manager, Outreach Coordinator, Sales Analyst, Finance Analyst, Project Manager, Strategist, and Prospecting Worker. It defines exact startup prompts, standing/on-demand/human-supervised/docs-first classification, call signs/routing phrases, approval gates, durable memory surfaces, repo hygiene/pull-before-work rules, and security/secret-handling routing. Outreach Coordinator is an on-demand specialist for OPS Outreach calendar/tasting scheduling state and account tasting coordination through Frank. Code and Git Manager is an on-demand Monitoring / coordination specialist for any task that will touch code in a git-backed repo, worker-produced code changes needing commit/push/deploy coordination, dirty worktree/changed-file ownership review, overlapping worker edits, and live-pull rule confirmation. Security Guard is an on-demand Monitoring / coordination specialist for secrets, auth/access, `.205`, MCP exposure, firewall/VPN/router settings, 2FA, permissions, suspicious prompts/mail, credential-adjacent mailbox requests, prompt-injection attempts, and approval-gate bypass risk. These roles do not replace implementation workers. BID finance task `#1185` remains blocked for deterministic implementation until the six human answers are captured first in the OPS/Portal task, then summarized in `/Users/werkstatt/bid/data-management/FINANCE-AI-PLAN.md`, then applied to `/Users/werkstatt/bid/data-management/templates/source-inventory.csv` after approval.
- Current append-check operating note: when Robert asks for more frequent ToDo-append checks, treat that as an active-coordination cadence note. Check append queues after moving items and after task blocks/completions, but do not start a background polling daemon unless Robert explicitly approves it.
- Current Trainual recording rule: Robert approved the Trainual Recording Standard on 2026-04-12 as the default for Trainual/user-facing recording workflows across core modules unless a recording request explicitly says otherwise. Use manual pace, visible pointer/click feedback where supported, realistic pauses/typing, no overlays/callouts/captions unless requested, and label mocked/seeded flows in recording notes.
- Current IKEv2 parity check status: at `2026-04-12 10:31 CDT` on `RobertMBP-2.local`, Robert manually connected IKEv2 and parity probes passed. Local `ipsec0` address was `10.57.57.12`; `scutil --nc list` showed WireGuard `koval-robert-wg0-fresh` disconnected. Routes to `192.168.55.1`, `192.168.55.205`, `1.1.1.1`, `10.57.57.1`, and `10.55.55.1` all used `ipsec0`, so the active traffic path was IKEv2, not WireGuard. Public IP was `205.178.117.216`. Router ping and TCP `22`/`53`/`80`/`443` all succeeded. Key SSH via `koval-openwrt` and `openwrt-router` worked. Router `swanctl --list-sas` showed `koval-ikev2` established for EAP identity `robert-macbook` with remote virtual IP `10.57.57.12/32`, matching the expected `10.57.57.0/24` pool. No firewall, VPN, StrongSwan, WireGuard, or router password changes were made. IKEv2 can replace WireGuard as primary, with WireGuard retained as fallback.
- Current OpenWrt/LuCI upgrade assessment: at `2026-04-12 11:07 CDT` on `RobertMBP-2.local`, read-only SSH confirmed the router is Linksys WRT3200ACM (`mvebu/cortexa9`) on OpenWrt `24.10.5` with LuCI installed and active IKEv2 SAs for `robert-macbook` and `sonat`; Mac-side route to `192.168.55.1` uses `ipsec0` and public IP is `205.178.117.216`. Latest same-series OpenWrt is `24.10.6`; latest stable is `25.12.2`, and the official downloads include `linksys_wrt3200acm-squashfs-sysupgrade.bin`. `25.12` is higher risk because package management changes from `opkg` to `apk`. No firmware/package upgrade, backup creation, firewall reload, VPN reload, or reboot was performed. At `2026-04-12 11:27 CDT`, Robert chose to evaluate the bigger `25.12.2` upgrade path first and set Tuesday 2026-04-14 10:00 CDT as the target maintenance/evaluation slot. At `2026-04-12 11:31 CDT`, the no-flash runbook was drafted: official profile supports `linksys,wrt3200acm`, target image is `openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin` with SHA256 `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`, and the main risk is that plain sysupgrade may preserve configs but not all non-default StrongSwan/WireGuard packages. Blocked pending Robert approval for backup creation/validation-only staging, and a separate explicit approval before any actual flash or disruptive action. Detail log: `project_hub/issues/2026-04-12-openwrt-luci-upgrade-assessment.md`.
- OpenWrt/LuCI staging update at `2026-04-12 11:53 CDT`: Robert approved backup creation and validation-only staging, still not firmware flash/reboot/firewall reload/VPN reload/service restart. Completed staging under `.private/router/openwrt-upgrade-20260414-1000`: official image/hash/profile/buildinfo downloaded, SHA256 verified, router sysupgrade and critical-config backups copied off-router, non-secret metadata captured, verified image staged on router at `/tmp/codex-openwrt-20260414-1000/openwrt-25.12.2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`, and `sysupgrade -T` exited `0` with no compatibility warning in captured output. Generated secret-bearing backup tarballs were removed from router `/tmp` after copy-out; the non-secret staged firmware image remains. Also moved former top-level `/Users/robert/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/network_workspace` intact to `.private/router/network_workspace`; no conflict was found. Remaining decision: custom package-preserving `25.12.2` image evaluation vs accepting the plain official image with local/LAN recovery ready; still no disruptive action approved.
- OpenWrt/LuCI preservation update at `2026-04-12 12:38 CDT`: Robert clarified the priority is preserving current behavior after any eventual restart/upgrade: VPN behavior, routing, static IPs/leases, DNS/DHCP, firewall/NAT, WAN/LAN, SSH/LuCI, IKEv2, WireGuard fallback, and recovery paths. Drafted a current-state preservation checklist in `project_hub/issues/2026-04-12-openwrt-luci-upgrade-assessment.md` using private backups/metadata. Source summary is `.private/router/openwrt-upgrade-20260414-1000/metadata/preservation-checklist-source-summary.txt`; critical package set is `.private/router/openwrt-upgrade-20260414-1000/metadata/custom-image-critical-package-set.txt`. Counts from backup include `206` static DHCP host sections, `2` DHCP pools, `4` firewall zones, `5` forwardings, `19` firewall rules, `34` redirects, and `6` network interface sections. Live router refresh is currently blocked because MacBook is not on IKEv2/WireGuard (`ipsec0` absent, WireGuard disconnected, route to `192.168.55.1` via `en0`, ping/SSH timed out). Before Tuesday, Robert should reconnect IKEv2, provide local LAN access, or confirm another management path. Still no disruptive action approved.
- OpenWrt/LuCI live refresh update at `2026-04-12 14:54 CDT`: Robert reconnected IKEv2 and live read-only router refresh completed. Artifacts: `.private/router/openwrt-upgrade-20260414-1000/metadata/live-current-state-20260412-1452.txt`, `.private/router/openwrt-upgrade-20260414-1000/metadata/live-nft-ruleset-20260412-1452.txt`, and `.private/router/openwrt-upgrade-20260414-1000/metadata/live-refresh-diff-20260412-1454.txt`. Route to `192.168.55.1` uses `ipsec0` (`10.57.57.12`); router ping, SSH `22`, HTTP `80`, HTTPS `443`, and TCP DNS `53` are reachable; public IP is `205.178.117.216`; IKEv2 SA is active for `robert-macbook`; WireGuard interfaces `wgmac`/`wg0` remain present as fallback but Mac WireGuard is disconnected locally. Live structural counts match backup: `206` static DHCP hosts, `2` DHCP pools, `4` firewall zones, `5` forwardings, `19` rules, `34` redirects, `6` network interfaces, `0` explicit route sections, `3` wifi devices, and `3` wifi interfaces. Runtime DHCP leases: `57`; nftables summary: `3` tables, `46` chains, `232` rule lines, SHA256 `1a69f2092b9c54a7440392988a2d886c3646da8874a8455817841b6ca2e1955e`. DNS note: direct UDP `dig @192.168.55.1` over IKEv2 timed out, while Mac DNS uses `1.1.1.1`/`8.8.8.8` over `ipsec0`; preserve current public-DNS-over-IKEv2 behavior unless Robert deliberately changes it. Still no disruptive action approved.
- OpenWrt/LuCI custom-image evaluation update at `2026-04-13 19:20 CDT`: Robert approved checklist/package-plan preparation only for the custom package-preserving `25.12.2` evaluation. Created `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-evaluation-checklist.md` and updated the main project note. Safe public read-only checks reconfirmed the official WRT3200ACM sysupgrade hash `cf1ab7a2cafd6e317afc76cf1653be774474ba9ca3f74e6cdf5bd26118c4640c`, ImageBuilder tarball hash `87fba1a44f6fa07660da4278bb4ef27e6aade813a7fde2cfe1dd81edcf09220f`, and `profiles.json` WRT3200ACM target metadata. Local Google Drive private artifacts under `.private/router/openwrt-upgrade-20260414-1000` currently show logical sizes but `0` local blocks, so hydrate non-secret metadata/official files and rerun hashes before building/using a package list. No custom image was built, no router-side staging was performed, and all hard gates remain: no flash, reboot, firewall/VPN reload, StrongSwan/WireGuard restart, live-router package install, or secret printing.
- OpenWrt/LuCI guide/build-plan update at `2026-04-13 20:04 CDT`: continued evaluation only for Tuesday `2026-04-14 10:00 CDT`. Created `project_hub/issues/2026-04-14-openwrt-25.12.2-upgrade-rollback-guide.md`, `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-build-evaluation-plan.md`, and `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-package-input.txt`. Public feed checks confirmed required package families exist in 25.12.2 feeds/kmods. No custom image was built/requested, no private secret-bearing files were read or printed, and no router-side action was taken. Because the prior checklist gates build/request itself, the exact next approval needed is: approve local custom OpenWrt 25.12.2 WRT3200ACM image build/request evaluation, allowing non-secret metadata hydration, ImageBuilder/Firmware Selector use, local image/manifest generation under `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/`, and no router-side staging/`sysupgrade -T`/flash/reboot/reload/restart/package install/secret printing.
- OpenWrt/LuCI custom image build result at `2026-04-13 20:25 CDT`: Robert approved local custom image build/request evaluation only. Used official ASU/custom image API from macOS; no router-side action was taken. Build result note: `project_hub/issues/2026-04-14-openwrt-25.12.2-custom-image-build-result.md`. Generated local sysupgrade image: `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`, SHA256 `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`, size `11735688`, ASU request hash `e4cbf3a63c081b2096075aac200969b37c7c4595b73ad5079599f5eec40514fd`. Manifest comparison against candidate package input: `62/62` requested packages present, `0` missing; required LuCI/uhttpd/dropbear, firewall/DNS, WireGuard, WRT3200ACM device defaults, and StrongSwan/IKEv2 package families are present. Caveat: private saved package metadata is still Google Drive placeholder-only on this machine, so full `opkg-list-installed-24.10.5.txt` reconciliation is not complete here. Next approval required: validation-only router staging of that exact image/hash and `sysupgrade -T`; actual flash remains separately gated.
- OpenWrt/LuCI custom validation blocker at `2026-04-13 20:35 CDT`: Robert approved validation-only staging of the exact custom image and `sysupgrade -T`, with no flash/reboot/reload/restart/package install/secret printing. Local hash was reverified as `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029` and router ping/reachability passed, but staging did not proceed because router authentication is not available on this Mac. The old router aliases/key are absent, direct root key auth to `192.168.55.1` fails, no matching local keychain item metadata exists, and `.private/router/openwrt-root-password.txt` is a dataless Google Drive placeholder that cannot be safely read/copied here (`Resource deadlock avoided`). A temporary secret-materialization directory was removed; no password content or hash was printed. No custom image was copied to the router, no `sysupgrade -T` was run, and no router config/service/disruptive action occurred. Next safe continuation requires Robert to materialize/provide an approved router SSH credential path on this Mac without printing secrets; after that, rerun only staging plus `sysupgrade -T` for the exact custom image/hash. Actual flash remains separately gated.
- OpenWrt/LuCI credential-reference retry at `2026-04-13 20:45 CDT`: Robert reconfirmed `.private/router/openwrt-root-password.txt` as the approved sensitive local credential reference. Retried only non-printing local consumption for validation-only access. File Provider still reports the file is not downloaded, pin/keep-downloaded metadata did not hydrate it, direct read/expect read/copy paths fail or return zero bytes, and copy attempts still report `Resource deadlock avoided`. Temporary secret test directory was removed. Validation remains blocked before router staging; no custom image copy, `sysupgrade -T`, router config change, or disruptive action occurred.
- OpenWrt/LuCI credential-location follow-up at `2026-04-13 20:52 CDT`: Robert suggested Macmini Google Drive or SSH to MacBook as credential-location hints. Checked local synced paths by filename metadata only. `/Users/robert` is absent on this Macmini account, `/Users/werkstatt` has no ai_workspace credential copy, and the only local candidate remains the admin Google Drive placeholder (`blocks=0`, not downloaded). MacBook SSH probes to `macbookpro.lan`/`192.168.55.33` timed out or reported host down; `192.168.55.34` answered ping but refused SSH. No credential contents were read or printed. Validation remains blocked before staging.
- OpenWrt/LuCI custom image validation result at `2026-04-13 21:04 CDT`: Used the approved `/Users/werkstatt/.private/router/` credential reference only inside SSH/SCP validation helpers without printing/storing contents. Custom image staged to `/tmp/codex-openwrt-20260414-custom-validation/openwrt-25.12.2-285891de87a2-mvebu-cortexa9-linksys_wrt3200acm-squashfs-sysupgrade.bin`. Local and staged SHA256 both matched `c2dd7796370a4cdec34aabccfb85721ef38401b2ee5f6ffd29ea2fcce62d1029`; `sysupgrade -T` exit status `0`; captured output showed no compatibility warning text. Artifacts are under `.private/router/openwrt-upgrade-20260414-1000/custom-image-evaluation/`, including `custom-validation-result-20260413-2104.md`. No flash, reboot, firewall/VPN reload, StrongSwan/WireGuard restart, live-router package install, or router config change occurred. Separate explicit approval is required before actual firmware flash.
- MacMini sync note for the 2026-04-12 medium-independent policy update: local AI workspace files were updated on `RobertMBP-2.local`, but direct `scp`/`ssh` verification to MacMini could not complete from the current network path. `admin-macmini` resolved to `192.168.55.17` and returned `Network is unreachable`; direct `admin@192.168.55.16` timed out. Verify Google Drive sync or copy the updated policy files from this machine when MacMini is reachable.
- Mac mini reachability-only update at `2026-04-13 08:37 CDT` on `RobertMBP-2.local`: Robert reported the Mac mini was reset/back online, but the current AI Workspace path still cannot reach the KOVAL `192.168.55.0/24` network. `ssh -G admin-macmini` shows the alias points to `admin@192.168.55.17:22` with the existing admin key path. `scutil --nc list` shows WireGuard disconnected, `ipsec0` is absent, local interface is `en0` at `192.168.4.29`, and routes to `192.168.55.1`, `.16`, `.17`, and `.205` go via `192.168.4.1` on `en0`. Ping and TCP checks to router `.1`, previous Mac mini candidates `.16`/`.17`, and `.205` all timed out; SSH to `admin-macmini`/`.17` and direct `.16` both timed out. `Macmini.lan`, `Macmini.local`, and `admin-macmini` did not resolve as hostnames outside the SSH alias; mDNS SSH browse saw only this MacBook. Public egress was `168.91.196.90`, not the prior KOVAL VPN egress `205.178.117.216`. Conclusion: current evidence supports wrong/disconnected VPN/LAN path from the MacBook, not a proven Mac mini IP change or SSH daemon failure. Next safe action is to reconnect/verify the approved KOVAL VPN or local LAN path, then rerun the same read-only alias/route/ping/TCP/SSH checks before doing any Mac mini npm work. No router, Mac mini, SSH key, password, or firewall settings were changed.
- Mac mini npm/runtime follow-up at `2026-04-13 11:33 CDT` on `MacBookPro.lan`: office LAN reachability returned. Read-only SSH to `admin-macmini` succeeded as `admin` on `Macmini.lan`, macOS `15.7.4`, and Workspaceboard `http://127.0.0.1:17878/api/status` returned `ok: true`, `board_version: 0.63`, host `Macmini.lan`. Non-login SSH PATH is minimal and does not expose Node/npm/Codex. Live Workspaceboard LaunchAgent `com.koval.workspaceboard` runs `/Users/admin/.workspaceboard-launch/runtime/scripts/launch_codex_dashboard_agent.sh 17878`, which explicitly exports `/usr/local/opt/node@24/bin` and executes `/usr/local/opt/node@24/bin/node /Users/admin/.workspaceboard-launch/runtime/app/server/index.js`. Active Workspaceboard Node is `v24.14.1`; Node 24 bundled npm is `11.11.0`; Node 24 npm reports global prefix `/usr/local` and root `/usr/local/lib/node_modules`; global packages include `@openai/codex@0.118.0` and a separate global `npm@11.6.2`; npm registry metadata says latest npm is `11.12.1` and supports Node `^20.17.0 || >=22.9.0`. `npm outdated -g --depth=0` shows `@openai/codex` wanted/latest `0.120.0` and global `npm` wanted/latest `11.12.1`. `/usr/local/bin/codex` is a custom wrapper that explicitly runs `/usr/local/opt/node@24/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js`, and `codex --version` reports `codex-cli 0.118.0`. Default Homebrew `/usr/local/bin/node`, `/usr/local/bin/npm`, and `/usr/local/bin/npx` point to `/usr/local/Cellar/node/25.2.1`; that default Node currently fails read-only execution because `libsimdjson.29.dylib` is missing, while Homebrew shows `node` `25.2.1` outdated to `25.9.0_2`, `node@24` installed as `24.14.1_1`, and `simdjson` versions `4.2.2` and `4.6.1`. Recommendation: no in-place npm update while Workspaceboard/Codex sessions are active; treat the broken default Node 25 path and Codex/npm updates as a scoped Mac mini runtime maintenance window. No Node/npm/Codex updates, config edits, or service restarts were performed.
- Workspaceboard Mac mini update at `2026-04-13 12:02 CDT` on `MacBookPro.lan`: MacBook `/Users/werkstatt/workspaceboard` carried the current `0.67` source as uncommitted local work while Mac mini source/runtime were still `0.63`. Validated the MacBook source with `node --check` for `server/index.js`, `assets/app.js`, `assets/management.js`, `assets/task-management-light.js`, and `assets/task-manager-phone.js`; PHP lint for `lib.php`, `workspaceboard_auth.php`, `api/network/addresses`, and `api/network/addresses.php`; and `git diff --check`. Committed and pushed `229c231 Update workspaceboard to v0.67` to `origin/main`, pulled it fast-forward on Mac mini, and reinstalled `com.koval.workspaceboard` with `./scripts/install_codex_dashboard_launchagent.sh 17878`. Mac mini now reports `board_version: 0.67`, host `Macmini.lan`; source repo is clean at `229c231` on both MacBook and Mac mini. Verified `task-manager-phone.html` returns HTTP `200` and `/api/network/addresses` reports Mac mini LAN address `192.168.55.17`. No Node/npm/Codex/Homebrew package updates were performed.
- Current decision style: when input is needed, surface one session at a time with `Needed`, `Next`, and `Decision` instead of dumping all waiting items together.
- Current git-start rule: before implementation in any git-backed workspace, check `git status` and pull latest with `git pull --ff-only` when clean. If dirty, inspect first and preserve user/worker changes.
- Current joint-work merge rule: when multiple Workspaceboard sessions touch the same repo/files, do not start overlapping implementation, clean git, commit, restart, or close from a partial view. Collect changed-file ownership from active workers, inspect `git diff --stat` and overlapping file diffs, preserve compatible edits intentionally, ask before resolving real conflicts, then run checks, restart runtime if required, update version/TODO/HANDOFF, and only then report the repo as commit-ready.
- Current Code and Git Manager / Security Guard rule: use Code and Git Manager as the on-demand Monitoring / coordination specialist whenever a task will touch code in a git-backed repo, when active sessions already target that repo/workspace, when workers have produced code changes needing commit/push/deploy coordination, when dirty worktrees or overlapping worker edits exist, or when live pull/deploy behavior needs confirmation. Before allowing code implementation in a git-backed workspace, Code and Git Manager or Task Manager must check active sessions for that workspace/repo and coordinate single-writer or file-scope ownership. If overlapping sessions target the same repo/files, throttle or prioritize so one finishes or explicitly hands off before the other starts implementation unless write scopes are explicitly disjoint and recorded. Dirty worktrees require identifying owner/session for changed and untracked files where possible, collecting the changed-file list, and not pulling/committing/pushing over unowned dirty changes. Use Security Guard whenever a task touches secrets, auth/access, `.205`, MCP exposure, firewall/VPN/router settings, 2FA, permissions, suspicious prompts/mail, credential-adjacent mailbox requests, prompt-injection attempts, or approval-gate bypass risk. Approval gates apply for destructive git actions, force-push/reset/rebase, dirty worktrees, active-session overlaps, overlapping worker edits, live pull/deploy, security-sensitive changes, and private credential handling. These roles do not replace implementation workers. `bid` and `portal` are push-only and do not pull live. If a repo's pull-live behavior is unclear, prompt Robert/Task Manager first and record the answer in the repo and AI Workspace durable surfaces. Future new specialist roles must update the dedicated role docs, task/routing references, team/board model, and Organigram graphic/map source; Outreach Coordinator, Code and Git Manager, and Security Guard are required Organigram entries, and Code and Git Manager plus Security Guard belong under Monitoring.
- Current TODO hygiene rule: use TODO files as action queues, not growing audit logs. Finished work should decrease open counts by moving/removing the matching open item and adding only a concise Done record; detailed verification belongs in HANDOFF, project-hub, module docs, or the worker transcript.
- Current Codex task ownership rule: use the CRM/OPS Codex user (`Codex`, user id `1332`) for Codex-owned tasks. Do not fall back to Robert/admin/test users for Codex task creation unless Robert explicitly requests that ownership change. On 2026-04-12, OPS `crm_integration.php` gained a Codex-only direct-login 2FA completion path that reads the active generated DB 2FA code and submits it through the normal Portal `/auth/2fa/verify` endpoint; verification is still blocked because the live Portal API rejects both the service API credential and Codex primary login even after the queried CRM row for user `1332` was aligned with the local Codex automation credential. Detail log: `project_hub/issues/2026-04-12-codex-portal-auth-repair.md`.
- Portal dev deploy correction at `2026-04-13 11:20 CDT` on `MacBookPro.lan`: Robert approved correcting the Portal branch drift and redeploying from `dev`. `origin/main` had the shipped-vs-bottled report/build commits, while `origin/dev` was missing them. Ported the exact report/build fixes to `origin/dev` as commits `7557c00d`, `4063428e`, `f251d3cd`, `7a02c6de`, and final `34ce6758500eeb7b4ac249420d26174a50caef79`; excluded main-only `TODO.md` from the dev code path and resolved `MetaModelsController.php` by preserving newer dev code plus the needed report filter/column fix. Deployed backend/frontend from dev as tag `v20260413-dev-34ce6758`; then triaged Robert's urgent login error and found the first clean frontend build had compiled an undefined API base, causing `/undefined/auth/login`. Rebuilt/deployed frontend only with the VPS production frontend env as `v20260413-dev-34ce6758-envfix` without printing secrets. Final live state: frontend `koval-crm-frontend:v20260413-dev-34ce6758-envfix`, backend `koval-crm-backend:v20260413-dev-34ce6758`; credential-free auth endpoint returned validation `422`, fresh browser-like `https://portal.koval-distillery.com/` returned `200`, bundle scan found no `/undefined` signature and found the expected Portal API base, and backend nginx showed a real `POST /auth/login` returning `202`. One mobile client still emitted stale `/undefined/user/profile/settings` and `/undefined/logs` shortly after the swap, consistent with an old in-memory tab; a follow-up 30-second frontend log window was clean for `/undefined`, `auth/login`, and `404` matches. DB/view verifier remains paused per the urgent login instruction. Detail log: `project_hub/issues/2026-04-13-portal-dev-deploy-branch-correction.md`.
- Current AI-Bridge auth note: `.205` access is verified with `admin@192.168.55.205` using the approved private credential reference `ai_workspace/.private/passwords/raetan.txt`, parsed as a prompt/label-style credential reference rather than a raw whole-file password. Never print the secret. `claude-user.txt` remains unverified for SSH. Use `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-10-205-auth-recheck.md`, `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-10-claude-205-tool-surface-discovery.md`, and `/Users/werkstatt/ai-bridge/bridge/traces/2026-04-10-claude-205-live-refresh-command.md` as the current source of truth before attempting `.205` work.
- Current OPS Codex task creation note: for non-interactive Robert-originated Codex task creation, use `/Users/werkstatt/ops/scripts/create_codex_task.php`. It uses the explicit `crm_create_task(..., ['allow_service_fallback' => true])` path, repairs duplicate open tasks by title or explicit task id, forces creator/owner/assignee metadata without printing secrets, and creates tasks silently by default. Verified refs: `366460`, `366486`, `363191`, `360626`, `363052`, `366499`, `366563`, `366564`, `366565`, and `366566`.
- High-importance manager-only workflow note: the AI Workspace Task Manager/monitor must not perform implementation or investigation itself. It must start or route the task to a visible board-managed worker session, verify from board status/history or tmux/session history that the worker actually started, and report only session routing/status in monitor chat. Substantive findings, diagnosis, implementation results, and final answers belong in the relevant worker session or a visible Task Management worker card.
- Hard manager-routing rule approved by Robert on 2026-04-12: keep `ws ai` as the overreaching manager. If work needs more than a quick status check or one command, route it into a visible Workspaceboard worker session and return to manager chat with the worker id. Throttling/queueing belongs in Workspaceboard; the manager accepts tasks, routes them, tracks one decision at a time, and does not implement.
- Visible correction record: AI worker session `7a2b187a` is the visible coordination transcript for this workflow correction. OPS worker session `16683383` is live in `/Users/werkstatt/ops`, titled `OPS AI Codex Kanban task 366212`, and should remain the OPS implementation surface.
- Closure record for AI worker `7a2b187a`: the workflow visibility correction has been recorded in `AGENTS.md`, `HANDOFF.md`, and `TODO.md`. The AI workspace root is Google Drive-synced and is not a git repository, so no git commit is possible here. This AI worker session can be closed after reporting that status.
- Closure record for AI worker `8363c1a0`: the MacBook Workspaceboard sync status cleanup has been recorded in `HANDOFF.md` and `TODO.md`; the current package is verified, the obsolete package is removed, and the MacBook package/install step was completed from Macmini.lan at `2026-04-10 19:21:06 CDT`. MacBookPro.lan now reports local `board_version=0.61`. Follow-ups at `2026-04-10 19:27:13 CDT` and `2026-04-10 19:31:27 CDT` rebuilt/reapplied the package with Workspaceboard HTML page access fixes and visible v0.61 index text; direct runtime HTML pages are fixed, while Apache still needs an admin/root reload to pick up the corrected host config.
- Follow-up record for AI worker `8363c1a0`: on `2026-04-11 12:43:58 CDT` from `RobertMBP-2.local`, direct runtime URLs still returned HTTP `200`, while Apache `http://127.0.0.1/workspaceboard/start.html` still returned HTTP `403`. `/usr/local/etc/httpd/httpd.conf` was backed up to `/usr/local/etc/httpd/httpd.conf.bak.workspaceboard-20260411-124301` and updated with `Require all granted` / PHP handler blocks for the real `/Users/werkstatt/workspaceboard` alias target; `apachectl -t` returned `Syntax OK`. The running Apache service is root-owned `system/homebrew.mxcl.httpd` PID `336`; `sudo -n apachectl graceful`, `launchctl kickstart -k system/homebrew.mxcl.httpd`, and `kill -HUP 336` are blocked by password/permission requirements, so the live Apache URL remains 403 until a local admin reloads the daemon.
- Completion record for AI worker `8363c1a0`: at `2026-04-11 12:47:23 CDT` from `RobertMBP-2.local`, the local admin reload landed; Apache error log recorded `Graceful restart requested, doing restart` at `12:46:46`. `http://localhost/workspaceboard/start.html` and `http://127.0.0.1/workspaceboard/start.html` now return HTTP `302` to the login referrer instead of HTTP `403`, which confirms the Apache route is working and the authenticated Workspaceboard start page is under `/workspaceboard/start.html`.
- Follow-up fix at `2026-04-11 12:49:13 CDT` from `RobertMBP-2.local`: `http://localhost/workspaceboard/task-management.html` loaded but stayed at `Board Loading...` because the already-loaded Apache alias bridge requested missing PHP API targets such as `/Users/werkstatt/workspaceboard/api/serve-mode.php` and `/Users/werkstatt/workspaceboard/api/management/overview.php`. Added compatibility wrappers for the aliased API paths: `api/status.php`, `api/serve-mode.php`, `api/management/overview.php`, `api/task-manager/history.php`, `api/task-manager/ensure.php`, and `api/task-manager/message.php`. PHP lint passes for all wrappers; unauthenticated localhost API checks now return JSON `401`/validation JSON instead of Apache `404`, so logged-in browser sessions should populate after refresh.
- Follow-up fix at `2026-04-11 12:54:46 CDT` from `RobertMBP-2.local`: inspected Macmini.lan read-only and confirmed the intended setup has live AI monitors `5909d11e` Task Manager and `d168f87c` Summary Worker. No Frank email automation was started or changed. On MacBook, the board only had stale closed AI metadata from April 8, causing AI Workspace to show `finished` and the Summary Worker/Summarizer role to be absent. Updated Workspaceboard so AI Workspace reports `monitor needed` instead of `finished` when AI monitors are absent, `monitor partial` if only one monitor is live, and `monitoring` when both Task Manager and Summary Worker are live. Updated `/api/task-manager/ensure` to create both local monitor sessions. Reinstalled the board runtime and started local MacBook monitors: Task Manager `0f99c595`, Summary Worker `df09cc20`; API now reports AI Workspace `{key: working, label: monitoring}` with both monitors live.

## Current Handoff (2026-04-10 weekend / Workspaceboard)

- Visible sync status recorded in AI worker session `8363c1a0` at `2026-04-10 19:03:00 CDT`:
  - Current machine is `Macmini.lan`, not the MacBook.
  - Macmini Workspaceboard runtime is live at `http://127.0.0.1:17878` and reports `board_version=0.61`.
  - `/Users/werkstatt/workspaceboard` is on `main` at `464b76a` and is ahead of `origin/main` (`fea07ed`) by one commit.
  - Workspaceboard source is not handoff-clean: `git status --short` currently shows 18 changed/untracked paths.
  - The staged MacBook sync package `tmp/workspaceboard-0.61-v104-macbook-sync.tgz` was verified against `/Users/werkstatt/workspaceboard`; the only package/source difference is intentional omission of `server/node_modules`.
  - Package SHA-256 after MacBook visible v0.61 / HTML access follow-up: `78e01ad4d61b99f92f2217f07c117aafb8230cdf105dd1ff9575f0074c8d884e`.
  - Obsolete package `tmp/workspaceboard-0.60-v103-macbook-sync.tgz` was removed from the synced AI workspace.
  - 2026-04-10 19:21:06 CDT (Machine: Macmini.lan): MacBookPro.lan source/runtime were updated from `tmp/workspaceboard-0.61-v104-macbook-sync.tgz`, the old `com.koval.codex-dashboard` LaunchAgent was unloaded/disabled to avoid port collision, the new `com.koval.workspaceboard` LaunchAgent was installed and is running, and MacBook local `http://127.0.0.1:17878/api/status` returns `board_version=0.61`.
  - 2026-04-10 19:27:13 CDT (Machine: Macmini.lan): MacBookPro.lan source/runtime were updated again for Workspaceboard HTML page access. Direct runtime pages `http://127.0.0.1:17878/start.html`, `task-management.html`, `workspaceboard.html`, `todos.html`, `history.html`, and `analytics.html` all return HTTP `200` without exposing PHP preambles. MacBook Apache config `/usr/local/etc/httpd/httpd.conf` was backed up to `/usr/local/etc/httpd/httpd.conf.bak.workspaceboard-html-20260410-192456` and corrected on disk; `apachectl -t` returns `Syntax OK`, but reload is blocked from SSH because `sudo -n apachectl graceful` returns `sudo: a password is required`.
  - 2026-04-10 19:31:27 CDT (Machine: Macmini.lan): MacBookPro.lan source/runtime were updated again so `http://127.0.0.1:17878/` and `/index.html` show `Codex Workspace Board v0.61` instead of `v0.49`; `http://127.0.0.1:17878/workspaceboard/start.html` returns HTTP `200`. Apache `http://127.0.0.1/workspaceboard/start.html` still returns HTTP `403`; live error log reports `AH01630: client denied by server configuration: /Users/werkstatt/workspaceboard/start.php`. The running Apache master is root-owned system LaunchDaemon `homebrew.mxcl.httpd`; `sudo -n apachectl graceful` and `sudo -n /usr/local/bin/brew services restart httpd` both return `sudo: a password is required`, and `osascript ... with administrator privileges` over SSH returns `execution error: The administrator user name or password was incorrect. (-60007)`.
  - 2026-04-11 12:43:58 CDT (Machine: RobertMBP-2.local): MacBook local runtime still serves `http://127.0.0.1:17878/` and `http://127.0.0.1:17878/workspaceboard/start.html` with HTTP `200`; Apache still serves `http://127.0.0.1/workspaceboard/start.html` with HTTP `403` until reload. The config now also grants and sets PHP handlers for the real alias target `/Users/werkstatt/workspaceboard`; backup is `/usr/local/etc/httpd/httpd.conf.bak.workspaceboard-20260411-124301`; `apachectl -t` returns `Syntax OK`. Non-interactive/adminless reload attempts remain blocked (`sudo -n` password required, launchctl kickstart operation not permitted, root PID HUP operation not permitted).
  - 2026-04-11 12:47:23 CDT (Machine: RobertMBP-2.local): local admin reload completed; Apache log shows graceful restart at `12:46:46`. `http://localhost/workspaceboard/start.html` now returns HTTP `302` to `/login/index.php?referrer=workspaceboard%2Fstart.html`, confirming the prior 403 is resolved and the desired localhost route is active behind the auth gate.
  - 2026-04-11 12:49:13 CDT (Machine: RobertMBP-2.local): fixed the `Board Loading...` / disabled action console state by adding PHP wrapper entrypoints for the Apache alias API targets that were missing on disk. Verified `api/status.php`, `api/serve-mode.php`, `api/management/overview.php`, `api/task-manager/history.php`, `api/task-manager/ensure.php`, and `api/task-manager/message.php` pass `php -l`; unauthenticated localhost API requests now return JSON instead of Apache `404`.
  - 2026-04-11 12:54:46 CDT (Machine: RobertMBP-2.local): read-only SSH check of Macmini.lan confirmed live monitor model: Task Manager `5909d11e` and Summary Worker `d168f87c` were running there; Frank automation was not touched. MacBook board state was corrected so AI Workspace is no longer `finished` when monitors are missing. `/api/task-manager/ensure` now starts both monitor roles locally, and MacBook now has local Task Manager `0f99c595` plus Summary Worker `df09cc20`; `http://127.0.0.1:17878/api/management/overview` reports AI Workspace `monitoring`.
  - Current MacBook sync package available through the synced AI workspace: `tmp/workspaceboard-0.61-v104-macbook-sync.tgz`.

- Timestamp: 2026-04-10 19:04:01 CDT
- Machine: Macmini.lan
- Workspaceboard source repo: `/Users/werkstatt/workspaceboard`
- Runtime URL: `http://127.0.0.1:17878`
- Local Apache UI: `http://localhost/workspaceboard/task-management.html`
- LAN Apache UI: `http://192.168.55.17/workspaceboard/task-management.html`
- Installed runtime: `board_version=0.61`
- Current task-management asset cache key: `v104`
- Runtime reinstall command after source changes: `cd /Users/werkstatt/workspaceboard && ./scripts/install_codex_dashboard_launchagent.sh 17878`
- Validation completed on Macmini:
  - `/usr/local/opt/node@24/bin/node --check server/index.js`
  - `/usr/local/opt/node@24/bin/node --check assets/management.js`
  - `php -l task-management.html`
  - `curl http://127.0.0.1:17878/api/status` returned `board_version: 0.61`

### Workspaceboard Notes

- Task Manager and Summary Worker are coordinator sessions and should not appear as worker decision items.
- Summary Worker should display as `monitoring`, not as a user-input blocker.
- Latest source-side fixes exclude Summary Worker from Work Queue fallback selection, keep recently-working live Codex sessions from being marked `finished` just because the reusable `/skills` prompt is visible, stop hiding real waiting workers as "handled", and restore normal iPhone page scrolling on Task Management.
- The page may need a hard reload after install because the current management asset cache key is now `v104`.
- MacBook push/sync when online:
  - wait for Google Drive sync if using synced `ai_workspace` notes
  - copy/pull `/Users/werkstatt/workspaceboard` source changes to the MacBook workspaceboard repo
  - run `./scripts/install_codex_dashboard_launchagent.sh 17878` on MacBook
  - verify `http://127.0.0.1:17878/api/status` returns `board_version: 0.61`
  - verify `http://localhost/workspaceboard/task-management.html` loads `assets/management.js?v=104`
  - if direct SSH is still unavailable, use synced package `tmp/workspaceboard-0.61-v104-macbook-sync.tgz` from `ai_workspace` as the source snapshot for MacBook restore/install.

### Live Worker Sessions Started

- `8a4321d2` — Lists communications setup strategy — workspace `lists`
- `c64c159c` — BID finance/report workflow planning — workspace `bid`
- `79d25eb6` — Salesreport AI reporting workflow plan — workspace `sales`
- `42d80bb0` — OPS outreach dashboard card follow-up — workspace `ops`
- `edb77ab0` — Frank actual inbox triage — workspace `frank`
- Existing active worker sessions:
  - `4dc9c536` — AI-Bridge onboarding and Braincloud bridge review
  - `56fd7397` — Frank Angele cleanup and review
- Existing coordinator sessions:
  - `5909d11e` — Task Manager
  - `d168f87c` — Summary Worker
- Current visible correction / OPS work pairing:
  - `7a2b187a` — AI workflow visibility rule correction — workspace `ai`
  - `16683383` — OPS AI Codex Kanban task `366212` — workspace `ops` — status `working` / runtime `live`
  - AI worker `7a2b187a` closure status: complete; no git commit possible in AI workspace because this folder is not a git repo.

### Weekend Operating Notes

- Keep Task Manager as coordinator only.
- Keep Summary Worker as summarizer only; summaries should be concise, user-facing, and should not end in ellipses or cut off words.
- When a worker reaches `waiting`, answer that worker, move it back to working, and rotate to the next worker. Do not run implementation work inside Task Manager.
- Frank inbox triage and Angele inbox cleanup are separate workstreams.
- Do not print secrets from `.private/passwords`.

## Current Handoff (2026-04-07 ai_workspace)

- Timestamp: 2026-04-07 17:26:56 CDT
- Machine: Macmini.lan
- Workspace: `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace`
- Sync mode: Google Drive workspace, not a git repo
- Working tree clean?: n/a

### Current Status

- `TODO.md` is the active queue file.
- `ToDo-append.md` is present and currently empty other than the header.
- Open `TODO.md` workstreams are:
  - AI workspace board build
  - Email archive transfer follow-up
  - Salesreport report automation + hitlist optimization
- `project_hub/INDEX.md` last updated on `2026-04-07 13:05:26 CDT` and currently lists 11 open initiatives.
- Nested repo status:
  - `screenbox` is clean on `main`.
  - `external/mempalace` has local uncommitted changes in `mempalace/entity_detector.py` and `mempalace/miner.py`, so those changes are not pushed anywhere yet.

### Immediate Notes

- The dashboard count issue is real: the parser currently counts every `- ` bullet inside `## In Progress`, including nested directive bullets, as a separate in-progress task.
- Source location: `codex_dashboard/server/index.js`, function `parseTodoMarkdown()`.
- That is why you can see an inflated value like `25 tasks in progress` even though the section is really a few projects with many subitems.
- The dashboard port mismatch is fixed in the synced workspace source: `codex_dashboard/server/index.js` now defaults to `17878`.
- The dashboard server now resolves `tmux` by absolute path instead of assuming it is on `PATH`; this fixed the MacBook `terminal not connected` state where `tmux_available` was false under a minimal launch environment.
- Current limitation: the MacBook board runtime does not run cleanly on Node `v25.2.1` because `node-pty-prebuilt-multiarch` fails to provide/load `pty.node` there. The working fallback is Node `v24.14.0` for the board runtime until that dependency stack is updated.
- Machine-local note: the installed LaunchAgent/runtime under `~/Library/LaunchAgents/com.koval.codex-dashboard.plist` and `~/.codex-dashboard-launch/` does not sync through Google Drive.
- After the MacBook sees the updated `ai_workspace` files, run `./scripts/install_codex_dashboard_launchagent.sh 17878` there and verify `http://127.0.0.1:17878/api/status`.
- Do not assume `external/mempalace` is current on the MacBook unless its changes are separately committed and pushed.

### Next Step on MacBook

- Wait for Google Drive sync to finish, then re-open `AGENTS.md`, `HANDOFF.md`, and `TODO.md`.
- Reinstall the local dashboard LaunchAgent from the synced workspace:
  - `./scripts/install_codex_dashboard_launchagent.sh 17878`
- Verify the board is listening on the correct port:
  - `curl -fsS http://127.0.0.1:17878/api/status | head`
- Re-open `TODO.md`, `HANDOFF.md`, and `project_hub/INDEX.md` after sync completes.
- If resuming dashboard work, fix the TODO parser to count only top-level `In Progress` bullets.
- If resuming ops work, prioritize Mitch archive verification first.

## Previous Handoff Archive

### 2026-03-04 Eventmanagement

- Timestamp: 2026-03-04
- Machine: Macmini.lan
- Repo: `/Users/admin/Documents/GitHub/eventmanagement`
- Branch: `main`
- Pushed commit: `f790ec1`
- Remote status: `origin/main` updated

### Completed

- Implemented staged lifecycle for event support requests:
  - `intake_received`
  - `parameters_sent`
  - `negotiation`
  - `approved`
  - `denied`
  - `deleted`
- Added lifecycle schema support and auto-ensure columns in `config.php`.
- Updated dashboard/list filtering in `index.php` to use `lifecycle_stage`.
- Removed "Suggested Collab" nav/action flow.
- Added actions in `action_handler.php`:
  - `send_parameters`
  - `move_negotiation`
  - `create_ops_event`
- Added OPS draft event creation + link via `ops_event_id`.
- Updated detail/list views for stage badges, stage actions, denied reason, and OPS event button.
- Fixed detail-view data bug (`$all_support_options` mismatch in `request_details.php`).
- Added workflow documentation:
  - `docs/project_overview.md`
  - linked from `README.md`
- Updated `TODO.md` and cleared moved items from `ToDo-append.md`.

### Validation

- PHP lint passed for all PHP files:
  - `find . -name '*.php' -print0 | xargs -0 -n1 php -l`

### Follow-ups

- Tighten customer-facing email copy for each lifecycle stage.
- Add direct OPS event-details deep link once target route is confirmed.
- Run Chromium pass on live after deploy and capture UI regressions.

### 2026-03-02 MacBook Git Auth

- Timestamp: 2026-03-02 09:49:08 CST
- Machine: MacBookPro.lan
- Target machine: Macmini.lan (`admin@Macmini.lan` / `ssh admin-macmini`)
- Scope: bi-directional git auth fix for `ops`, `portal`, `forge`, `importer`, `contactreport`
- Status: auth diff complete; MacBook works with HTTPS+Keychain, Macmini SSH session fails HTTPS credential lookup (`-25308`)

### Auth Diff Summary (Confirmed)

- On MacBook (`robert`):
  - Repos are HTTPS remotes (`https://github.com/robs1412/<repo>.git`).
  - `credential.helper=osxkeychain`.
  - `git ls-remote origin` works in all target repos.
  - `ssh -T git@github.com` fails (`Permission denied (publickey)`), so SSH GitHub auth is not configured/usable here.
- On Macmini via SSH (`admin`):
  - Repos are also HTTPS remotes + `osxkeychain`.
  - `git ls-remote origin` fails with:
    - `failed to get: -25308`
    - `fatal: could not read Username for 'https://github.com': terminal prompts disabled`
  - `ssh -T git@github.com` also fails (`Permission denied (publickey)`).

### Root Cause

- macOS Keychain-backed HTTPS credentials are available in the interactive MacBook context but not in the non-GUI SSH context on Macmini.
- Both machines currently lacked working SSH-to-GitHub key auth at that time.

### Action Plan Captured Then

1. Verify baseline on Macmini:
   - `ssh -o BatchMode=yes -T git@github.com`
   - `GIT_TERMINAL_PROMPT=0 git -C /Applications/MAMP/htdocs/ops ls-remote origin`
2. Create/attach a dedicated GitHub SSH key on Macmini and add public key to GitHub account.
3. Add/confirm `~/.ssh/config` entry for GitHub on Macmini:

```sshconfig
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github_modules
  IdentitiesOnly yes
```

4. Re-test SSH auth:
   - `ssh -o BatchMode=yes -T git@github.com`
5. Convert module remotes to SSH on Macmini:

```bash
for r in /Applications/MAMP/htdocs/ops /Applications/MAMP/htdocs/portal /Applications/MAMP/htdocs/forge /Applications/MAMP/htdocs/importer /Applications/MAMP/htdocs/contactreport; do
  [ -d "$r/.git" ] || continue
  name="$(basename "$r")"
  if [ "$name" = "contactreport" ]; then
    git -C "$r" remote set-url origin git@github.com:robs1412/contactreport.git
  else
    git -C "$r" remote set-url origin "git@github.com:robs1412/${name}.git"
  fi
  git -C "$r" remote -v
done
```

6. Verify per repo:
   - `git -C <repo> ls-remote origin`
   - `git -C <repo> push --dry-run origin <branch>`

### Repo State Snapshot (at 2026-03-02 handoff time)

- `ops` `main` HEAD `c3805f9`
- `portal` `main` HEAD `88fdd30e`
- `forge` `main` HEAD `509f616`
- `importer` `main` HEAD `8964958`
- `contactreport` `master` HEAD `a98244e`

## Single-Writer Rule

- One machine/session writes to a repo at a time.
- Before handoff: commit or stash, push, then send this note.

## Handoff Template

- Repo:
- Branch:
- Last commit SHA:
- Working tree clean? (`yes`/`no`)
- Summary of what changed:
- Next step to run:
- Safe for you to continue? (`yes`/`no`)

## Quick Command

From inside a repo:

```bash
./handoff.sh
```

Or with an explicit path:

```bash
./handoff.sh /Applications/MAMP/htdocs/ops
```
