# TODO — ai_workspace

Updated: 2026-04-19 10:12 CDT (Machine: Macmini.lan)

## In Progress

_No active AI Workspace implementation items._

## Waiting for Next Step

- Codex / Claude / Papers integration: Robert's 2026-04-19 directives are recorded and routed; worker outputs are waiting for approval/input before implementation.
  - Source log: `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`; Master ID `AI-INC-20260419-CODEX-CLAUDE-PAPERS-01`.
  - Routed sessions: Codex Integration Manager `b66fdade`; Portal existing-account summary design `ba888628`; Portal fixture-only dry-run replacement `d3f5b188`; Frank/Macee/national outreach dated task records `2e9c321b`; AI-Bridge read-only MI/Papers registration design `f66bd3cb`; Security Guard OAuth follow-up review `71ab6f94`.
  - Current status: role docs and Workspaceboard organigram source include Codex Integration Manager, Outreach Communicator, Codex Local Agent, Claude Server Agent, Claude `.205` Structure, AI Manager Robert, and AI Manager Dmytro. Frank created the Macee and 2026-04-27 national outreach task records; Security Guard recorded the OAuth planning checklist; Portal and AI-Bridge produced read-only designs; Robert approved a Portal fixture-only dry run and worker `d3f5b188` is running it.
  - Approval gates still closed: no `.205`, OAuth, Papers/MI writes, Portal/CRM mutation, mailbox credential/content exposure, MCP exposure, deploy/live pull, service restart, or external email send without separate approval.

- Frank/Avignon Gmail push: parked until Monday, 2026-04-20; keep current 15-second polling and verify polling health first.
  - Source log: `project_hub/issues/2026-04-18-frank-avignon-gmail-push-plan.md`; Master ID `AI-INC-20260418-FRANK-AVIGNON-GMAIL-PUSH-01`.
  - Current local non-secret evidence: Frank/Avignon use machine-local IMAP/SMTP polling/sending via LaunchAgents; no local evidence of Gmail `users.watch`, Pub/Sub topic/subscription, persisted `historyId`, or watch-renewal state. Separate `/Users/werkstatt/Gmailconnector` uses Gmail API OAuth read-only for search/export but is not wired into Frank/Avignon monitors and has local token metadata for Robert/Sonat/Oleg/Sebastian only, not Frank or Avignon.
  - Immediate installed improvement: `com.koval.frank-auto` and `com.koval.avignon-auto` now poll every `15` seconds instead of `60` seconds, using the same duplicate-protected inbox cycle, handled-mail filing rules, completion-report/decision behavior, and persona routing.
  - Pause directive from Robert on 2026-04-18: keep email handling on the current 15-second polling path until Monday, 2026-04-20. On Monday, verify polling health first. Resume Gmail API push/OAuth/PubSub only from the M4 ERTC Google auth context if still needed.
  - Hard boundaries before Monday approval: no Google Cloud/Pub/Sub/IAM mutation, no OAuth token work, no mailbox content read, no runtime cadence change, no deploy/push/live pull for the Gmail push slice, and no Google auth changes unless Robert explicitly reopens this before Monday.
  - Recommended safe path after Monday health check, if still needed: approved Google Cloud project/topic/subscription from the M4 ERTC Google auth context, `users.watch` for Frank and Avignon with `INBOX` include filter, pull subscriber or authenticated approved HTTPS endpoint, machine-local `historyId` persistence, `users.history.list` processing, fallback periodic sync, daily watch renewal, duplicate protection, and normal Task Manager routing/completion-report workflow.
  - Robert decision email sent via Frank at 2026-04-18 11:06 CDT: subject `Frank/Avignon Gmail push: concrete approvals needed`, task id `frank-2026-gmail-push-approval-packet-2026-04-18`, Message-ID `<177652840568.70175.10644898545170796700@kovaldistillery.com>`, draft `frank/drafts/gmail-push-approval-packet-robert-2026-04-18.txt`, Robert-only recipient.
  - Decisions now requested from Robert in that email: choose/create Google Cloud project; name Pub/Sub topic/subscription/IAM owner; approve/reject Gmail API `users.watch` for Frank and Avignon with minimum mailbox scope; approve/reject Mac mini machine-local token/historyId storage; approve/reject pull-subscriber/runtime LaunchAgent slice with fallback periodic sync and no cadence change until separately installed; decide whether MacBook local Codex gets setup instructions only or may also run supplemental workers.
  - Monday follow-up task: verify `com.koval.frank-auto` and `com.koval.avignon-auto` polling health, last exits, recent run timestamps, error logs, duplicate-protection behavior, and captured/routed acknowledgement behavior. Only after that health check should Task Manager decide whether Gmail API push is still needed.
  - Monday morning update addition from Robert on 2026-04-19: include Mac mini hard-server-mode planning alongside the Gmail polling/OAuth health follow-up. Scope for the update: wire the Mac mini; plan turning the Mac mini into hard server mode; migrate/verify critical Workspaceboard, Frank, and Avignon services so logout of the Aqua/GUI session is safe; only then consider logging out the old workstation GUI session.
  - Hard-server-mode boundaries from this note: no service migration, logout, LaunchDaemon change, service restart, LaunchAgent/runtime change, runtime cadence change, OAuth work, mailbox read, credential access, Workspaceboard mutation, deploy, push, or live pull is approved by adding this follow-up.

