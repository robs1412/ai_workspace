# Vanessa Tasting Directive Index

Updated: 2026-05-17 CDT
Project: `AI-INC-20260501-AI-WORKERS-SETUP-01`
Lane: `Vanessa Tasting Directives`
Scope: docs-only planning output; no OPS, calendar, mailbox, Portal, or external-send mutation performed in this pass.

## Directive Index

| Duty / workflow | Current directive | Source(s) | Default owner / route | Approval gate or stop condition |
| --- | --- | --- | --- | --- |
| Account tasting correspondence | Vanessa handles tasting coordination through the approved National Outreach route when facts, audience, and sender identity are clear. Keep account wording practical and specific; do not expose Task Flow or worker internals. | `nationaloutreach/PERSONA.md`; `worker_roles/outreach-coordinator.md` | Task Manager -> Email Coordinator -> Outreach Coordinator; send as `vanessa.sterling@kovaldistillery.com` through National Outreach when approved | Pause for new commitments, unclear facts, pricing/terms, external-sensitive sends, suspicious mail, or owner-lane ambiguity |
| Team reminders to tasters | Use OPS event data plus Salesreport chain/account history to tell tasters what products accounts appear to carry. Keep the tone upbeat and supportive for COTeam. | `nationaloutreach/templates/taster-reminder-product-carry.md`; `nationaloutreach/TODO.md`; `nationaloutreach/HANDOFF.md`; `worker_roles/outreach-coordinator.md` | Outreach Coordinator plus OPS scheduling state; send through National Outreach only in approved reminder workflows | Stop if account/product history is unclear, if reminder facts are incomplete, or if the route would require a new send/runtime workflow |
| Open-tastings group messages | Broad staff mailings do not send from the National Outreach mailbox directly. Vanessa can supply the brief and clarifying questions, but audience/campaign mechanics belong in `/Users/werkstatt/lists` and phpList. | `nationaloutreach/TODO.md`; `nationaloutreach/PERSONA.md` | Vanessa brief -> Lists worker / phpList | Approval-gated for broad sends; do not queue a group mailing from National Outreach |
| Whole Foods booking and sync | Import only buyer-approved WFM events into OPS Outreach. Pending or unclear buyer approval does not create confirmed OPS events. Keep the account-facing product request Bourbon-only unless explicitly widened. Internal COTeam notes may add recent sold products and last-sold dates. | `nationaloutreach/WHOLE_FOODS_TASTING_PLANNING.md`; `worker_roles/outreach-coordinator.md`; `salesreport/doc/chain-store-intelligence-basis-2026-05-01.md` | National Outreach coordination -> OPS Outreach worker | Stop on missing approval evidence, nondeterministic CRM match, or any need for external-sensitive reply beyond the approved workflow |
| Mariano's and similar chain tastings | Treat Mariano's and similar routine chain tastings like normal Outreach scheduling work. Use Salesreport Chain Invoice / Chain Store Intelligence as the practical product-carry source. If account scheduling needs OPS mutation, route to an OPS worker. | `worker_roles/outreach-coordinator.md`; `nationaloutreach/HANDOFF.md`; `salesreport/doc/chain-store-intelligence-basis-2026-05-01.md` | Outreach Coordinator -> OPS workspace worker for scheduling state | Pause on staffing commitments, unclear event state, or external promises not already approved |
| Binny's tastings | Use the same Outreach coordination model as Mariano's. For ordinary reminder prep, yesterday's Binny's scraper output can be used as fresher current-placement context when needed, but do not overbuild scraper-vs-invoice comparison. | `nationaloutreach/HANDOFF.md`; `worker_roles/outreach-coordinator.md`; `nationaloutreach/ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md` | Outreach Coordinator -> OPS workspace worker; BID only if the request is scraper/reporting rather than scheduling | Pause on new account commitments or if the work is actually BID/scraper scope instead of Outreach scheduling |
| Illinois compliance check | Regular retail tastings such as Binny's, Mariano's, Whole Foods, and similar ordinary account tastings do not require Sebastian notification solely because a tasting exists. If KOVAL supplies samples directly to a non-routine event, or if the sample-provider path is unclear, flag Sebastian / CAO review. | `nationaloutreach/ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md` | Outreach Coordinator with compliance escalation when needed | Stop for unclear sample-provider path, non-routine venue/event type, or late permit timing |
| OPS organization and Google Calendar | OPS is the durable schedule/state system. Calendar reminders use the shared `KOVAL Outreach Events` path when appropriate, but calendar state supplements OPS and Task Flow rather than replacing them. | `project_hub/issues/2026-05-01-ai-workers-setup.md`; `nationaloutreach/TODO.md`; `worker_roles/outreach-coordinator.md` | OPS workspace worker for schedule changes; shared calendar path for approved reminder/event workflows | Do not make live OPS or calendar mutations in a docs-only lane |
| Mitch Conti weekly overview | Weekly report remains approval-gated before first live send to Mitch. Once approved, send only staffed tastings, regenerate the report from the live builder, and include product/sample-prep guidance. | `nationaloutreach/TODO.md`; `nationaloutreach/HANDOFF.md`; `nationaloutreach/scripts/build_mitch_weekly_report.php` | Vanessa / National Outreach after Robert approval | Do not send to Mitch until Robert explicitly approves the live recipient workflow |

