# TODO — ai_workspace

Updated: 2026-04-19 08:45 CDT (Machine: RobertMBP-2.local)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- Codex/Claude integration approvals: approve the next no-write work-record projection slice and decide whether Monday OAuth planning should be routed through Security Guard before any Frank/Avignon/Macee token work.
  - Source: `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`.
  - Immediate safe implementation candidate: sanitized read-only JSON projection from TODO/project-hub/Workspaceboard session metadata into a Workspaceboard view, shaped around the Claude-style task-record spine from `ref:2379` (`task #1361`, requester, assigned agent, priority, deliverable bullets, update promise, source ref) and preferring OPS/Portal task IDs where available; no `.205`, Papers write, OAuth, Portal/CRM mutation, mailbox runtime, MCP, or production action.
  - Follow-up tasks to route after approval: Portal existing-account/contact summary workflow; Monday Frank/Avignon OAuth planning; Macee inbox OAuth/template derivation; April 27 Frank national-outreach/Macee handoff email; MI/Papers read-only agent registration.

- OPS/outreach decisions: approve or define the next Connecteam replacement stage and OPS market-improvement product rules before live implementation.
  - Connecteam source: ops commit `18d32a04ddaf5257214d62340eda7e044a1ef3d8`, including docs and `scripts/connecteam_staging_parity.php`.
  - Market improvements source: ops commit `478593f3329c49aec9a30ce0464f2f507394a60e`, `docs/2026-04-16-ops-market-improvements-plan.md`.
  - Decisions still needed: final sync/live schedule/notifications/auth/canonical-rule approval; account/contact request ownership; duplicate rules; account category mapping; Salesreport consumption shape; audit/retention expectations.
  - Approval gates: no `--apply`, final sync, live schedule, notification send, auth/access change, canonical data-rule change, or implementation beyond docs/read-only dry-run until approved.

- Source/access blockers: provide approved read-only access, sanitized exports, screenshots, or reports before the blocked reviews can produce real counts or account findings.
  - Shopify/Square signup recurring checks: lists commit `e2ce6afd8706372d2375b7dd50c4c4a0c63091e4`, `docs/signup-recurring-checks-review-2026-04-16.md`; needs source owner and approved read-only export/API path.
  - PHPList legacy send-history inventory: lists commit `075cd358b784e47c246ef4f5fbd02cfab66facdd`, `docs/phplist-legacy-send-history-read-only-inventory-plan-2026-04-16.md`; needs sanitized export or approved read-only DB/export path.
  - Google Postmaster: session `6ee02528`; needs Google account with Postmaster Tools access for `kovaldistillery.com` or supplied read-only export/screenshot/report.
  - Google Ads: session `258b4242`; public tags found were GA4 `G-4D8S5SQHQ5` and Google Ads `AW-628725001`; needs Ads login/admin access or approved export/screenshot/report.
  - IT Papers GitLab planning: session `e6071659`; `papers.koval` has a TLS hostname mismatch and `papers.koval.lan` redirects to `mi.koval.lan` login; needs Papers/Portal auth or supplied exports.
  - MacBook wake-cause review: AI Workspace commit `02d5dc7`; `MacBookPro.lan` did not resolve, `192.168.55.180` had 100% ping loss, and SSH timed out; needs the MacBook reachable or local log access.
  - Approval gates: no credentials, production DB reads/exports, source-system API access, live account changes, DB mutation, deletion, restore, cleanup, or system-setting changes until each read-only path is approved.

