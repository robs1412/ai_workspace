# TODO — ai_workspace

Updated: 2026-04-14 21:57:30 CDT (Machine: Macmini.lan)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- OpenWrt/LuCI upgrade decision:
  - Evaluation-only work is complete; official and custom `25.12.2` WRT3200ACM images passed validation-only `sysupgrade -T`, with no flash, reboot, firewall/VPN reload, or router config change performed.
  - Decision: Robert must explicitly approve or reject flashing the staged custom package-preserving image and accept the reboot/connectivity-risk window after rollback prerequisites are reviewed.

- Email archive transfer follow-up:
  - Decision prompt prepared 2026-04-14 after reviewing only AI Workspace TODO/HANDOFF/project note; no mailbox, credential, or `imapsync` access was used.
  - Needed: Robert needs to decide whether to continue the Mitch Donohue archive transfer now that the 2026-04-10 project-note reassessment says both source and destination IMAP logins worked, while destination counts remain incomplete (`Mitch-Inbox`, `Mitch-Sent`, `Drafts`, `Spam`, `Trash`, and `All Mail` short by `1`).
  - Next: if approved, run a separate security-gated email/archive worker on `Macmini.lan` to rerun or locate final `imapsync` completion logs, rerun only the intended `UserArchive/Mitch_Donohue/...` mappings if needed, verify counts, and close the project log only after completion evidence exists.
  - Decision: Robert, do you approve continuing the Mitch archive verification/rerun worker on Mac mini, or should this remain parked with the source account retained and not deleted?

## Backlog
- Build in-house outreach events module (parity with Events/Market Events):
  - outreach events should work like Events + Market Events.
  - tie outreach events to shifts (minimum one shift; allow multiple).
  - keep/use existing shift notifications behavior.
  - target Connecteam replacement with equal-or-better core functionality.
  - improve over Connecteam by linking directly to accounts, user logins, and activity tracking.
  - keep users in one system (no dual logins) and keep operations in-house.
- Trainual first module: OPS Market Events workflow planning only.
  - Recommendation: make `ops` / Market Events the first Trainual module because it is already called out as a needed demo, is close to the outreach-events/Connecteam replacement work, and exercises the approved manual recording standard before expanding to `salesreport`, `contactreport`, or `portal`.
  - Scope now: produce the module outline, user-facing walkthrough script, recording checklist, safe demo-data notes, output-location convention, and acceptance checklist.
  - Acceptance checklist: confirm target audience and workflow boundaries; define 5-8 walkthrough steps; list exact screens/actions to show; identify safe demo records or mocked data; note required login/role state without exposing credentials; specify output path under `ai_workspace/recordings/`; include recording notes template with mocked/seeded-flow disclosure; include Robert approval checkpoint before any recording or publishing.
  - Out of scope until explicitly requested: recording, external publishing, code changes, live data mutation, and broad cross-module Trainual rollout.
  - After this first module is accepted, decide whether a dedicated Codex Trainual skill is warranted for repeated module production.
- Get PHP list cleaned (legacy soft delete for send history).
- Clean distributor accounts.
- Bid data import plan.
- Check data-importer:
  - Julia imports the salesreports manually right now from XLS and other data sources.
  - evaluate whether AI-assisted import can streamline the workflow and improve data accuracy.
- Review: `https://papers.koval.lan/teams/it/research.html`.
- Imported from `project_list-import.txt`:
  - BID ETL processes: define extract/transform/load flow, schedule, and validation.
  - Google Ads issues: audit and fix campaign/account problems.
  - Web analytics funnel reporting for `koval-distillery.com` (Dmytro analytics + GA-style funnel view).
  - Portal production audit enhancements:
    - extended modification trails for bottling/distillation records
    - monthly report for edits affecting prior-month bottlings/distillations
    - report for shipped-vs-bottled mismatches
    - report for mashes using `<2000 lb` grain and product/grain mismatch logic
  - Review IT planning docs and decide transfer/deprecation plan for GitLab:
    - `https://papers.koval/teams/it/task-queue.html`
    - `https://papers.koval/teams/it/roadmap.html`
    - `https://papers.koval.lan/teams/it/dashboard.html`
  - Check MacBook power management logs and wake causes.
  - Fix OPS <-> Portal SSO/login persistence (including next-day logout behavior).
  - Salesreport user adoption/access:
    - track usage by login
    - ensure required state/access controls for named sales users
  - Review event strategy notes: `https://docs.google.com/document/d/1EaHH97GJ_9ztMNtWaEp-abGUHdVqVcyvJWkUjko5euc/edit?tab=t.0`
  - Manage COT team in OPS and finalize Connecteam replacement plan.
  - OPS market improvements:
    - create account/contact from OPS (activity/receipt style flow)
    - decide OPS -> salesreport data flow and entry/reporting boundaries
  - Unified user activity reporting across systems:
    - Portal activity, task stats, shift/check-in stats
    - OPS/salesreport/contactreport/BID/automation usage
    - optional Gmail/Gemini admin usage overlays
  - Systems usage recurring operations:
    - importer roster update cadence
    - distributor inventory recurring checks
    - monthly task stats send-out
    - events/task stats review cadence
    - barrel sample page manual and follow-up
    - PHPList/Shopify/Square signup reviews
    - monthly/quarterly WH + distribution salesreport checks
    - BID data refresh cadence
  - Google Postmaster monitoring: `https://postmaster.google.com/u/0/dashboards#do=kovaldistillery.com&st=userReportedSpamRate&dr=7`
  - Google Cloud security hardening initiative:
    - key inventory, dormant-key cleanup, API restrictions, least privilege, key rotation/expiry policies
    - update Essential Contacts and billing anomaly/budget alerts

## Done

- **2026-04-15** AI Workspace legacy archive cleanup recovery completed.
  - Verified the encrypted vault retained the Mac mini legacy archive payload, loose Mac mini/MacBook archive folders are gone, embedded `screenbox`/`external/mempalace` copies are vaulted legacy/audit material only, and no secret contents were read or printed.