- OPS/outreach decisions: Connecteam staged-window parity approved; remaining blocker is final read-only re-sync/export plus OPS market account/contact product rules before live writes.
  - Connecteam source: ops commit `18d32a04ddaf5257214d62340eda7e044a1ef3d8`, including docs and `scripts/connecteam_staging_parity.php`.
  - Approved 2026-04-18: Robert accepted OPS Outreach as parity-ready for the staged Connecteam window `2026-03-31` to `2026-05-30`. The approval covers the docs-only packet `ops/docs/2026-04-17-connecteam-parity-readiness-approval-packet.md`, where `151/151` staged rows matched OPS with linked shifts, `0` safe-to-apply rows, `0` review-needed rows, and a clean `17`-user crosswalk.
  - Worker-ready OPS next task: run one final read-only Connecteam re-sync/export before decommission, regenerate/review parity, bridge-plan, and user-crosswalk artifacts, and produce a new approval packet showing deltas since the approved staged window. Boundary: no `--apply`, no Connecteam decommission, no OPS/Portal/CRM mutation, no Google sync mutation, no notification send, no auth/canonical-rule change, no deploy, no push, no live pull, and no source-task closure.
  - Market improvements source: ops commit `478593f3329c49aec9a30ce0464f2f507394a60e`, `docs/2026-04-16-ops-market-improvements-plan.md`.
  - Market narrowed next slice: keep work to read-only `market_readiness` / `ops.market_events.v1` export preview and Code/Git review of any already-produced local OPS slice. Do not start account/contact creation from OPS yet.
  - Decisions still needed from Robert/source owners: final Connecteam re-sync/export scheduling details and decommission go/no-go after the final packet; whether zero-shift Outreach events are tentative holds or hard-blocked; Outreach notification groups/channels; claim/unclaim approval and cutoff rules; reminder timing/channels; canonical account/activity behavior when multiple links exist; account/contact request owner and approver; direct OPS CRM creation vs pending Portal/CRM review; duplicate-match rules; required account category mapping; Salesreport consumption shape; audit/retention fields.
  - Approval gates still closed: no `--apply`, decommission, live schedule change, notification send, auth/access change, canonical data-rule change, CRM account/contact mutation, Salesreport production-table/import change, deploy, push, live pull, or source task closure until explicitly approved.

