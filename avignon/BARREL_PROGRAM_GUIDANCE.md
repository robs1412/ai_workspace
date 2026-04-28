# Avignon Barrel Program Guidance

Updated: 2026-04-27

This is Avignon's standing guidance for Sonat emails about the WH Barrel Program, barrel samples, reservations, sold barrels, bottling, and barrel-program task flow.

## When To Use This

Use this guidance when Sonat asks Avignon to:

- reserve or unreserve a barrel;
- select or deselect a barrel for a request;
- create a barrel sample request;
- mark a barrel as sold or unsell a barrel;
- check WH Barrel Program status;
- check bottling schedule, invoice context, program details, sticker ETA, ABV, bottle size, or barrel notes;
- complete, reassign, or inspect barrel-program tasks;
- follow up on a barrel sample request needing attention.

Do not use this guidance for a generic product/sample request unless Sonat explicitly says `barrel sample`, says `barrel`, or links/references the WH Barrel Program pages.

## Key Links

- WH Barrel Program Management: `https://www.koval-distillery.com/salesreport/wh_barrel_program_management.php`
  - Hit the green `Run Report` button before treating the page as current.
- Available and reserved barrels: `https://www.koval-distillery.com/salesreport/wh_barrel_program_available.php`
- Bottling schedule: `https://www.koval-distillery.com/salesreport/wh_barrel_program_bottling.php`
- Barrel detail: `https://www.koval-distillery.com/salesreport/wh_barrel_detail.php?barrel_number=####`
- Manual: `https://www.koval-distillery.com/salesreport/barrelprogram.md`
- Portal sample request area: `https://portal.koval-distillery.com/#/pos-and-samples/sample-requests`

## Ownership Pattern

- Sonat can send Avignon barrel-program work.
- Matt Andrews usually reserves barrels and selects them.
- Barrel Sales Manager owns the workflow coordination and should be the specialist route for these requests.
- Salesreport owns the WH Barrel Program pages and report/action behavior.
- Portal owns POS/Samples sample-request entry and related CRM-linked request data.
- Avignon owns Sonat-facing acknowledgement, routing, completion, or blocker reporting.

## Intake Packet

For a barrel action, capture:

- barrel number(s);
- requested action: reserve, unreserve, select, deselect, mark sold, unsell, check, remind, create request, assign, reassign, update notes/details;
- account/company and contact if known;
- sample request or program context if known;
- date needed and bottling/program details if supplied;
- whether Matt has already reserved/selected the barrel;
- completion-report target, normally Sonat.

If any of the required business target fields are missing, ask one concrete question in plain English. Do not ask Sonat to work from Message-IDs or old thread ids.

## Routine Execution Rule

Sonat's clear request is routine approval for bounded internal barrel-program execution when the packet is complete. Avignon should route the work to Barrel Sales Manager and the correct visible workspace worker without asking Sonat for a second approval.

Sold attribution must follow the person who actually pushed the Salesreport/Portal `sold` action. If that person is unclear, ask one concrete question before marking sold. If Sonat emails that she sold a barrel or says `I sold`, it is safe to treat Sonat as the seller; the final Salesreport/Portal barrel state, created barrel project, and created child tasks should attribute to Sonat user id `3`, not the Codex automation user.

Do not create generic promote/social-media tasks from barrel sales. Robert clarified those tasks do not help barrel sales. Prefer useful post-sale follow-up such as account feedback, reorder opportunity checks, distributor/account follow-up, bottling readiness, sticker/artwork readiness, POS needs, and invoice/bottling completion.

Pause only for real gates:

- unclear barrel/account/request target after deterministic checks;
- duplicate ambiguity;
- missing account/contact/request fields required for Portal entry;
- external-sensitive customer commitment or outbound message;
- pricing, invoice, finance, legal, or unusual partner terms;
- auth, credential, 2FA, or permission blocker;
- destructive/bulk action;
- production-impacting code/runtime change outside the requested routine workflow;
- suspicious mail or policy conflict.

## Completion Report

When complete, Avignon reports to Sonat unless Robert is supervising the lane. The report should say:

- what was done;
- which barrel(s), account/request, and page/action were involved;
- what changed;
- what was verified after the action;
- what was not done;
- any remaining missing fields, approval gates, or human owner actions.

Keep the report business-first and concise. Internal session ids and source ids are trace references only.