- **2026-04-14** Earth Day Forge/lists workflow reconciled.
  - Account-send draft `#550` remains draft-only, Vegas distributor inclusion and Johnson Brothers MN old-distributor cleanup were verified, and Forge/phpList list sync work completed without campaign send.

- **2026-04-14** `/lists/` phpList CRM activity logging backlog item reconciled.
  - Completed/deployed in `/Users/werkstatt/lists` commit `d35aabe1b249052539446b407a8061e00b6b03b0`; first confirmed apply for campaign `545` created `87` CRM E-mail activities and follow-up dry-run returned `0` pending.

- **2026-04-14** OpenWrt and LuCI 25.12.2 evaluation parked/closed.
  - Official and custom image validation-only work is complete; custom package-preserving image is the preferred candidate. No router access or network-device action was performed during this closeout check. Remaining decision: Robert must explicitly approve or defer flashing the staged custom image after rollback prerequisites are reviewed.

- **2026-04-14** Communications Manager task routing TODO closed.
  - Read-only OPS metadata verification at 21:55 CDT confirmed Square `363191`, Shopify `360626`, and Forge donations `363052` are active/not deleted with creator `1`, owner `1332`, and assignee `1332`. No reassignment, task creation, external newsletter/email send, or Forge/lists/donations implementation was performed. Follow-up remains separate: a Forge/lists worker should handle any approved `/donations` email pull/list workflow.

- **2026-04-14** Heritage distributor un-blacklist backlog closed.
  - Salesreport completed Robert-approved Path A in commit `8281602`: seven active RNDC replacement contacts were linked to Heritage account `11884`; old Heritage-domain contacts stayed blacklisted/suppressed, no PHPList list sync or email send was performed, and the audit is recorded in `/Users/werkstatt/salesreport/doc/heritage-rndc-contact-link-update-2026-04-14.md`.

- **2026-04-14** Trainual backlog reduced to first concrete module.
  - Broad cross-module Trainual backlog was narrowed to an `ops` / Market Events planning slice with recording/publishing/code work explicitly out of scope.

- **2026-04-14** KOVAL VPN / Bitdefender takeover follow-up closed.
  - Robert approved closeout via Task Manager. Read-only evidence captured Lakehouse Wi-Fi path instability (`en0` at `192.168.4.41`, gateway/DNS `192.168.4.1`, DNS working, high jitter, low `networkQuality` responsiveness) and kept the work separate from OpenWrt/LuCI upgrade work. No Bitdefender, VPN profile, router VPN, firewall/VPN service, or network equipment changes were made.

- **2026-04-14** Disabled Codex daily check-in reminder notifications.
  - Live Portal `notifications_user_settings.id=7981` for Codex user `1332` and `checkins.reminder` now has `channel_email=0` and `is_enabled=0`; global human reminder rule remains active. OPS bookkeeping commit pushed as `/Users/werkstatt/ops` commit `7a5ffc9`; project log: `project_hub/issues/2026-04-14-codex-daily-checkin-notifications.md`.

- **2026-04-14** Digital Office project/task/work-record source-of-truth proposal.
  - Docs-only proposal created at `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md` and linked from `ai-digital-office.md` / `project_hub/INDEX.md`; first read-only Workspaceboard prototype was implemented and pushed as `/Users/werkstatt/workspaceboard` commit `68df99c`, live at `http://localhost/workspaceboard/digital-office.html`, with no Papers, `.205`, OPS/Portal schema, production DB, notification, or MCP writes.

- **2026-04-14** Task Manager worker closeout sweep and Code/Git cleanup.
  - Closed 19 finished/superseded board sessions, committed/pushed Workspaceboard worker changes as `/Users/werkstatt/workspaceboard` commit `af631f4`, and committed/pushed BID preflight/cadence changes as `/Users/werkstatt/bid` commit `8e1bc80`; both repos are clean on `main...origin/main`.
  - Workspaceboard closure covered expandable email decision workers, Latest Output height stabilization, and new-session attachment documentation/verification.

- **2026-04-14** Code and Git Manager active-session throttle rule.
  - Updated Code and Git Manager docs and AI Workspace policy so Task Manager/Code and Git Manager check active sessions before git-backed implementation, coordinate single-writer or disjoint file-scope ownership, throttle overlapping sessions, and block pull/commit/push over unowned dirty changes.

- **2026-04-14** Worker role specialist/team map follow-up.
  - Added Security Guard as a Monitoring / coordination specialist in `worker_roles/`, updated the operating model, role references, AGENTS/HANDOFF policy pointers, and Workspaceboard organigram map/snapshot. No secrets, code commit, push, deploy, or runtime restart.

- **2026-04-14** Deleted legacy `ai_workspace/codex_dashboard`.
  - Removed only the synced legacy source directory after confirming active Workspaceboard v0.69 runs from `/Users/admin/.workspaceboard-launch` and `/Users/werkstatt/workspaceboard`; old runtime/LaunchAgent files, Workspaceboard source, scripts, logs, and unrelated cleanup candidates were left in place.

- **2026-04-14** AI Digital Office coordination note.
  - Created and expanded `ai-digital-office.md` to track Claude/Frank feedback, Dmytro's Digital Office reference, KOVAL/Raetan `.205` mapping, public Git/code leads, papers investigation gates, Screenbox migration/security notes, related board sessions, the stuck-session/restart recovery idea, and a proposed object model.
  - Moved the standalone `Claude at work and Codex integration` backlog item under the Digital Office umbrella; AI-Bridge now holds supporting plans/traces only, and remaining `.205`, papers, MCP/workspace bridge, and Claude feedback follow-up must be routed as Digital Office work with the existing approval gates.

- **2026-04-14** Worker role documentation follow-up verified.
  - `worker_roles/operating-model.md` now holds exact operating prompts, role classes, call signs/routing phrases, approval gates, durable memory surfaces, recent specialist roles, organigram directives, and BID finance task `#1185` answer-recording gate; individual role docs now point back to that active reference and preserve only true remaining role-specific gaps.

