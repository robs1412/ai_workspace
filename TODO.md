# TODO — ai_workspace

Updated: 2026-04-16 18:07 CDT (Machine: Macmini.lan)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- Blocker: event strategy Google Doc for COT/Connecteam replacement needs read-only access or a supplied text export before full external-source review.
  - Source: `https://docs.google.com/document/d/1EaHH97GJ_9ztMNtWaEp-abGUHdVqVcyvJWkUjko5euc/edit?tab=t.0`.
  - Local coordination review completed in AI Workspace commit `128c5f1` from existing AI Workspace notes; exact blocker is anonymous Google Docs export returned `HTTP/2 401`.
  - Decision note: `project_hub/issues/2026-04-16-event-strategy-cot-connecteam-review.md`.

- Decision needed: approve the next OPS outreach Connecteam replacement stage before any final sync, live schedule, notifications, auth/access work, or canonical rule changes.
  - Completed source: ops commit `18d32a04ddaf5257214d62340eda7e044a1ef3d8`, including docs and `scripts/connecteam_staging_parity.php`.
  - Allowed next slice without this decision: keep work to docs or read-only dry-run analysis in `ws ops`.
  - Approval gates: no `--apply`, final sync, live schedule, notification send, auth/access change, or canonical data-rule change without explicit approval.

- Decision needed: choose owner/product rules for OPS market improvements.
  - Completed source: ops commit `478593f3329c49aec9a30ce0464f2f507394a60e`, `docs/2026-04-16-ops-market-improvements-plan.md`.
  - Decisions needed before implementation: account/contact request ownership, duplicate rules, account category mapping, Salesreport consumption shape, and audit/retention expectations.

- Blocker: Shopify/Square signup recurring checks need source owner and approved read-only export/API path.
  - Completed source: lists commit `e2ce6afd8706372d2375b7dd50c4c4a0c63091e4`, `docs/signup-recurring-checks-review-2026-04-16.md`.
  - Approval gate: no Shopify/Square/API credential access, production read, automation, or mutation until the read-only path is approved.

- Decision needed: define exact next-day logout policy and obtain Security Guard approval before SSO/session changes.
  - Completed source: login commit `ad6a19760d626e3e709122d311e247187e3df72b`, `docs/2026-04-16-ops-portal-sso-persistence-preflight.md`.
  - Approval gate: no auth/session code change, production session mutation, deploy, or live login test requiring credentials before Security Guard approval.

- Decision needed: define Portal production audit report rules and Salesreport handoff.
  - Completed source: portal commit `2e076c6c8e47ce54140ddc95704f574adb9f8333`, `docs/production-audit-enhancements.md`.
  - Decisions needed before implementation: edit-trail definitions, prior-month edit handling, `<2000 lb` rule semantics, and which shipped-vs-bottled work belongs in Salesreport.

- Decision needed: assign recurring sales/data cleanup owners and mutation boundaries.
  - Completed source: salesreport commit `8004fd93f97ccc0f65db8f4755523facb1370271`, `doc/recurring-sales-data-ops-review-2026-04-16.md`.
  - Decisions/handoffs needed before implementation: importer roster owner, BID refresh cadence, CRM mutation approval, and cleanup owner for distributor/account changes.

- Decision needed: choose Google Drive OAuth/token storage policy before any future Drive-backed Digital Office projection automation.
  - Policy review completed 2026-04-16: recommendation is a machine-local OS keychain/private path by default, or an approved secret manager/keychain/service-account path for shared automation.
  - Rejected storage targets: Google Drive-synced files, Google Drive-synced runtime folders, Papers records, normal manifests, and git.
  - Exact human decision if Drive-backed automation is requested: approve Option A as the default storage path for this project, or name the approved Option B secret manager/keychain/service-account path.
  - Decision note: `project_hub/digital-office/storage-decision-needed.md`.

- Blocker: MacBook power-management wake-cause review needs the MacBook to be reachable or local user access to its logs.
  - Completed source: AI Workspace commit `02d5dc7`.
  - Target checked: `MacBookPro.lan` / `192.168.55.180`.
  - Read-only diagnostics attempted 2026-04-16: hostname resolution, ICMP ping, and batch-mode SSH only.
  - Result: `MacBookPro.lan` did not resolve, `192.168.55.180` had 100% ping loss, and SSH to `192.168.55.180:22` timed out. No `pmset` logs were available remotely.
  - Approval gates preserved: no credentials requested, no settings changed, no daemon/LaunchAgent/SSH config/system state touched.

- Blocker: PHPList legacy send-history inventory needs an approved sanitized export or approved read-only DB/export path before real counts.
  - Completed source: lists commit `075cd358b784e47c246ef4f5fbd02cfab66facdd`, `docs/phplist-legacy-send-history-read-only-inventory-plan-2026-04-16.md`.
  - Approval gate: no production DB read/export, credential access, mutation, deletion, restore, or cleanup until the inventory input path is approved and the resulting inventory is reviewed.

