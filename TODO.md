# TODO — ai_workspace

Updated: 2026-04-16 17:32 CDT (Machine: Macmini.lan)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- Decision needed: choose Google Drive OAuth/token storage policy before any future Drive-backed Digital Office projection automation.
  - Policy review completed 2026-04-16: recommendation is a machine-local OS keychain/private path by default, or an approved secret manager/keychain/service-account path for shared automation.
  - Rejected storage targets: Google Drive-synced files, Google Drive-synced runtime folders, Papers records, normal manifests, and git.
  - Exact human decision if Drive-backed automation is requested: approve Option A as the default storage path for this project, or name the approved Option B secret manager/keychain/service-account path.
  - Decision note: `project_hub/digital-office/storage-decision-needed.md`.

## Backlog

### OPS / Outreach / Trainual
- Build the in-house outreach events module in `ws ops`.
  - Goal: Events + Market Events parity, one-or-more linked shifts, existing shift-notification behavior, Connecteam replacement, account/login/activity linkage, and no second user system.
  - Route before implementation: `ws ops` worker with Code and Git Manager preflight; Security Guard only if auth/access or production data mutation enters scope.
- Review event strategy notes and COT/Connecteam replacement plan.
  - Sources: `https://docs.google.com/document/d/1EaHH97GJ_9ztMNtWaEp-abGUHdVqVcyvJWkUjko5euc/edit?tab=t.0`.
  - Route: coordination in `ws ai`; implementation in `ws ops`.
- Define OPS market improvements.
  - Scope: account/contact creation from OPS and OPS -> salesreport data-flow boundaries.

### Lists / Forge / Communications
- Clean PHPList legacy send-history soft deletes.
  - Route: `ws lists`; coordinate with Forge only if newsletter/list workflow crosses modules.
- Review PHPList, Shopify, and Square signup recurring checks.
  - Route: `ws lists` / `ws forge` after a concrete checklist is approved.

### BID / Importer / Salesreport / Analytics
- Build web analytics funnel reporting for `koval-distillery.com`.
  - Scope: Dmytro analytics source review and GA-style funnel view.
  - Route: likely `ws sales` or a dedicated analytics worker after source ownership is clarified.
- Audit Google Ads issues.
  - Route: read-only account/campaign audit first; no account changes without explicit approval.
- Track Salesreport user adoption/access.
  - Scope: usage by login and required state/access controls for named sales users.
- Review recurring sales/data operations.
  - Scope: importer roster update cadence, distributor inventory checks, monthly/quarterly warehouse + distribution salesreport checks, and BID data refresh cadence.
- Clean distributor accounts.
  - Route after scope split: `ws sales` for reporting/account analysis, `ws portal` or `ws ops` only if the cleanup mutates CRM records.

### Portal / Login / Activity Reporting
- Fix OPS <-> Portal SSO/login persistence, including next-day logout behavior.
  - Existing related project-hub records remain open; route through `ws login` and `ws ops` with Code and Git Manager plus Security Guard preflight.
- Define Portal production audit enhancements.
  - Scope: extended modification trails, prior-month edit report, shipped-vs-bottled mismatch report, and `<2000 lb` grain/product mismatch logic.
  - Route: `ws portal` for Portal-owned reports, with Salesreport ownership checked for shipped-vs-bottled work.

### IT / Security / Workstations
- Review IT planning docs and decide transfer/deprecation plan for GitLab.
  - Sources: `https://papers.koval/teams/it/task-queue.html`, `https://papers.koval/teams/it/roadmap.html`, `https://papers.koval.lan/teams/it/dashboard.html`, and `https://papers.koval.lan/teams/it/research.html`.
  - Approval gate: no live Papers writes or `.205` work without explicit approval.
- Check MacBook power-management logs and wake causes.
  - Route: `ws ai` coordination; no daemon or system-setting change without explicit approval.
- Monitor Google Postmaster.
  - Source: `https://postmaster.google.com/u/0/dashboards#do=kovaldistillery.com&st=userReportedSpamRate&dr=7`.
  - Route: read-only review first; no admin/account changes without approval.
- Plan Google Cloud security hardening.
  - Scope: key inventory, dormant-key cleanup, API restrictions, least privilege, key rotation/expiry policy, Essential Contacts, and billing anomaly/budget alerts.
  - Route: Security Guard-led planning; no credential, IAM, billing, or production changes without explicit approval.

## Done

- **2026-04-16** Recurring operations reporting planning slice completed.
  - Added `project_hub/issues/2026-04-16-recurring-operations-reporting-plan.md` with owner modules, read-only source surfaces, cadence, approval gates, first no-write slice, and notification/email boundaries for monthly task stats, events/task stats review, and barrel sample page manual/follow-up. Scope stayed docs-only: no code, production data, email, notifications, credentials, scheduled jobs, commit, push, deploy, runtime change, OPS intake, or live-source access.