- **2026-04-14** AI workstation/sync transition follow-up audit.
  - Docs-only audit recorded in `project_hub/issues/2026-04-12-ai-workstation-sync-transition.md`; recommendation is to mark `ai_workspace/codex_dashboard` legacy/read-only after launcher/reference checks and handle other code/generated/runtime candidates in an explicit cleanup pass.

- **2026-04-13** Security hardening review project docs-only closeout.
  - Reviewed Codex/agent malicious-prompt handling docs, workstation SSH posture, and live `koval@ftp.koval-distillery.com` SSH posture without changing client config or server SSHD.
  - Confirmed MacBook publickey-only access to `admin-macmini` now succeeds at `192.168.55.17`; live server key access works but server still advertises password auth and uses OpenSSH `8.0p1` / non-PQ `curve25519-sha256`.
  - Created silent Codex follow-up OPS task `366581` due `2026-04-22` for client-side SSH hardening review across Mac mini, M4 Mac mini, and MacBook.
  - Project note: `project_hub/issues/2026-03-07-security-hardening-review.md`.

- **2026-04-13** iPhone Task Manager chat page.
  - Completed in Workspaceboard worker `1357a9e2` and pushed as `156c3c3`; phone page is now a lightweight Task Manager interaction surface, remote login-gated access is enabled, and the stale status-label fix is included.

- **2026-04-13** Mac mini terminal npm/Codex repair.
  - Fixed broken `/usr/local/bin/node`/`npm` by reinstalling Homebrew `node` to `25.9.0_2`, then updated global `@openai/codex` to `0.120.0`; plain terminal `npm -v` now reports `11.12.1` and `codex --version` reports `codex-cli 0.120.0`.

- **2026-04-13** Mac mini npm update follow-up.
  - Read-only SSH/runtime check completed from AI Workspace after office LAN reachability returned. No Node/npm/Codex/Workspaceboard updates or service restarts were made.
  - Recommendation: do not perform an in-place npm update during active Workspaceboard/Codex runtime; schedule a scoped Mac mini runtime maintenance step if Robert wants to fix the broken default Homebrew Node `25.2.1` path and update Codex/npm.

- **2026-04-12** ToDo-append intake: evaluate Infisical for password/key management.
  - AI-Bridge/security worker completed the evaluation in `/Users/werkstatt/ai-bridge/INFISICAL-CREDENTIAL-MANAGEMENT-EVALUATION.md`.
  - Recommendation: treat Infisical as a controlled secrets-management pilot candidate, not as an immediate replacement and not primarily as an SSH target.
  - No secrets were migrated, printed, or exposed, and no credential storage was changed.

- **2026-04-12** ToDo-append intake: Workspaceboard Security Guard monitor.
  - Added `Security Guard` as a standard Workspaceboard AI monitor kept live by `/api/task-manager/ensure`.
  - Security Guard enforces security directives, watches for prompt-injection, unauthorized folder/credential access, unwanted data leakage, and risky email-worker behavior, and routes pause/quarantine/escalation through Task Manager.
  - Workspaceboard source change is in `/Users/werkstatt/workspaceboard`; it appears in `task-management-light.html` under Monitoring, separate from worker `118db6da`.

- **2026-04-12** ToDo-append intake: update npm on MacBook and Mac mini.
  - MacBook handled safely for the workspace nvm runtime: `nvm` Node `v22.19.0` npm updated from `10.9.3` to `11.12.1` at `/Users/robert/.nvm/versions/node/v22.19.0/bin/npm`.
  - Did not update `/usr/local` system npm because default Node is `v14.19.3` and latest npm `11.12.1` requires Node `^20.17.0 || >=22.9.0`; did not update nvm Node `v24.14.0` npm because live Codex sessions use that prefix.
  - Verification: default `/usr/local/bin/npm` remains `6.14.17`, nvm Node `v24.14.0` npm remains `11.9.0`, `codex --version` reports `codex-cli 0.120.0`, and Workspaceboard `http://127.0.0.1:17878/api/status` returned `ok: true`.
  - Mac mini remains blocked as a separate follow-up because SSH to `admin-macmini` / `192.168.55.17:22` timed out.

- **2026-04-12** IKEv2/WireGuard parity check and router SSH follow-up.
  - Restored key-based router management from this MacBook with dedicated key `~/.ssh/id_ed25519_openwrt_192_168_55_1` and local SSH aliases `koval-openwrt` / `openwrt-router`; router backup before public-key append is `/root/codex-backups/sshkey-20260412-100945`.
  - Verified IKEv2 active at `2026-04-12 10:31 CDT`: local `ipsec0` address `10.57.57.12`, route to `192.168.55.1` via `ipsec0`, public IP `205.178.117.216`, router ping and TCP `22`/`53`/`80`/`443` all OK, and key SSH works through both router aliases.
  - Router `swanctl --list-sas` shows `koval-ikev2` established for EAP identity `robert-macbook` with remote `10.57.57.12/32`; pool `koval-ikev2-pool` shows one assigned lease from expected `10.57.57.0/24`.
  - WireGuard service `koval-robert-wg0-fresh` was disconnected in `scutil`; router still had a recent `wg0` peer handshake history, but local traffic was routed over `ipsec0`, not WireGuard.
  - No router password change, firewall reload, VPN service reload, WireGuard disable, or StrongSwan restart was performed. Result: IKEv2 can replace WireGuard as the primary path, with WireGuard retained as fallback.

- **2026-04-12** Closed the Salesreport MemPalace pilot.
  - Robert approved killing the local Salesreport MemPalace pilot after worker `e25751cd` recommended not expanding it inside `salesreport`.
  - Evidence: the helper existed only as a short-lived repo-local experiment and there is no current useful Salesreport implementation to expand.
  - Future memory/retrieval experiments should stay in AI Workspace or a deliberate cross-repo tool, not as ad hoc Salesreport repo-local scripts.
  - Closed board session `e25751cd`.