- Decision needed: approve Salesreport distributor cleanup production read/export and define mutation ownership/source of truth.
  - Completed source: salesreport commit `dd58319202d308f86c8e20f2cf31b12413b0ddae`, `doc/distributor-account-cleanup-report-workflow-2026-04-16.md`.
  - Decisions needed before implementation: approved production read/export path for the report workflow, and owner/source-of-truth definition for any distributor cleanup mutation.

## Backlog

### OPS / Outreach / Trainual
- Build the in-house outreach events module in `ws ops`.
  - Goal: Events + Market Events parity, one-or-more linked shifts, account/login/activity linkage, and no second user system.
  - Completed planning/dry-run source: ops commit `18d32a04ddaf5257214d62340eda7e044a1ef3d8`, docs plus `scripts/connecteam_staging_parity.php`.
  - Next scoped work: implementation design or read-only dry-run follow-up only until final sync/live schedule/notifications/auth/canonical-rule approvals are explicit.
  - Route before implementation: `ws ops` worker with Code and Git Manager preflight; Security Guard only if auth/access or production data mutation enters scope.
- Implement OPS market improvements after owner/product decisions.
  - Completed planning source: ops commit `478593f3329c49aec9a30ce0464f2f507394a60e`, `docs/2026-04-16-ops-market-improvements-plan.md`.
  - Next scoped work: convert approved account/contact request, duplicate, category, Salesreport handoff, and audit/retention rules into an implementation plan.
  - Route: `ws ops`, with `ws sales` involved for Salesreport consumption shape.

### Lists / Forge / Communications
- PHPList legacy send-history cleanup next slice.
  - Completed planning/review source: lists commit `a246095d14f07c4e82ebc23fe47e0836a7dded26`, `docs/phplist-legacy-send-history-soft-delete-review-2026-04-16.md`; inventory plan source: lists commit `075cd358b784e47c246ef4f5fbd02cfab66facdd`, `docs/phplist-legacy-send-history-read-only-inventory-plan-2026-04-16.md`; TODO closeout commit `eae015bef06eed50fbbcbacd6324033fa62fb427`.
  - Next scoped work: run the planned read-only inventory only after a sanitized export or approved read-only DB/export path is provided.
  - Approval gate: no production DB read/export, credential access, DB mutation, deletion, restore, or production cleanup until the input path is approved and inventory results are reviewed.
  - Route: `ws lists`; coordinate with Forge only if newsletter/list workflow crosses modules.
- Implement signup recurring checks after Shopify/Square source access is approved.
  - Completed review source: lists commit `e2ce6afd8706372d2375b7dd50c4c4a0c63091e4`, `docs/signup-recurring-checks-review-2026-04-16.md`.
  - Next scoped work: build a read-only recurring-check design from approved source exports/API surfaces.
  - Route: `ws lists` / `ws forge`; no source-system access or credential handling until approved.

### BID / Importer / Salesreport / Analytics
- Build web analytics funnel reporting for `koval-distillery.com`.
  - Completed planning/review source: salesreport commit `85971d9004d1d73c49751d52080a5ec7587f9780`, `doc/web-analytics-funnel-source-review-2026-04-16.md`.
  - Next scoped work: implement the approved GA-style funnel view only after analytics source ownership and build scope are confirmed.
  - Approval gate: no account changes, tracking changes, production data mutation, deploy, or external analytics-system write without explicit approval.
  - Route: likely `ws sales` or a dedicated analytics worker after source ownership is clarified.
- Audit Google Ads issues.
  - Route: read-only account/campaign audit first; no account changes without explicit approval.
- Implement approved Salesreport adoption/access follow-ups.
  - Completed planning source: salesreport commit `85971d9004d1d73c49751d52080a5ec7587f9780`, `doc/salesreport-adoption-access-planning-2026-04-16.md`.
  - Next scoped work: turn the planning result into specific usage-by-login and state/access-control changes after owner review.
  - Approval gate: no access-control mutation, user-state change, deploy, or production data change without explicit approval and Code and Git Manager preflight.
- Implement recurring sales/data operations after owner handoffs.
  - Completed review source: salesreport commit `8004fd93f97ccc0f65db8f4755523facb1370271`, `doc/recurring-sales-data-ops-review-2026-04-16.md`.
  - Next scoped work: turn approved importer roster ownership, distributor inventory cadence, warehouse/distribution checks, and BID refresh cadence into concrete tasks.
  - Route: `ws sales`, with `ws importer` and `ws bid` involved for their owned cadences.
- Clean distributor accounts after report input and mutation ownership are approved.
  - Completed workflow source: salesreport commit `dd58319202d308f86c8e20f2cf31b12413b0ddae`, `doc/distributor-account-cleanup-report-workflow-2026-04-16.md`.
  - Next scoped work: run/prepare the report workflow after approved production read/export access; mutation cleanup remains separate until owner and source of truth are defined.
  - Route after scope split: `ws sales` for reporting/account analysis, `ws portal` or `ws ops` only if a later approved cleanup mutates CRM records.