- Sales/analytics/reporting decisions: define owners, report semantics, source-of-truth boundaries, and import contracts before implementation or cleanup.
  - Portal production audit source: portal commit `2e076c6c8e47ce54140ddc95704f574adb9f8333`, `docs/production-audit-enhancements.md`; needs edit-trail definitions, prior-month edit handling, `<2000 lb` rule semantics, and Salesreport handoff decision for shipped-vs-bottled work.
  - Recurring sales/data operations source: salesreport commit `8004fd93f97ccc0f65db8f4755523facb1370271`, `doc/recurring-sales-data-ops-review-2026-04-16.md`; needs importer roster owner, BID refresh cadence, CRM mutation approval, and cleanup owner for distributor/account changes.
  - Distributor cleanup source: salesreport commit `dd58319202d308f86c8e20f2cf31b12413b0ddae`, `doc/distributor-account-cleanup-report-workflow-2026-04-16.md`; needs approved production read/export path and owner/source-of-truth definition for mutations.
  - Web analytics funnel source: salesreport commit `85971d9004d1d73c49751d52080a5ec7587f9780`, `doc/web-analytics-funnel-source-review-2026-04-16.md`; final readiness session `d73ed365`; needs analytics source of truth, scoped surfaces, funnel definitions, aggregate export owner, and import contract.
  - Approval gates: no `saved_reports` DB writes/runs, account changes, tracking changes, production data mutation, deploy, external analytics-system write, CRM mutation, or access-control change without explicit approval.

- Auth/security/storage decisions: define approved session/security policy before any auth or Drive-backed automation work.
  - OPS/Portal SSO persistence source: login commit `ad6a19760d626e3e709122d311e247187e3df72b`, `docs/2026-04-16-ops-portal-sso-persistence-preflight.md`; needs exact next-day logout policy and Security Guard approval.
  - Google Drive OAuth/token storage review: `project_hub/digital-office/storage-decision-needed.md`; recommendation is machine-local OS keychain/private path by default, or an approved secret manager/keychain/service-account path for shared automation.
  - Rejected OAuth/token storage targets: Google Drive-synced files, Google Drive-synced runtime folders, Papers records, normal manifests, and git.
  - Approval gates: no auth/session code change, production session mutation, deploy, live credentialed login test, OAuth credential access, token handling, Drive automation, or shared credential storage until approved.

## Backlog

- Source-owned implementation and review continuations resume only after the matching Waiting-family blocker is cleared.
  - Route implementation from the relevant blocker above into the owning workspace (`ws ops`, `ws lists`, `ws forge`, `ws sales`, `ws importer`, `ws bid`, `ws portal`, `ws login`, or read-only IT/security review) with Code and Git Manager preflight where code or git-backed closeout is involved.
  - Keep source-workspace-specific backlog in the owning workspace once its commit/docs reference is recorded above; do not expand AI Workspace TODO with separate implementation bullets for OPS/outreach, Lists/Forge communications, Salesreport/BID/importer/analytics, Portal/login/activity reporting, or IT/security/workstation reviews.
  - Preserve the approval gates from the matching Waiting family: no credentials, external sends, production DB/export access, source-system API access, auth/session changes, live data mutation, deploy, cleanup, or system-setting changes until explicitly approved.

## Done

- **2026-04-19** AI Manager Robert/Dmytro chain-of-command roles added.
  - Added role docs, operating-model routing, AGENTS/HANDOFF/project-hub notes, and Workspaceboard organigram entries so AI Manager Robert/Dmytro query Task Manager before routing to Codex workers or Claude agents. Live `.205`, OAuth, MI/Papers writes, Portal/CRM mutation, mailbox runtime, MCP exposure, and production actions remain gated.

- **2026-04-17** AI Workspace TODO count-reduction audit completed.
  - Compressed duplicate waiting/backlog entries into grouped blocker families, reduced verbose Done/audit detail in the active queue, and recorded the count policy in `HANDOFF.md`. Follow-up hygiene collapsed source-workspace implementation backlog into one source-owned continuation family. Scope stayed docs-only.

- **2026-04-16** Current planning/source/access closeouts compressed into active blockers and grouped future slices.
  - Source refs remain in the Waiting and Backlog sub-bullets above, `HANDOFF.md`, source-workspace docs, and project-hub notes. This includes OPS, Lists, Login, Portal, Salesreport, Google Postmaster, IT Papers, Google Ads, MacBook wake-cause, and web analytics readiness work from 2026-04-16.

- **2026-04-16** AI Workspace policy, Digital Office, security, Trainual, and operational-planning docs work remains closed.
  - Detailed closure history stays in `HANDOFF.md`, `project_hub/`, `TODO-done-archive-2026-04-16.md`, and git history instead of expanding the active TODO queue.

- Older Done history through 2026-04-15 was moved to `TODO-done-archive-2026-04-16.md` during the 2026-04-16 TODO hygiene pass so this file stays focused on active queue management.