- **2026-04-12** Trainual recording standard rollout decision closed.
  - Robert approved the Trainual Recording Standard as the default for Trainual/user-facing recording workflows across core modules unless a recording request explicitly says otherwise.
  - Updated `AGENTS.md` and `HANDOFF.md` with the approved default rule.
  - Next implementation step requested: create an OPS/Codex task for 2026-05-01 to start Trainual work, with Robert Birnecker and Sebastian Saller assigned in addition to Codex.

- **2026-04-12** ToDo-append intake: AI workstation setup decision.
  - Decision record created: `AI_WORKSTATION_SYNC_PLAN.md`.
  - AI-Bridge cross-link created: `/Users/werkstatt/ai-bridge/WORKSTATION-SYNC-DECISION.md`.
  - Recommendation: move Robert's daily workstation role to the Mac Mini M4 2025; keep the 2018 Mac mini on macOS as the near-term AI server; keep the MacBook Pro 2019 as portable fallback/client; keep Raetan/Claude as server-side analysis and planning support.
  - Linux on the 2018 Mac mini is deferred to a later reversible pilot after the macOS role split is stable.
  - Sync boundary recorded: Google Drive `ai_workspace` for planning/intake/role docs/project hub/handoff, `/Users/werkstatt` repos for code, git by default for source sync, SSH/rsync for deliberate non-git handoff, and runtime/secrets as machine-local.
  - Board worker: `0c0ea2cf` (`2026-04-12 AI workstation setup decision`).

- **2026-04-12** Frank/Avignon medium-independent task flow approved.
  - Robert approved the medium-independent model after the decision-option emails.
  - Frank and Avignon should now independently ingest, route, execute, log, and file clearly bounded low-risk internal email-derived tasks so work does not stay stuck in inboxes.
  - Approval gates remain for external-sensitive sends, finance/legal/security/auth, credentials, production-impacting changes, destructive operations, suspicious email, ambiguous ownership/recipient intent, or policy conflicts.
  - Recorded in `AGENTS.md`, `HANDOFF.md`, `frank/AGENTS.md`, `frank/WHAT_TO_DO.md`, `frank/HANDOFF.md`, `avignon/AGENTS.md`, and `avignon/HANDOFF.md`.

- **2026-04-11** ToDo-append intake: Frank and Avignon persona outreach.
  - Frank emailed Robert and Avignon emailed Sonat for persona guidance from the MacMini single-writer path.
  - MacMini logs confirmed Sonat replied to Avignon and Robert replied to Frank on 2026-04-11.
  - Incorporated Sonat's guidance into `avignon/PERSONA.md` and Robert's guidance into `frank/PERSONA.md`.
  - Sent decision-option emails asking Sonat and Robert whether narrow low-risk task auto-approval should become the default, or whether draft-only/manual approval should remain the default.
  - Frank task id: `frank-decision-options-task-flow-2026-04-11`; Avignon task id: `avignon-decision-options-task-flow-2026-04-11`.
  - Board worker: `be926e66` (`2026-04-11 Frank/Avignon persona outreach`).

- **2026-04-11** ToDo-append intake: OPS remove Mitch Donohue from tasks/events.
  - Reconciled from board worker `1f958cb7` completion review after OPS worker `2b451363` was closed.
  - Matching OPS Done entries confirm Mitch/Mitchell Donohue references were cleaned from active event/task/calendar paths and event `504` now lists Christina Pinciotti and Jack Dempsey only.

- **2026-04-11** ToDo-append intake: update Portal email domains.
  - Reconciled from board worker `1f958cb7` completion review after Portal worker `bb73d00c` was closed.
  - Portal TODO is currently open `0`; no matching Portal Done entry was found, so this note records the AI coordination item as no longer active rather than adding a new Portal implementation claim.

- **2026-04-11** OPS outreach events / Connecteam replacement planning.
  - Reconciled from board worker `1f958cb7` completion review after OPS planning worker `3fd37724` was closed.
  - Planning/audit slice is no longer an active AI coordination item; broader Outreach/Connecteam implementation remains tracked separately in OPS and AI backlog.

- **2026-04-11** ToDo-append intake: OPS dashboard JavaScript/postpone + Outreach assignment visibility.
  - Reconciled from board worker `1f958cb7` completion review after OPS worker `5845bb85`.
  - Matching OPS Done entry confirms the dashboard arrow/postpone blinking fix and Outreach assignment visibility (`Assigned: ...` / `Unassigned`) landed and was live-pulled.

- **2026-04-11** BID/importer data-workflow planning:
  - Reviewed BID TODO/docs around ETL, downloads, intelligence, cadence, and importer handoff.
  - Highest-value first step: stabilize a deterministic BID finance/source registry from `data-management/templates/source-inventory.csv` before AI/importer implementation.
  - Next planning path: capture the six finance human answers, confirm `.205`/SSH sync handoff, then use the registry to specify `import_health.php` reminders and any later helper script.
  - Routing decision: keep the workflow in `ws bid`; use `ai-bridge` only for Codex/Claude handoff mechanics; do not route to `ws importer` yet because importer currently covers Portal contact/account imports.
  - OPS/Codex task refs included: `366460` for BID finance/report workflow follow-up and `366486` for BID improvement follow-up from Papers note `https://papers.koval.lan/3a05a0dd-a85b-42e1-9e42-1246fdcf7462`.