- Source/access blockers: narrowed to remaining read-only source inputs; Google Ads is routed out of Codex access tracking.
  - Shopify/Square signup recurring checks: lists commit `e2ce6afd8706372d2375b7dd50c4c4a0c63091e4`, `docs/signup-recurring-checks-review-2026-04-16.md`; local Lists evidence shows no Square signup implementation and only a Shopify Forge planner reference. Frank sent Claude the status request `frank-2026-claude-square-shopify-list-links` on 2026-04-17; needs Claude/source owner reply with OPS task IDs, source-of-truth record, Google Doc/Drive links if any, and an approved read-only export/report/API path before Lists/Forge can do real counts.
  - PHPList legacy send-history inventory: lists commit `075cd358b784e47c246ef4f5fbd02cfab66facdd`, `docs/phplist-legacy-send-history-read-only-inventory-plan-2026-04-16.md`; needs sanitized export or approved read-only DB/export path.
  - Google Postmaster: session `6ee02528`; needs Google account with Postmaster Tools access for `kovaldistillery.com` or supplied read-only export/screenshot/report.
  - IT Papers GitLab planning: source session `e6071659`; Frank task `frank-2026-claude-papers-completion-reporting`; Claude replied on 2026-04-17 that the Papers MCP is live at `https://papers.koval.lan/mcp`, and Robert replied that this should route to Task Manager / Workspaceboard. Execution chain: Workspaceboard scoping worker `c6421ac1` verified no-secret MCP reachability/tool schema; Security Guard `c2e66c43` classified the endpoint as sensitive and required a deny-by-default read-only wrapper; Code/Git Manager `9a4787cd` cleared design-only planning but blocked implementation until dirty worktree ownership is resolved; design worker `778ef252` produced the read-only wrapper plan. Decision now needed: approve or reject live read-only Workspaceboard access to Papers through that wrapper and name the initial allowed scopes/collections and document IDs. Approval gates remain closed for Papers writes, credential/auth handling, `.205` access, MCP config changes, LaunchAgent/runtime changes, production mutation, code edits without Code/Git Manager, or private mailbox-body exposure.
  - MacBook wake-cause review: AI Workspace commit `02d5dc7`; 2026-04-17 reachability recheck still failed (`MacBookPro.lan` unresolved, `192.168.55.180` 100% ping loss, SSH/TCP 22 timeout); needs the MacBook reachable on LAN/VPN or a local wake-cause log excerpt/report supplied from the MacBook.
  - Closed/routed out: Google Ads session `258b4242`; public tags found were GA4 `G-4D8S5SQHQ5` and Google Ads `AW-628725001`, but Robert confirmed on 2026-04-17 that Claude/Sonat own the Google Ads credit/current-state item. Frank and Avignon filed/routed the email evidence; Codex should not request Ads login/admin access for this item unless Robert reopens it.
  - 2026-04-18 11:04 CDT local-docs sweep: no new safe source inputs were found for Shopify/Square, PHPList, Postmaster, Papers live read access, or MacBook wake-cause. Remaining work still needs supplied read-only material or explicit approval; no mailbox bodies, credentials, external systems, source APIs, production DBs, or runtime state were accessed.
  - Approval gates: no credentials, production DB reads/exports, source-system API access, live account changes, DB mutation, deletion, restore, cleanup, or system-setting changes until each read-only path is approved.

- Sales/analytics/reporting decisions: define owners, report semantics, source-of-truth boundaries, and import contracts before implementation or cleanup.
  - Portal production audit source: portal commit `2e076c6c8e47ce54140ddc95704f574adb9f8333`, `docs/production-audit-enhancements.md`; needs edit-trail definitions, prior-month edit handling, `<2000 lb` rule semantics, and Salesreport handoff decision for shipped-vs-bottled work.
  - Recurring sales/data operations source: salesreport commit `8004fd93f97ccc0f65db8f4755523facb1370271`, `doc/recurring-sales-data-ops-review-2026-04-16.md`; needs importer roster owner, BID refresh cadence, CRM mutation approval, and cleanup owner for distributor/account changes.
  - Distributor cleanup source: salesreport commit `dd58319202d308f86c8e20f2cf31b12413b0ddae`, `doc/distributor-account-cleanup-report-workflow-2026-04-16.md`; needs approved production read/export path and owner/source-of-truth definition for mutations.
  - Web analytics funnel source: salesreport commit `85971d9004d1d73c49751d52080a5ec7587f9780`, `doc/web-analytics-funnel-source-review-2026-04-16.md`; final readiness session `d73ed365`; needs analytics source of truth, scoped surfaces, funnel definitions, aggregate export owner, and import contract.
  - AI sales analytics decision-matrix source: `/Users/werkstatt/salesreport/doc/sales-analytics-decision-matrix-2026-04-18.md`; local docs-only slice completed for OPS `366208`. Current decision packet: wired CRM-backed summaries and National Sales Assistant CRM sections are candidates for an approved first monthly packet; top-product and channel-comparison reports are stubbed; new prospects/open-status/web analytics remain outside-source/manual until owners approve inputs.
  - Approval gates: no `saved_reports` DB writes/runs, account changes, tracking changes, production data mutation, deploy, external analytics-system write, CRM mutation, or access-control change without explicit approval.