### Portal / Login / Activity Reporting
- Fix OPS <-> Portal SSO/login persistence, including next-day logout behavior.
  - Completed preflight source: login commit `ad6a19760d626e3e709122d311e247187e3df72b`, `docs/2026-04-16-ops-portal-sso-persistence-preflight.md`.
  - Next scoped work: implement only after exact next-day logout policy and Security Guard approval are recorded.
  - Route through `ws login` and `ws ops` with Code and Git Manager plus Security Guard preflight.
- Implement Portal production audit enhancements after definitions are approved.
  - Completed definition source: portal commit `2e076c6c8e47ce54140ddc95704f574adb9f8333`, `docs/production-audit-enhancements.md`.
  - Next scoped work: build extended modification trails, prior-month edit report, shipped-vs-bottled mismatch report, and `<2000 lb` grain/product mismatch logic after rule definitions and Salesreport handoff are clear.
  - Route: `ws portal` for Portal-owned reports, with Salesreport ownership checked for shipped-vs-bottled work.

### IT / Security / Workstations
- Review IT planning docs and decide transfer/deprecation plan for GitLab.
  - Sources: `https://papers.koval/teams/it/task-queue.html`, `https://papers.koval/teams/it/roadmap.html`, `https://papers.koval.lan/teams/it/dashboard.html`, and `https://papers.koval.lan/teams/it/research.html`.
  - Approval gate: no live Papers writes or `.205` work without explicit approval.
- Monitor Google Postmaster.
  - Source: `https://postmaster.google.com/u/0/dashboards#do=kovaldistillery.com&st=userReportedSpamRate&dr=7`.
  - Route: read-only review first; no admin/account changes without approval.

## Done

- **2026-04-16** Event strategy / COT Connecteam replacement coordination review completed locally.
  - Source commit `128c5f1`; added `project_hub/issues/2026-04-16-event-strategy-cot-connecteam-review.md` with local actionable strategy points and OPS-safe next steps. Google Doc source was reachable but returned `HTTP/2 401`, so full external-source review remains blocked pending read-only access or supplied text export. Scope stayed docs-only: no Google Docs mutation, credentials, OPS/Papers/Connecteam/notification/production-data access, code change, commit, push, deploy, or runtime change.

- **2026-04-16** PHPList inventory and distributor cleanup workflow closeouts reconciled.
  - Moved completed source plans into scoped backlog entries and preserved the true remaining blockers. Sources: lists commit `075cd358b784e47c246ef4f5fbd02cfab66facdd`, `docs/phplist-legacy-send-history-read-only-inventory-plan-2026-04-16.md`; salesreport commit `dd58319202d308f86c8e20f2cf31b12413b0ddae`, `doc/distributor-account-cleanup-report-workflow-2026-04-16.md`. Current real manual blocker count: 11 active Waiting items. Docs-only: no external systems, credentials, source workspaces, OPS intake, email, live data, deploys, or runtime services were accessed.

- **2026-04-16** Source workspace planning/review closeouts reconciled into AI TODO.
  - Moved completed source items out of raw open backlog and preserved only scoped next slices or real waiting decisions. Sources: ops commits `18d32a04ddaf5257214d62340eda7e044a1ef3d8` and `478593f3329c49aec9a30ce0464f2f507394a60e`; lists commit `e2ce6afd8706372d2375b7dd50c4c4a0c63091e4`; login commit `ad6a19760d626e3e709122d311e247187e3df72b`; portal commit `2e076c6c8e47ce54140ddc95704f574adb9f8333`; salesreport commit `8004fd93f97ccc0f65db8f4755523facb1370271`. Current real manual blocker count: 8 active Waiting items. Docs-only: no external systems, credentials, OPS intake, email, runtime services, live data, deploys, or source workspace mutation was accessed.

- **2026-04-16** Google Cloud security hardening plan completed.
  - Added `project_hub/issues/2026-04-16-google-cloud-security-hardening-plan.md` with a no-credential checklist, first read-only audit plan, and explicit approval gates for IAM, keys, APIs, billing, Essential Contacts, credentials, live admin surfaces, notifications, deploys, and automation. Scope stayed local docs-only: no Google Cloud console, credentials, keychain, OAuth files, secrets, billing accounts, IAM, live admin surfaces, email, deploy, or runtime service was accessed.

- **2026-04-16** Completed planning/review backlog reconciled from source workspaces.
  - Moved raw open planning items for Salesreport adoption/access, web analytics funnel/source review, and PHPList legacy send-history soft-delete review into this concise Done record. Sources: salesreport commit `85971d9004d1d73c49751d52080a5ec7587f9780` with `doc/salesreport-adoption-access-planning-2026-04-16.md` and `doc/web-analytics-funnel-source-review-2026-04-16.md`; lists commit `a246095d14f07c4e82ebc23fe47e0836a7dded26` with `docs/phplist-legacy-send-history-soft-delete-review-2026-04-16.md`; lists TODO closeout commit `eae015bef06eed50fbbcbacd6324033fa62fb427`. Preserved only scoped future implementation/inventory work and approval gates in Backlog. Docs-only: no OPS intake, credentials, live external systems, email, runtime service, deploy, production data, or source-workspace mutation was accessed.

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