- **2026-04-11** OpenWrt IKEv2 / StrongSwan evaluation.
  - Evaluated and configured StrongSwan/IPsec/IKEv2 on OpenWrt as a non-WireGuard VPN path with native client support.
  - Router reachable at `192.168.55.1`, OpenWrt `24.10.5`.
  - Installed StrongSwan/swanctl/pki/EAP-MSCHAPv2 package set after approval.
  - Configured connection `koval-ikev2`, pool `10.57.57.10-10.57.57.60`, remote ID `vpn.koval-distillery.local`, EAP user `robert`, and explicit WAN firewall accepts for UDP `500`, UDP `4500`, and ESP.
  - Working verification: `ipsec0` gets `10.57.57.10`, DNS is `1.1.1.1` / `8.8.8.8`, and public IP is `205.178.117.216`.
  - Opened the native macOS VPN menu extra at `/System/Library/CoreServices/Menu Extras/VPN.menu` so it can be used from the menu bar/control center path.
  - Added Sonat access after explicit approval: EAP user `sonat`, password stored in `.private/ikev2/sonat-eap-secret.txt`, and profile stored in `.private/ikev2/KOVAL-IKEv2-Sonat.mobileconfig`.
  - Added separate Robert MacBook access: EAP user `robert-macbook`, password stored in `.private/ikev2/robert-macbook-eap-secret.txt`, and profile stored in `.private/ikev2/KOVAL-IKEv2-Robert-MacBook.mobileconfig`.
  - Added additional per-person access for Sebastian, Dmytro, and Mark: EAP users `sebastian`, `dmytro`, and `mark`, with password/profile files stored under `.private/ikev2/`.
  - Fixed LAN internet regression risk after bar iPad reports: removed the temporary WAN `masq_src='10.57.57.0/24'` restriction so normal LAN-to-WAN masquerading applies again; `fw4 check` passed and firewall reloaded.
  - Per user direction, Sonat router management used the working IKEv2 path through `admin-macmini`, not the old WireGuard config.
  - Client setup details: `.private/ikev2/CLIENT-SETUP.md`.
  - Project hub: `project_hub/issues/2026-04-11-openwrt-ikev2-strongswan-evaluation.md`.

- **2026-04-11** ToDo-append intake: Barrel-sales internal audience/list project.
  - Built from internal Salesreport barrel program data only; no importer path used.
  - Filtered accounts with sold barrels in the prior 10 years while excluding the last 12 months and managed-account prefixes Ema, ABA, Beatrix, Cultivate, Hotel Zachery/Zachary.
  - Created Forge audience `#40`, Forge planner/list item `#82`, PHPList list `#140`, and final Forge snapshot `#42`.
  - Synced `49` primary contact rows / `49` distinct PHPList members; documented `35` accounts with no eligible synced contact, `31` accounts with no CRM contacts, and `262` contacts blocked by PHPList suppression before snapshot sync.
  - Tightened the contact rule to use Portal `contact2account` plus legacy direct-account links, then choose one unsuppressed primary contact per account; alternates remain in review details only.
  - Excluded internal/test/sample account prefixes from the outreach audience: KOVAL, KOVALTEST, Sample/Samples.
  - Wrote the audit table and workflow notes to `/Users/werkstatt/salesreport/doc/barrel-sales-audience-2026-04-11.md`.
  - Sent the Avignon review email to Sonat from the Mac mini single-writer path; original plain-text Markdown-table message id `<177593347071.78670.13080383981128895677@kovaldistillery.com>`.
  - Corrected the email by resending with a real HTML table; message id `<177593420564.79113.15399117273173041174@kovaldistillery.com>`.
  - Resent the updated deduped `49` contact review list to Sonat as an HTML table with subject `Barrel buyer re-engagement list for review (updated 49-contact list)`; task id `barrel-sales-audience-sonat-review-2026-04-11-updated-list`.
  - Created PHPList draft campaign `#549` for the barrel buyer re-engagement list `#140`; draft only, no send timestamps, no recipient send rows, and no attachments added.
  - Added `/Users/werkstatt/salesreport/quick_contact.php` for fast Salesreport-side contact create/update/linking, with duplicate checks and audit notes.
  - Added `/Users/werkstatt/salesreport/barrel_contact_review.php` for row-by-row barrel list contact cleanup tied to Forge audience `#40`, PHPList list `#140`, and draft `#549`.
  - Follow-up: after contact cleanup, rerun `php scripts/build_barrel_sales_forge_audience.php` so PHPList list `#140` has the maximum valid contacts before draft `#549` is approved or sent.
  - Tastingroom archive boundary: local imapsync logs confirm `UserArchive/Chelsea_Lovett` folders exist, but the available local logs are folder listings rather than message exports; mailbox message search still needs an approved/searchable mailbox access path or export.
  - Project hub log: `project_hub/issues/2026-04-11-barrel-sales-audience-list.md`.
  - Board worker: `a7a6d9f5` (`2026-04-11 Barrel-sales audience/list project`).

- **2026-04-11** Portal/Frank receipts routing investigation:
  - Worker `d9c28811` verified Portal-side routing and the current Frank receipt script.
  - Portal module IDs are Receipts = `4` and Reimbursements = `11`; current Frank receipt script uses `PUT /receipts` and attaches with `module_id = 4`.
  - No Portal code change or deploy needed; remaining boundary is whether the active Frank/Mac mini runtime is stale.
  - Closed Portal worker session after review.

- **2026-04-11** ToDo-append intake: AI worker organigram and Codex/Claude guide completed in `ws ai-bridge`.
  - Created `/Users/werkstatt/ai-bridge/WORKER-ORGANIGRAM.md`.
  - Covered Task Manager, Summary Worker/Summarizer, `Decision Driver` as a distinct Task Manager child role, workspace workers, Frank Cannoli, Avignon Rose, Claude on KOVAL server `.205`, email/OPS as bridge transport, and needed coordinator/analyst/project/strategy/communications/systems roles.
  - Recorded that BID finance task `#1185` remains blocked until the six human answers are provided before deterministic finance registry implementation.
  - Board worker: `5cf35836` (`2026-04-11 Codex/Claude worker organigram`).

- **2026-04-10** AI workflow visibility rule correction recorded:
  - AI worker session `7a2b187a` recorded the manager-only / visibility workflow correction in `AGENTS.md` and `HANDOFF.md`.
  - Confirmed AI workspace root is Google Drive-synced and not a git repository, so no git commit is possible here.
  - OPS worker session `16683383` remains the separate live OPS implementation surface for Codex Kanban task `366212`.
  - AI worker session `7a2b187a` can be closed.

