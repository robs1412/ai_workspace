# Barrel Sales Manager Role Setup

- Master Incident ID: `AI-INC-20260427-BARREL-SALES-MANAGER-ROLE-01`
- Date Opened: 2026-04-27 CDT
- Date Completed: 2026-04-27 CDT
- Owner: AI Workspace / Task Manager
- Priority: Medium
- Status: Completed

## Scope

Robert asked to create another organigram worker for `Barrel Sales Manager` and supplied current WH Barrel Program links, status context, and Avignon/Sonat handling direction.

Approved scope for this slice:

- create the role definition;
- record a detailed Markdown operating sheet for WH Barrel Program and barrel-sample flow;
- make Avignon's Sonat-facing barrel-program route explicit;
- register the role in AI Workspace role docs and operating model;
- add the role to the Workspaceboard organigram source/feed;
- record TODO/project state.

## Symptoms

Barrel-program work can arrive through Sonat to Avignon and can involve Salesreport WH Management pages, Portal POS/Samples sample requests, Matt Andrews' usual reserve/select handling, sold-barrel state, bottling details, task flow, and account/request follow-up. The organigram did not yet have a dedicated worker for this workflow.

## Root Cause

Barrel sample and WH Barrel Program work previously straddled Avignon, Salesreport, Portal, OPS, and sales/account follow-up guidance. Generic sample-request guidance existed, but it needed a separate barrel-program branch so Avignon does not treat barrel requests as normal product sample requests.

## Repo Logs

### ai_workspace

- Repo Log ID: `barrel-sales-manager-role-docs-20260427`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary: Added `worker_roles/barrel-sales-manager.md`; added `avignon/BARREL_PROGRAM_GUIDANCE.md`; updated Avignon request-sample guidance, Avignon role guidance, role README, and operating-model registration.

### workspaceboard

- Repo Log ID: `barrel-sales-manager-organigram-source-20260427`
- Commit SHA: not committed
- Commit Date: not committed
- Change Summary: Added `Barrel Sales Manager` to `worker-organigram.php` role feed so Workspaceboard can display the new role from the AI Workspace `worker_roles` source.

## Operating Rules Recorded

- Sonat email to Avignon about barrel actions should route to Barrel Sales Manager when it asks to reserve, select, unreserve, deselect, create a barrel sample request, mark sold, unsell, check WH Management, check bottling, or handle barrel-program task flow.
- Generic product/sample requests remain regular Portal POS/Samples work unless Sonat explicitly says `barrel sample`, says `barrel`, or links/references WH Barrel Program pages.
- Matt Andrews is recorded as the usual person who reserves and selects barrels.
- Portal POS/Samples is recorded as the sample-request entry surface.
- WH Barrel Program Management requires hitting the green `Run Report` button before treating the view as current.
- Routine bounded internal barrel-program actions can proceed from a clear Sonat request when the packet is complete; real blockers remain unclear target/duplicate ambiguity, missing required fields, external-sensitive commitments, pricing/finance/legal issues, auth/credential issues, destructive/bulk actions, production-impacting changes outside the requested workflow, suspicious mail, and policy conflict.

## Verification Notes

- Read current TODO and append queue before editing.
- Checked existing organigram contract in memory and local source: role docs live in `/Users/werkstatt/ai_workspace/worker_roles`, and `worker-organigram.php` is the live role map.
- Planned checks: Markdown/source text search, `php -l /Users/werkstatt/workspaceboard/worker-organigram.php`, and `git diff --check` on touched repos.

## Rollback Plan

If Robert rejects the role, remove `worker_roles/barrel-sales-manager.md`, remove `avignon/BARREL_PROGRAM_GUIDANCE.md`, remove the Barrel Sales Manager entries from `worker_roles/README.md`, `worker_roles/operating-model.md`, `project_hub/INDEX.md`, this project note, and `/Users/werkstatt/workspaceboard/worker-organigram.php`. Restore the prior Avignon request-sample wording only for the barrel-specific additions. Do not reset or clean unrelated dirty files.

## Follow-Ups

- If Robert wants live execution next, route a visible Barrel Sales Manager or Salesreport/Portal worker for a concrete barrel packet.
- Live Salesreport/Portal actions, external messages, and any code changes remain separate authenticated/routed work.