## Backlog

_No separate AI Workspace backlog items. Source-owned continuations are already represented by the matching Waiting-family blocker above and should resume in the owning workspace only after that blocker clears._

## Done

- **2026-04-19** Mac mini hard-server-mode Monday follow-up recorded.
  - Added Robert's Monday morning update item alongside the Gmail polling/OAuth health follow-up: wire Mac mini, hard-server-mode plan, migrate/verify Workspaceboard/Frank/Avignon critical services before Aqua/GUI logout, and only then consider old workstation GUI logout. Docs-only; no service migration, logout, LaunchDaemon change, service restart, LaunchAgent/runtime change, deploy, push, live pull, credential access, OAuth, mailbox read, or Workspaceboard mutation was performed.

- **2026-04-19** Security Guard OAuth follow-up checklist recorded.
  - Added a non-secret planning-only checklist for Monday Frank/Avignon OAuth follow-up and future Macee inbox/template work. It records owner paths, minimum scopes, storage boundaries, blocked pre-approval actions, due-date handling, and remaining Robert decisions. No OAuth, Google auth, mailbox content read, credential/token path disclosure, Google Cloud/PubSub/IAM mutation, runtime cadence change, deploy/live pull/service restart, external send, or mailbox mutation was performed.

- **2026-04-18** Frank direct-email recovery routing directive recorded.
  - Recorded Robert's recovery note that direct Frank emails were silently logged as local-routing/no-email. Updated central, Frank, Avignon, and worker-role docs so direct primary-owner emails that report breakage, give approval, ask status, or instruct work must route to visible Task Manager/board-managed workers and send a concise captured/routed acknowledgement with duplicate protection. Also recorded recovered phone-access and Gmail/OAuth instruction items in handoff. Docs/handoff only; no mailbox content, secrets, runtime, LaunchAgent, or external-system state changed in this update.

- **2026-04-18** Frank/Avignon Gmail fast-poll runtime improvement installed.
  - Changed machine-local LaunchAgents `com.koval.frank-auto` and `com.koval.avignon-auto` from 60-second to 15-second polling, reloaded/enabled/kickstarted both, and verified last exit `0`. True Gmail push is not enabled because Frank/Avignon Gmail API OAuth and Pub/Sub setup are not locally available.

- **2026-04-18** AI source/access blocker sweep rechecked.
  - Reviewed local TODO/HANDOFF/project docs only. No new safe source inputs were found for Shopify/Square, PHPList, Google Postmaster, Papers live read access, or MacBook wake-cause; Google Ads remains routed out of Codex access tracking. Also aligned project-hub status for the Avignon CRM intake audit to the narrowed source `1`/source `10` decision blockers. No credentials, mailbox bodies, external systems, source APIs, production DBs, runtime state, email, deploy, commit, or push were accessed.

- **2026-04-18** Frank/Avignon mandatory completion-report correction recorded.
  - Updated the chief-of-staff directive so accomplished tasks require a clear report email by default unless explicitly suppressed. Reports must include what was done, what changed, links/session IDs/task IDs, what was not done, and remaining decisions; Frank defaults to Robert, Avignon defaults to Sonat with Robert included only when required. Docs-only; no runtime/mailbox/send/cadence change.

- **2026-04-18** Frank/Avignon chief-of-staff email-worker directive recorded.
  - Updated AI Workspace, worker-role, Frank, and Avignon docs so clear low-risk internal email tasks route through visible board-managed workers with full briefs, start verification, completion monitoring, TODO/project/handled-mail updates, required owner completion reports, duplicate protection, FYI/CC filing, and 24-hour decision follow-up. Approval gates and docs-only/runtime boundaries remain intact.

- **2026-04-18** UI/report/page completion-output directive recorded.
  - Updated AI Workspace policy/role docs and handoff so completed UI/report/page workers must report findable user-facing location, deploy/live state, verification, changed files/commit SHA, auth/gating, redirect compatibility, and remaining action before closure. Added the Salesreport live-pull rule for safe implemented/verified/committed/pushed UI/report/menu changes. Also recorded the corrected Salesreport market-events note. Scope stayed docs-only.