- **2026-04-10** MacBook Workspaceboard sync status cleanup:
  - verified `tmp/workspaceboard-0.61-v104-macbook-sync.tgz` matches `/Users/werkstatt/workspaceboard` except for intentionally omitted `server/node_modules`
  - recorded package SHA-256 `78e01ad4d61b99f92f2217f07c117aafb8230cdf105dd1ff9575f0074c8d884e` in `HANDOFF.md` after the MacBook visible v0.61 / HTML access follow-up
  - removed obsolete package `tmp/workspaceboard-0.60-v103-macbook-sync.tgz`
  - 2026-04-10 19:21:06 CDT (Machine: Macmini.lan): applied the package on MacBookPro.lan, reinstalled/restarted the runtime as `com.koval.workspaceboard`, and verified `http://127.0.0.1:17878/api/status` reports `board_version=0.61`
  - 2026-04-10 19:27:13 CDT (Machine: Macmini.lan): rebuilt/reapplied the package with Workspaceboard HTML page access fixes; MacBook `127.0.0.1:17878` serves `start.html`, `task-management.html`, `workspaceboard.html`, `todos.html`, `history.html`, and `analytics.html` with HTTP `200`; MacBook Apache config is fixed on disk but still needs an admin/root reload because non-interactive `sudo apachectl graceful` returns `sudo: a password is required`
  - 2026-04-10 19:31:27 CDT (Machine: Macmini.lan): rebuilt/reapplied package with visible `index.html` text updated from `v0.49` to `v0.61`; MacBook `http://127.0.0.1:17878/` now returns HTTP `200` with `Codex Workspace Board v0.61`; Apache `/workspaceboard/start.html` remains blocked at HTTP `403` until the system Homebrew Apache LaunchDaemon is reloaded locally/admin-side; SSH reload attempts failed with `sudo: a password is required` and macOS administrator prompt failed with `execution error ... (-60007)`
  - 2026-04-11 12:43:58 CDT (Machine: RobertMBP-2.local): verified the same state locally on the MacBook; direct runtime URLs on `127.0.0.1:17878` return HTTP `200`, while Apache `/workspaceboard/start.html` still returns HTTP `403`. Added the missing `/Users/werkstatt/workspaceboard` and `/Users/werkstatt/workspaceboard/api` Apache directory allow/PHP handler blocks to `/usr/local/etc/httpd/httpd.conf`; backup is `/usr/local/etc/httpd/httpd.conf.bak.workspaceboard-20260411-124301`; `apachectl -t` returns `Syntax OK`; live Apache still needs local admin reload because non-interactive reload, `launchctl kickstart`, and root PID `HUP` are blocked by password/permission requirements.
  - 2026-04-11 12:47:23 CDT (Machine: RobertMBP-2.local): local admin reload completed; Apache log shows graceful restart at `12:46:46`; `http://localhost/workspaceboard/start.html` now returns HTTP `302` to `/login/index.php?referrer=workspaceboard%2Fstart.html` instead of HTTP `403`, confirming the desired localhost route is working behind the auth gate.
  - 2026-04-11 12:49:13 CDT (Machine: RobertMBP-2.local): fixed `http://localhost/workspaceboard/task-management.html` staying at `Board Loading...` by adding missing PHP API wrapper entrypoints for the Apache alias bridge: `api/status.php`, `api/serve-mode.php`, `api/management/overview.php`, `api/task-manager/history.php`, `api/task-manager/ensure.php`, and `api/task-manager/message.php`; lint passes and localhost API requests now return JSON instead of Apache `404`.
  - 2026-04-11 12:54:46 CDT (Machine: RobertMBP-2.local): read-only SSH inspection of Macmini.lan confirmed the intended live monitor setup there: Task Manager `5909d11e` and Summary Worker `d168f87c`; Frank email automation was not started or changed. Fixed MacBook Workspaceboard state so AI Workspace shows `monitor needed` instead of `finished` when monitors are absent, `monitor partial` if only one monitor is live, and `monitoring` when both are live; `/api/task-manager/ensure` now starts both the Task Manager and Summary Worker. Reinstalled the board runtime and started local monitors `0f99c595` Task Manager and `df09cc20` Summary Worker; API now reports AI Workspace `monitoring`.

- **2026-04-10** California SGWS/Southern Wine XLS/PDF import and five-list creation completed:
  - Source files live under `/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/tmp/california-lists`.
  - Imported/linked `179` unique payload emails under CRM account `2095` (`Southern Wine and Spirits of California`) using importer history rows `#46`-`#50`.
  - `SGWS CA - SIG NCA 2025-11-03`: Forge audience `#35`, planner `#77`, phpList list `#135`; `67` total / `67` eligible / `67` phpList members.
  - `SGWS CA - SIG KAM CA 2025-11-03`: Forge audience `#36`, planner `#78`, phpList list `#136`; `22` total / `22` eligible / `22` phpList members.
  - `SGWS CA - SIG D&E Imports CA 2025-11-03`: Forge audience `#37`, planner `#79`, phpList list `#137`; `22` total / `22` eligible / `22` phpList members.
  - `SGWS CA - SIG SCA 2025-11-03`: Forge audience `#38`, planner `#80`, phpList list `#138`; `83` total / `81` eligible / `81` phpList members; `2` blocked by phpList blacklist.
  - `SGWS CA Chain Org Chart 2023-10-03`: Forge audience `#31`, planner `#72`, phpList list `#131`; `48` total / `48` eligible / `48` phpList members.

- **2026-04-10** Portal user deactivation from ToDo-append intake:
  - Set Brent Adams (`badams32@gmail.com`, Portal user ID `1229`) and Bryan Mattox (`bryanmattox@ameritech.net`, Portal user ID `1311`) to `Inactive` with `deleted = 1`.
  - Matched Portal disable behavior by deactivating their active salary rows.
  - Removed their phpList memberships from list `71` / `KOVAL - INTERNAL`; post-check found `ACTIVE_INTERNAL_COUNT = 0`.