## Account Rule Matrix

| Account family | Intake / source of truth | OPS / calendar rule | Product guidance rule | Communication rule | Escalation trigger |
| --- | --- | --- | --- | --- | --- |
| Whole Foods | WFM portal plus approval email evidence when present | Only approved buyer records become confirmed OPS Outreach events; pending rows stay reported-only | External request stays Bourbon-only unless explicitly widened; internal prep can add recent sold products and last-sold dates | Confirmation/reporting stays internal until approval/import path is satisfied | Missing buyer approval, unclear CRM match, or external-sensitive reply need |
| Mariano's | OPS Outreach state plus normal account coordination threads | Use OPS as durable event/shift state; route schedule changes through OPS worker | Use Salesreport Chain Invoice / Chain Store Intelligence for product-carry notes | Vanessa may coordinate approved account/staff follow-through; no silent OPS mutation from inbox-only work | New commitment, staffing promise, unclear shift state, or unusual account terms |
| Binny's | OPS Outreach state for scheduling; BID scraper context only when current-placement detail matters | Use OPS for event/shift truth; scraper/reporting work routes to BID, not Outreach | Use normal chain-store sales guidance; yesterday's scraper output can supplement reminder prep when needed | Vanessa handles scheduling coordination; BID handles scraper/reporting requests | If the request is really scraper/reporting scope, or if new commitments need human approval |
| Other routine retail chains | OPS Outreach plus account thread and chain-store sales context | Use OPS as schedule truth | Use Salesreport chain/account history as practical product-carry source | Handle through standard Vanessa coordination path | Same gates as Mariano's: unclear facts, commitments, or unusual terms |
| Non-routine Illinois events | Owner packet plus venue/sample-provider facts | Do not rely on ordinary retail assumptions; confirm event type and sample-provider path first | Product plan depends on who is supplying samples | Do not confirm logistics until permit path is clear | Sebastian / CAO review when KOVAL supplies samples directly or facts are unclear |

## Mitch Weekly Overview Verification Checklist

1. Regenerate the weekly report from `nationaloutreach/scripts/build_mitch_weekly_report.php`; do not reuse a stale draft.
2. Confirm the report window matches the intended Monday-Sunday week.
3. Include only staffed tastings; exclude open or unassigned shifts.
4. Keep the current approval gate in place until Robert explicitly authorizes live sends to Mitch.
5. Confirm the output includes the `Product / sample prep` guidance field.
6. Strip Connecteam import tags or similar internal import residue from staff-facing text.
7. If a calendar reminder is part of the workflow, use the shared `KOVAL Outreach Events` path only as a supplement to OPS/task state.

## Open-Tastings Group Message Approval Path

1. Vanessa identifies the business need and prepares the audience/message brief.
2. If the brief is broad staff outreach rather than one-to-one coordination, route it to `/Users/werkstatt/lists`.
3. Lists/phpList owns list selection, campaign draft, sender allowance, suppression handling, and send proof.
4. Keep the send approval gate explicit; do not send broad staff mail directly from National Outreach unless Robert separately approves that path.

## Current Gaps

- No Mariano's-specific standalone directive file exists yet; current guidance is split across Outreach role docs, handoff notes, and the chain-store product-carry rule.
- No generic "other chains" coverage template is linked yet, only Whole Foods and Binny's reusable report templates.
- This lane intentionally did not verify live OPS/calendar/mailbox state because the requested output was a docs-only planning artifact, not an operational send or schedule change.
