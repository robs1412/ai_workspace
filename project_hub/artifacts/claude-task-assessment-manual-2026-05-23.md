# KOVAL AI Secretary And PM Task Assessment

Date: 2026-05-23
Classification: shared mechanic
Audience: Robert / AI Manager / internal AI workflow owners

## Main Recommendation

Keep the AI Secretary as a routing and dispatch surface, split the vague `PM` label into the actual local roles that own planning versus live follow-through, and require explicit worker execution plus explicit verification before anything is reported complete.

## Why

The current failure mode is role overlap. When Secretary, PM, and implementation blur together, work becomes harder to route, harder to verify, and easier to report as done before the actual worker has finished or before the send/protected-system side is confirmed.

## Local Role Map

- AI Manager: Robert's priority and approval role. This role decides direction, scope changes, and human approvals, but should not become the hidden execution lane.
- Task Manager / Polier: the live execution-management role. This is the closest local match to an operational PM because it routes work, focuses the correct worker, follows through, and keeps board state honest.
- Project Manager: the planning role for multi-step work. This role scopes the task, improves the packet, and defines verification expectations, but does not replace Task Manager and does not quietly do the work.
- Frank / chief of staff: the secretary role for Robert-facing intake, classification, routing, follow-through, and concise completion or blocker reporting.
- Codex / workspace worker: the main coding and implementation lane. This role does the actual technical or operational work inside the correct workspace.
- Verification / closeout: the proof step. Confirm the real source of truth, then report completion or a concrete blocker.

## PM Clarification

- If we keep using the shorthand `PM`, it should not mean `AI Manager`.
- In this local system, `PM` is really split between `Task Manager` for live routing/follow-through and `Project Manager` for planning/decomposition.
- AI Manager stays above both as the human approval and priority surface.

## Practical Rules

- Do not let the Secretary become a hidden execution lane.
- Do not let AI Manager turn into the worker.
- Do not let Task Manager quietly become the implementer.
- Do not let Project Manager quietly perform the work it is supposed to assess and packetize.
- Require a stronger worker packet before execution: owner, goal, constraints, approval boundary, deliverable, and exact verification expectation.
- Keep testing and verification as a separate explicit step before reporting completion.
- Preserve explicit send confirmation and single-writer boundaries whenever mail, auth-gated systems, or other protected surfaces are involved.

## Functional Pickup Boundaries

- Frank stays Robert-facing: direct-owner intake, classification, routing, follow-through, and concise completion or blocker reporting.
- Avignon stays Sonat-facing market execution: sales follow-up, CRM and distributor coordination, calendar and market task flow, and Sonat-owned operational follow-through.
- Vanessa / Outreach Coordinator owns Outreach and tasting coordination: account-facing outreach scheduling, tasting state, and Outreach calendar execution.
- The National Outreach inbox stays in Vanessa's Outreach lane by default: inbox triage, reply-routing, and outreach follow-through belong with the Outreach Coordinator unless the packet clearly becomes a different business lane after review.
- Naomi Stern owns finance operations only: finance intake, close cadence, receipts, reporting readiness, finance controls, and finance follow-through.
- Ezra Katz owns special projects and legal-affairs routing: contracts, policy questions, legal-affairs follow-through, permits, and counsel-ready business packets.
- Codex workers own implementation in the correct workspace after the owner, route, and verification target are clear.

## Pickup Rule

- Do not move work to Naomi just because it is unclaimed. Finance stays with Naomi; Outreach and tasting work stays with Vanessa; Sonat-facing market and CRM follow-through stays with Avignon; special-project and legal-affairs work stays with Ezra; Robert-facing intake and coordination stays with Frank; implementation stays with the routed Codex worker.
- National Outreach inbox work is part of the Vanessa / Outreach lane unless the reviewed packet clearly converts into finance, legal, Robert-facing chief-of-staff follow-through, or another explicit owner lane.
- If a request touches more than one role, Task Manager should split the packet and keep each owner explicit instead of assigning the whole thread to the wrong lane.

## Pickup Order

- First classify the business lane before naming the worker: Robert-facing chief-of-staff follow-through = Frank; Sonat-facing market/CRM/distributor/calendar execution = Avignon; Outreach/tastings/National Outreach inbox coordination = Vanessa; finance operations = Naomi; special projects/legal-affairs routing = Ezra; implementation after the owner is clear = Codex.
- Avignon is not the generic backup for Robert-facing intake, and Naomi is not the generic backup for Vanessa's Outreach work.
- If the owner is still unclear after the business lane is identified, hold the packet with Task Manager for split/routing instead of assigning it by idle capacity.

## Same-Thread Corrections From Robert

- This assessment lane is for Codex workflow analysis, not Naomi operations. Naomi remains finance-only.
- When Claude's project workflow or implementation guide is the object under review, the execution owner is Codex through a visible worker route, with Frank handling Robert-facing intake and completion reporting.
- The practical ask on this thread is: start the worker, analyze Claude's project workflow against our guide, and identify improvements we should make on our side.
- Durable notes on the thread must include the newest owner correction, not just the earlier role split, so later readers do not think the Naomi route or the earlier summary is still current.
- The same-thread repair is now a shared email-worker mechanic, not a one-off Frank fix: replies on an active owner thread should use the newest owner/source message as `In-Reply-To`, preserve `References`, and keep the durable note updated before the completion or blocker report is sent.

## Original Claude Source In Thread

- Original Claude source message: `<83a0ef1a76ebc22e489ab04e0f5873e3.claude@kovaldistillery.com>`.
- Subject: `KOVAL AI Secretary & PM Agent: Task Assessment Manual`.
- Received by Frank at `Sat, 23 May 2026 11:41:14 -0500`.
- Original ask preserved from the local thread record: compare Claude's guide and project workflow against our current guide and identify the workflow improvements we should make on our side.
- First answer preserved from the original Frank assessment draft: keep Frank as a routing surface instead of a hidden execution lane, keep PM and project-manager work focused on planning and task assessment instead of doing the work itself, require a stronger worker packet before execution, keep testing and verification as a separate explicit step before reporting completion, and preserve explicit send confirmation plus single-writer boundaries whenever mail or protected systems are involved.
- Frank's live automation log classified Claude's message as `cc-fyi-no-action`, so the operational follow-through belonged on Robert's later direct-owner thread rather than on Claude's copied note by itself.
- Robert's later correction makes the intended next action explicit: use Claude's task-assessment guide as the source packet, route the actual workflow analysis to a visible Codex worker, and report the concrete improvements back on the Robert thread.

## Next Action

Use this note as the standing operating split for the current AI Secretary / PM lane, and keep the labels explicit: AI Manager, Task Manager, Project Manager, Frank, Codex worker, and verification/closeout. For workflow-assessment requests about Claude/Codex execution, route the analysis to Codex, then send Robert the result with proof from the updated durable note and the actual worker output.