- **2026-04-08** AI workspace board build:
  - finished the board/session-state pass for `working`, `waiting`, and `finished`
  - fixed the session-status mismatch where finished sessions could still surface as `waiting`
  - verified finished sessions stay open for review and can then be closed cleanly
  - verified the `workspaceboard` repo path, LaunchAgent reinstall flow, and Mac mini sync path
  - dashboard runtime limitation remains: Node `v25.2.1` still breaks `node-pty-prebuilt-multiarch` on the MacBook, so local board runtime stays on Node `v24.14.0` until PTY dependency work is done

- **2026-04-08** Auth/session stabilization across `login`, `ops`, and `lists`:
  - added low-risk `/lists/admin` auth diagnostics for future repros
  - hardened shared SSO handoff helpers and OPS task auth fallback behavior
  - restricted legacy additional-user fallback to explicit exceptions so vtiger users no longer silently degrade out of full SSO
  - confirmed local vtiger-user login and cross-module behavior, pushed changes, and pulled live for `ops` and `login`

- **2026-04-08** AI reminder review prep finished:
  - reviewed the original March AI recommendation pass and the dated `2026-04-15` reminder scope
  - confirmed current decisions:
    - Codex primary workflow is CLI via Workspace Board
    - Gemini CLI was tested and is not currently useful enough to be primary
    - Codex skills are in use, including `playwright`
    - `openai-docs` support is now enabled locally via the `openaiDeveloperDocs` MCP entry
    - AI email-account operations can run in the Frank workspace with Frank-specific guardrails/logging
    - current mailbox candidates are `frank.cannoli@kovaldistillery.com` and `claude@koval-distillery.com`
  - moved evergreen AI/project-management review guidance into `ai-project-management-guide.md`
  - closed the dated AI reminder project-hub item after converting it into standing guidance

- **2026-04-08** Frank scheduled automation + Mac mini handoff:
  - verified the Mac mini is the active single automation host for `com.koval.frank-auto`
  - confirmed this MacBook is not also running the LaunchAgent
  - recorded the single-writer verification in `frank/HANDOFF.md`
  - closed the Frank automation project-hub log after verification

- **2026-04-08** Braincloud workspace path fix:
  - updated shared workspace references to prefer `/Applications/MAMP/htdocs/braincloud`
  - kept `ai_workspace/htdocs/braincloud` as the fallback/synced copy path
  - fixed `ws braincloud` and Codex dashboard mappings so Braincloud resolves like the other localhost web modules

- **2026-04-08** Salesreport report automation + hitlist optimization:
  - project log: `project_hub/issues/2026-03-15-salesreport-report-automation-and-hitlist-optimization.md`
  - verified authenticated UI/layout for `saved_reports.php`
  - verified live Illinois visit-planner execution; current implementation returns 40 accounts across 4 x 10-account segments
  - verified `hitlist_optimization.php` in browser with active batch review actions
  - tuned hitlist optimization by excluding chain/big-box noise, normalizing city/state display values, and constraining rep metric picks by live territory fit / Benjamin visited-state fallback
  - added manual review access via menu links plus an in-page `Open Latest Run` action
  - latest verified batch after tuning: run `5` for `2026-04-01`
  - remaining future work, if resumed later: additional saved-report/query wiring, visit-planner output refinements, and batch history / prospect-queue polish

- **2026-04-08** Braincloud workspace bootstrap:
  - created local `braincloud/` workspace under `ai_workspace`
  - initialized local git on `main` and pointed `origin` at `https://github.com/robs1412/braincloud.git`
  - defined starter node categories, source types, link types, and intake templates
  - added `braincloud` to local workspace docs and the Codex dashboard map

- **2026-04-07** Frank automation groundwork:
  - added portable path resolution for Frank mailbox scripts across MacBook/Mac mini path variants
  - added scheduled `draft-only` inbox runner plus LaunchAgent install/uninstall scripts
  - added single-writer cross-machine notes so Frank automation can be hosted on the Mac mini safely
- **2026-04-07** Codex Workspace Board workspace coverage:
  - added first-class workspace cards/launch targets for `frank`, `contactreport`, `eventmanagement`, and `donations`
- **2026-04-07** Codex Workspace Board session-state recovery:
  - fixed launchd runtime detection of live tmux sessions by exporting a consistent `TMPDIR` before the Node server starts
  - moved dashboard session metadata onto a shared machine-local state path so launchd and direct starts see the same sessions
  - changed exited sessions in the board UI to open tmux history by default instead of immediately showing `[detached]`
  - added recovery for existing `codex-board-*` tmux sessions when metadata is missing so live sessions reappear after runtime restarts
- **2026-04-07** Codex Workspace Board workspace resolution fix:
  - updated the dashboard workspace map to use portable path resolution instead of MAMP-only paths
  - fixed board launches for repos that exist under local GitHub clones on this machine, including `salesreport` and `bid`
- **2026-04-07** Codex Workspace Board cleanup:
  - disabled the blinking blue terminal cursor in board-managed Codex sessions
  - consolidated the dashboard source to a single canonical `codex_dashboard/` folder
  - updated launcher/runtime scripts to stop scanning both `codex_dashboard/` and `codex_dashboard 2/`
- **2026-04-07** Codex Workspace Board regression fix:
  - removed duplicate stage-level `History` / `Live` controls and kept terminal actions on the session shell only
  - cache-busted board assets after a frontend runtime regression (`terminal is not defined`) so the browser reloads the current script
