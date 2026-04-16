# TODO — ai_workspace

Updated: 2026-04-16 17:05:00 CDT (Machine: Macmini.lan)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- Decision needed: choose Google Drive OAuth/token storage policy before any future Drive-backed Digital Office projection automation.
  - Recommendation: keep OAuth credentials and token caches machine-local or in an approved secret manager/keychain path; do not store them in Google Drive-synced planning files or git.
  - Decision note: `project_hub/digital-office/storage-decision-needed.md`.

## Backlog

### OPS / Outreach / Trainual
- Build the in-house outreach events module in `ws ops`.
  - Goal: Events + Market Events parity, one-or-more linked shifts, existing shift-notification behavior, Connecteam replacement, account/login/activity linkage, and no second user system.
  - Route before implementation: `ws ops` worker with Code and Git Manager preflight; Security Guard only if auth/access or production data mutation enters scope.
- Produce the first Trainual planning slice for OPS Market Events.
  - Scope: module outline, user-facing walkthrough script, recording checklist, safe demo-data notes, output-location convention under `ai_workspace/recordings/`, and acceptance checklist.
  - Out of scope until Robert approves separately: recording, external publishing, code changes, live data mutation, and broad cross-module rollout.
  - After acceptance, decide whether a reusable Trainual skill is warranted.
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
- Plan BID ETL and import workflow.
  - Scope: extract/transform/load flow, schedule, validation, and BID data refresh cadence.
  - Route: `ws bid`; use `ws importer` only if the work becomes Portal/account import implementation.
- Evaluate AI-assisted data-import workflow.
  - Context: Julia currently imports salesreports manually from XLS and other data sources.
  - Goal: determine whether AI-assisted import can improve speed and data accuracy.
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
- Design unified user activity reporting.
  - Scope: Portal activity, task stats, shift/check-in stats, OPS/salesreport/contactreport/BID/automation usage, and optional Gmail/Gemini admin usage overlays.
  - Route: `ws ai` planning first; implementation split by source system.
- Define recurring operations reporting.
  - Scope: monthly task stats send-out, events/task stats review cadence, and barrel sample page manual/follow-up.
  - Route: `ws ai` planning first; implementation split by owning module.

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
