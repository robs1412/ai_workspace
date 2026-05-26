# Naomi Finance Task Map

Updated: 2026-05-17 CDT
Project: `AI-INC-20260501-AI-WORKERS-SETUP-01`
Lane: `Naomi Finance Setup`
Scope: docs-only planning output; no BID, Portal, QuickBooks, payroll, banking, external-send, or credential mutation performed in this pass.

## Current Role Frame

Naomi is the finance-operations coordinator, not the accountant of record and not an autonomous send/runtime owner. Her lane is to turn BID and Portal finance work into source-aware cadence, controls, owner questions, approval gates, and routed implementation work.

Current known operating context from local BID and AI Workspace records:

- BID already has read-only reporting/status surfaces for finance package status, finance analysis, market analysis, and credit-card statement review.
- Naomi cadence work already has explicit recurring packets for Financial Planning review, credit-card monitoring, and BID improvements feedback.
- Fresh QBO-driven workbook sync and Portal finance report filing were completed on 2026-05-14 through approved read-only and controlled-write paths.
- Naomi is still not send-enabled as a persona.
- Naomi QuickBooks invite acceptance and Naomi Portal/login activation remain separate onboarding/control-lane items when direct system access is required.

## Task Map

| Task area | What Naomi owns | Primary data/source surfaces | Recommended workspace / route | Approval gate | First safe read-only deliverable |
| --- | --- | --- | --- | --- | --- |
| BID reporting and management | Daily and weekly finance-operating review: package freshness, workbook readiness, missing sources, open owner questions, and practical BID improvement notes | `bid/finance_analysis.php`; `bid/finance_packages.php`; `bid/creditcard.php`; `2026 Financial Planning`; `data-management/finance-action-reports/NAOMI-FINANCE-CADENCE-REQUIREMENTS-2026-05-01.md`; BID handoff/readback snapshots | `ws bid` for BID evidence gathering; `ws ai` for cross-workspace finance coordination | No live finance mutation, no money movement, no tax/accounting policy decision, no private finance-source exposure beyond approved metadata | Daily/weekly finance status packet listing checked surfaces, stale/missing sources, practical improvement, blocker, and next owner |
| Financial reports in Portal, currently assigned to Oleg | Define the report calendar, required source package, reviewer path, and which reports can be prepared by Codex versus which remain Oleg-reviewed or owner-approved | Portal `koval_reports` history/readback; `NAOMI-PORTAL-FINANCE-REPORT-TEMPLATES-PROCESS-2026-05-03.md`; HTML samples under `data-management/finance-action-reports/html-samples/2026-05-03/`; BID handoff note for Portal report rows `7947`-`7950` | `ws portal` for approved report-row work; `ws bid` for finance-source preparation; visible Task Manager route when assignment/ownership changes | Portal writes need approved route; reassignment away from Oleg is an owner decision; notification/send behavior must stay explicit | Portal finance report inventory with current templates, report types, current assignee/reviewer, source package requirement, and approval path per report |
| Overdue invoice reminders | Build the evidence and draft queue for receivables follow-up without sending reminders until an approved send path exists | QBO A/R aging package/read-only API or export path; Portal/CRM invoice metadata when approved; Naomi cadence packet; existing QBO AP/AR setup packet | `ws bid` for aging/status evidence; `ws portal` only if approved invoice/contact metadata is needed; Task Manager route for any external reminder lane | External finance reminders require owner approval; ambiguous collections wording or customer/account ambiguity stops the lane; no hidden mailbox sends | Overdue-invoice reminder prep packet with aging basis, target account/contact evidence, draft path, owner question list, and explicit send gate |
| Create invoices from Portal invoices | Define the safe intake, duplicate checks, reviewer sequence, and system boundary before any invoice creation work | Portal invoice records/workflow docs when approved; BID/finance handoff notes; Naomi role docs; any existing Oleg workflow reference | `ws portal` for approved invoice-record work; `ws ai` for control-lane planning; visible worker route required for implementation | Live invoice creation is a business/finance-system mutation and needs explicit owner approval plus deterministic target/source checks | Portal invoice-creation checklist covering source record, duplicate guard, reviewer, posting destination, and proof/readback requirements |
| QuickBooks, A/P, A/R, and workbook sync context | Keep related finance-system work coordinated so Naomi tasks do not duplicate existing API/setup lanes | `QBO-AP-AR-API-SETUP-PACKET-2026-04-30.md`; `AP-AR-FIRST-WORK-PACKET-2026-04-30.md`; Financial Planning readbacks; BID handoff notes | `ws bid` with visible Workspaceboard route | OAuth/auth, tokens, direct QuickBooks setup, and account-access work stay separate approval-gated lanes | Current-state context note: what is already in progress, what remains blocked, and which Task Flow/OPS item already owns the next step |

## Recommended Worker Split

1. `Naomi Finance Setup Worker` in `ws bid`:
   - Own read-only BID finance evidence, workbook cadence, package freshness, and first-pass task packets.
2. `Portal Finance Worker` in `ws portal`:
   - Own approved Portal report-row or invoice-record work after Task Manager confirms write scope and reviewer path.
3. `Task Manager / AI Manager` in `ws ai`:
   - Own assignment questions, Oleg handoff/review path, direct-access onboarding follow-through, and escalation of owner approvals.

## Approval Gates By Task Type

| Task type | Gate |
| --- | --- |
| Live BID or QuickBooks finance mutation | Explicit owner approval plus visible routed worker |
| Portal finance report creation/update | Approved `ws portal` route; reviewer/notification path must be explicit |
| Overdue invoice external reminders | Owner approval for recipient path, wording, and send authority |
| Invoice creation/posting from Portal data | Explicit owner approval; deterministic duplicate/target checks; visible proof/readback |
| Tax/accounting classification or policy decisions | Stop and ask Robert/Sonat; Naomi can prepare evidence only |
| Credentials, OAuth, tokens, private finance-source exposure | Security Guard and approved secure path only |

## Immediate Safe Next Steps

1. Keep Naomi's recurring BID cadence on the read-only/status side: Financial Planning review, credit-card monitoring queue, and BID improvements feedback.
2. Produce the Portal finance report inventory packet before any assignment change away from Oleg.
3. Build the overdue-invoice reminder prep packet from approved aging evidence and stop before any external send.
4. Treat invoice creation from Portal invoices as a separate controlled implementation lane with deterministic duplicate/reviewer checks, not as inbox-only or ad hoc work.
5. Keep QuickBooks/API/onboarding work linked as context and avoid duplicating those setup tasks inside this lane.

## Current Exact Gaps

- Naomi is not send-enabled, so external finance reminders cannot be treated as an already-approved persona send path.
- Naomi direct Portal/login activation is still a separate onboarding/control-lane item if Naomi needs first-person system access.
- The "Financial reports in Portal" lane still names Oleg as the current assignee, so any ownership transfer or autonomous review path needs an owner decision.
- QuickBooks API/onboarding work remains approval-gated and should stay outside this docs-only planning slice.