- **2026-04-16** AI-assisted Salesreport data-import planning slice completed.
  - Added `project_hub/issues/2026-04-16-ai-assisted-salesreport-data-import-plan.md` with deterministic preflight, safe AI assist points, approval gates, first no-write prototype, owner workspace, and future routing. Scope stayed docs-only: no code, credentials, production data, email, commit, import, deploy, or runtime change.

- **2026-04-16** BID ETL/import workflow planning moved to Done.
  - Closed the planning item based on BID commit `54c8e544d967e7b5f645f8e872827fdcfebe207d` and `data-management/etl-import-workflow-plan.md`. Docs closeout only in AI Workspace; no BID code, commit, push, deploy, import run, data mutation, credential access, or external-system change was performed.

- **2026-04-16** Unified user activity reporting planning slice completed.
  - Added `project_hub/issues/2026-04-16-unified-user-activity-reporting-plan.md` with source systems, read-only data surfaces, privacy/security gates, cadence, first slice, and workspace ownership. Scope stayed docs-only: no code, credentials, production data, email, deploy, or runtime change.

- **2026-04-16** OPS Market Events Trainual planning slice prepared.
  - Added local planning docs under `trainual/ops-market-events/` for module outline, walkthrough script, recording checklist, safe demo-data notes, recordings output convention, and acceptance checklist. Ignored `recordings/` artifacts are excluded. Planning only; no recording, publishing, code, live data, email, secrets, deploy, or external-system mutation.

- **2026-04-16** Digital Office OAuth/token storage policy review completed.
  - Updated the local storage decision note after a docs-only review. Recommendation is a machine-local OS keychain/private path by default, or an approved secret manager/keychain/service-account path for shared automation; not Google Drive-synced files, Papers, manifests, or git. No credentials, OAuth, Drive, Papers, runtime, or email surfaces were accessed.

- **2026-04-16** Operational autonomy directive recorded.
  - Updated AI Workspace role/policy docs so Decision Driver may approve obvious verified Code/Git continuation within approved scope, Task Manager keeps routing until 15 real manual blockers, and Task Manager/Decision Driver/Code and Git Manager/Security Guard resolve safe routing, review, and cleanup without Robert where guardrails allow. Docs/notes only; no code, commit, push, restart, email, secret access, external-system mutation, deploy, or live-data action.

- **2026-04-16** Digital Office local no-write Papers projection pack prepared.
  - Added `project_hub/digital-office/` with a pack README, projection schema, sample export, Papers work-record template, Security Guard checklist, and OAuth/token storage decision note.
  - Scope stayed local and no-write: no Papers writes, `.205`/`.17` writes, OPS/Portal DB changes, credentials, MCP exposure changes, notifications/email, Frank/Avignon runtime changes, service restarts, deploys, or live runtime mutation.

- **2026-04-16** Workspace/account boundary and macOS permission-prompt policy recorded.
  - Updated AI Workspace and Security Guard docs to require explicit Robert approval before freely operating outside `/Users/werkstatt`, require explanation before macOS permission grants such as "Control other apps", and identify runtime enforcement surfaces for a later approved implementation slice. No runtime, LaunchAgent, SSH config, system permission, secret, deploy, or worker-injection change was performed.

- **2026-04-16** AI Workspace TODO hygiene pass completed.
  - Regrouped the open AI Workspace backlog by route and approval boundary, confirmed the append queue is empty, and closed stale project-hub entries for the killed Salesreport MemPalace pilot and completed Werkstatt path-unification migration. No OPS intake, code implementation, external-system mutation, emails, credential access, daemon work, commit, push, deploy, or production change was performed.

- **2026-04-16** KOVAL 2026 Management Planner guidance recorded for task-management docs.
  - Added concise docs-only guidance in AI Workspace role-map, Task Manager, Project Manager, project-management guide, and handoff notes. Source-file search did not find a local planner file outside private/secret paths; no email, external-system, credential, runtime, code, commit, push, deploy, or service change was performed.

- **2026-04-16** Completed-code-worker routing policy clarified.
  - Added docs-only direction that completed code-producing workers in git-backed workspaces route to Code and Git Manager for closeout, while Task Manager/Decision Driver surface only real human decisions. No runtime code, email, secret, monitor, commit, push, deploy, or service change.

- **2026-04-16** Frank/Avignon completion and summary policy aligned.
  - Updated AI Workspace, Frank, and Avignon docs so completed tasks get one concise completion confirmation, both workers default to morning summaries only, and evening roundups are disabled by default unless Robert re-approves them. Verified Frank morning overview LaunchAgent exists; Avignon morning summary still needs explicit runtime install approval.

- **2026-04-16** Avignon morning summary runtime installed.
  - Added and loaded `com.koval.avignon-morning-overview` for 06:00 local time with Sonat-only Avignon profile routing and duplicate protection. Verification used compile/lint/help/launchctl only; no test email was sent and the standing Avignon inbox monitor cadence was unchanged.

- Older Done history through 2026-04-15 was moved to `TODO-done-archive-2026-04-16.md` during the 2026-04-16 TODO hygiene pass so this file stays focused on active queue management.