- **2026-04-18** OPS Outreach staged Connecteam parity accepted.
  - Robert approved OPS Outreach as parity-ready for the staged `2026-03-31` to `2026-05-30` Connecteam window. Remaining Connecteam work is limited to one final read-only re-sync/export and new approval packet before decommission; no `--apply`, live mutation, decommission, notification, deploy, push, live pull, or source-task closure was approved.

- **2026-04-17** Source/access blocker cleanup completed.
  - Reviewed local TODO/HANDOFF/session evidence and source docs only. Google Ads is no longer a Codex access blocker because Robert routed ownership to Claude/Sonat; Square/Shopify and Papers have Claude status/guidance requests pending; MacBook reachability still fails; PHPList and Postmaster still need supplied read-only material. No credentials, account access, external APIs, production DBs, exports, mailbox contents, system settings, or live services were accessed.

- **2026-04-17** Auth/security/storage policy blocker closed.
  - Robert approved the default OPS/Portal persistence policy: explicit logout revokes Login/OPS/Portal artifacts globally, and next-day Portal/OPS access requires a fresh Login handoff/user action unless longer app persistence is explicitly approved. OAuth/token rejected storage targets remain closed as policy; future auth/storage implementation still requires Security Guard review and the normal no-credential/no-live-change gates.

- **2026-04-17** Cross-workspace TODO reduction continuation completed.
  - Board open count reduced from `15` to `10` by closing duplicate/deferred/routed rows in Braincloud, Frank, Importer, and OPS. Real blockers remain in AI Workspace grouped decisions, OPS/Portal task IDs, project-hub notes, or visible worker sessions. No risky implementation, credentials, deploy, mailbox mutation, broad git cleanup, or production mutation was performed.

- **2026-04-17** Cross-workspace TODO reduction pass completed.
  - Board open count reduced from `30` to `15` by closing/routing duplicate, stale, placeholder, standing-monitor, and external-owner TODO rows across AI Workspace child/module queues. A new OPS auth/session blocker appeared during the pass and remains open. No code implementation, OPS/Portal mutation, CRM write, email send, credential access, deploy, live pull, git cleanup, session close, or external-system change was performed.

- **2026-04-17** Summary directive policy correction completed.
  - Updated AI Workspace, Task Manager/Summary Worker, Frank, and Avignon docs/TODO/HANDOFF to record: morning summaries are upcoming-work summaries; evening summaries are accomplished Task Manager/board-work summaries. Preserved anti-spam and decision-email rules. No runtime, LaunchAgent, mailbox, send, credential, or external-system state was changed; Avignon evening runtime and Frank Task Manager-source alignment remain separate implementation-worker work if Robert wants them live.

- **2026-04-17** Frank/Avignon communication directive audit completed.
  - Tightened AI Workspace and local worker-role docs for request source tracking, routed-work status updates, direct safe tracked replies, completion confirmations, and exception-only decision prompts. The morning-only summary boundary from this pass was superseded by Robert's 11:56 clarification; no runtime or mailbox state was changed.

- **2026-04-17** AI Workspace TODO count-reduction audit completed.
  - Compressed duplicate waiting/backlog entries into grouped blocker families, reduced verbose Done/audit detail in the active queue, and recorded the count policy in `HANDOFF.md`. Follow-up hygiene collapsed source-workspace implementation backlog into one source-owned continuation family. Scope stayed docs-only.

- **2026-04-16** Current planning/source/access closeouts compressed into active blockers and grouped future slices.
  - Source refs remain in the Waiting and Backlog sub-bullets above, `HANDOFF.md`, source-workspace docs, and project-hub notes. This includes OPS, Lists, Login, Portal, Salesreport, Google Postmaster, IT Papers, Google Ads, MacBook wake-cause, and web analytics readiness work from 2026-04-16.

- **2026-04-16** AI Workspace policy, Digital Office, security, Trainual, and operational-planning docs work remains closed.
  - Detailed closure history stays in `HANDOFF.md`, `project_hub/`, `TODO-done-archive-2026-04-16.md`, and git history instead of expanding the active TODO queue.

- Older Done history through 2026-04-15 was moved to `TODO-done-archive-2026-04-16.md` during the 2026-04-16 TODO hygiene pass so this file stays focused on active queue management.