- **2026-04-07** Removed the local `finance` workspace and moved its contents into `bid/intelligence/analysis/finance-workspace`.
- **2026-04-07** Codex Workspace Board:
  - built a local browser dashboard in `codex_dashboard/` for active Codex session visibility
  - grouped sessions by workspace using live PID, TTY, elapsed-time, and cwd detection
  - upgraded it to browser-managed embedded terminals with `zsh` and `codex` launch modes
  - added grid, focus, and stack views plus hide/show session controls
  - added local daemon-style start/stop scripts at `scripts/start_codex_dashboard.sh` and `scripts/stop_codex_dashboard.sh`
  - added a macOS LaunchAgent install/uninstall path so the board auto-starts on login and stays available at `http://127.0.0.1:17878`
  - aligned the LaunchAgent/runtime server default back to `17878` so auto-start and direct links target the same port
  - kept Screenbox linked as a companion tool rather than forcing it into the terminal implementation

- **2026-03-15** Illinois strategy HTML report:
  - generated a user-openable Illinois strategy report in `salesreport`
  - included the 250-account core list, RTD seed list, and whale recovery list
  - applied requested exclusions for `Koerner`, `G&M`, and the prior big-box chain set

- **2026-03-15** WireGuard stability monitoring across networks:
  - confirmed failures were not caused by Sophos/HMA remnants or a single Wi-Fi network
  - created dated incident log and route/DNS/external-IP monitoring notes
  - isolated Linksys/OpenWrt config issues on temporary `wgmac` path and corrected missing WAN port rule during testing
  - replaced old stale `wg0` client/peer identity with fresh production tunnel `koval-robert-wg0-fresh`
  - left recovery watchdog targeting the fresh `wg0` tunnel and kept detailed project note for rollback/history

- **2026-03-06** Recommendation pass completed in [recommendations.md](/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My%20Drive/2026_workspace_sync/ai_workspace/recommendations.md):
  - answered `Ask AI: what else can we do`
  - answered `Ask AI: what are we missing`
  - answered `Ask AI: how can we push sales`
  - documented `Run Codex in CLI instead of VS Code: benefits`
  - documented `Gemini CLI installed: define usage plan`
  - documented `Can Codex manage an email account`
  - documented `Can we install Codex agents`
  - documented `How else can Codex via VS Code help`
- **2026-03-06** Git auth / live SSH setup documented and verified in project-hub records:
  - resolved `Tomorrow: investigate why git auth worked on the other machine but failed locally`
  - resolved `Tomorrow: set up SSH access for ftp.koval-distillery.com`
- **2026-03-06** Deployment strategy for live domains documented as completed rollout scope; no additional module git rollout planned right now.
- **2026-03-06** Added missing `ws` workspace mappings and aliases on admin machine (`~/.bashrc`) for `importer`, `eventmanagement`, `contactreport`, `donations`, and `lists`; verified path resolution via `ws <name>; pwd`.
- **2026-03-05** OPS Task `362555`: replaced automated polling with manual `check ToDo` trigger workflow.
- Add workspace launcher mappings for `importer`, `eventmanagement`, `contactreport`, and `donations` in `~/.bashrc` and sync those mappings/aliases in `ai_workspace/AGENTS.md`.
- **2026-02-26 Lists Image Browser White Page** (KCFinder path fix)
- **2026-03-02** How to keep tasks organized: own repo vs DB (resolved with `TODO.md` + `ToDo-append.md` workflow).
- Standardize TODO workflow across modules (`TODO.md` + `ToDo-append.md`/`TODO-append.md` + `AGENTS.md` TODO workflow section + matching `.htaccess` protections where applicable).
- Add `ToDo-append.md` in `ai_workspace` when missing (append-only queue file).
- Add `ws lists` workspace launcher support in `~/.bashrc` and sync `AGENTS.md` mapping/aliases.
- Add phpList send-page stale-tab overwrite guard so outdated editor tabs cannot overwrite newer campaign content.
- Harden module `.htaccess` rules so `ToDo-append.md`/`TODO-append.md` are not publicly web-accessible (validated locally for `/ops` and checked across related modules).
- Fix localhost PHPList admin crash (`/lists/admin`) caused by macOS/Homebrew Apache gettext locale segfault; set locale env defaults early in `lists/config/config.php`.
- Add/standardize `ToDo-append.md` queue workflow across modules and document append-to-TODO process in `AGENTS.md`.
- Update workspace/module AGENTS git flow to require local commit + localhost testing before push, and live pull only when needed.
- Merge `PROJECT_TODOS.md` into `TODO.md` backlog.
- Analyze `project_list-import.txt` and split into structured execution TODOs (`PROJECT_TODOS.md`).
- Set up key-based SSH from MacBook Pro to admin machine (`admin-macmini` -> `192.168.55.16`) and document in `AGENTS.md`.
- Document canonical live SSH host/user (`koval@ftp.koval-distillery.com`) and no-overwrite SSH config merge policy in workspace/module `AGENTS.md`.
- Add `HANDOFF.md` and `handoff.sh` to standardize cross-machine Codex handoffs.
- Add Codex terminal install instructions to `AGENTS.md` (`npm install -g @openai/codex`, `codex --version`, `codex login`).
- Remind me about open TODO items (now part of startup workflow from `AGENTS.md`).
- Users sharing a computer cannot log out of `portal.koval-distillery.com` (resolved in `project_hub/issues/2026-02-26-logout-reliability.md`).
- Proper `AGENTS.md` manual (standardized across `ai`, `ops`, `salesreport`, `forge`, `login`, `portal`, `bid`).
- Set up portable `ws` launcher + aliases across machine path variants.
- Merge `TODO2.md` into `TODO.md` and keep `TODO2.md` as fallback pointer.
- Remove OPS recording scripts/artifacts from `ai_workspace`; keep only process standards in TODO/AGENTS.
- Build a repeatable workflow from this TODO (implemented in `AGENTS.md` startup requirements + TODO-first flow).
- Turn TODO items into a project plan (implemented as startup planning + scoped execution flow).
- Create/use agents (skills) to execute plan items (implemented: skill check required each cycle; propose/create when missing).
- Deployment strategy for live domains: current rollout scope completed for `ops`, `login`, `forge`, `salesreport`, `lists`, `importer`, and `contactreport`; no additional module git rollout planned right now.
