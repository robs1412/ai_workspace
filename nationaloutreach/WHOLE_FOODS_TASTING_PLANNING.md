# National Outreach - Whole Foods Tasting Planning

Status: directive started 2026-04-27 CDT
Owner route: National Outreach Coordinator -> OPS Outreach worker
Source system: WFM demo portal at `portal.demosystem.net`
OPS target: Outreach Events, not general events

## Directive

Whole Foods demo portal items are imported into OPS only when the buyer approval state is approved. Pending, denied, cancelled, or unclear buyer-approval states must not create confirmed OPS Outreach events or linked shifts from the portal alone.

Important status distinction added 2026-04-27: the portal `ApprovedByBuyer=Pending` field is a portal field/status marker, not always final business truth. If an event is already in OPS from another approved source such as Connecteam, or if the event date has already passed, report the portal field separately from OPS schedule presence and do not imply that the event did not happen. Approval emails remain authoritative approval evidence when they conflict with or outpace the portal field.

For every sync pass, create an import report that separates:

- approved/imported events;
- approved events that could not be imported and why;
- pending or otherwise not-approved events that were intentionally not imported;
- duplicate or already-existing OPS matches;
- whether each portal row is already present in OPS, with the matching OPS event ID when found.

After each successful import pass, send a concise confirmation to Sonat and Robert from the approved National Outreach route. The confirmation must include the approved/imported count, OPS event IDs when available, and the not-approved/pending list. Do not send a confirmation that implies pending events are scheduled.

Use a normal National Outreach email shape: greeting, brief context, an HTML table for tabular reports, and a clean closing such as `Best, National Outreach`.

## Source Links From Robert

- `https://portal.demosystem.net/Pages/WorkOrder/TodaysEvents_Date.aspx?Status=Scheduled&Date=4/25/2026`
- `https://portal.demosystem.net/Pages/WorkOrder/WorkOrderSummary.aspx?Status=Scheduled`
- `https://portal.demosystem.net/Pages/WorkOrder/Edit.aspx?RequestNumber=310470&Status=Scheduled&ApprovedByBuyer=Pending`
- `https://portal.demosystem.net/Pages/WorkOrder/Edit.aspx?RequestNumber=310472&Status=Scheduled&ApprovedByBuyer=Pending`

The two explicit request links above are buyer-approval pending based on their URL parameters. Treat them as not approved until the portal record itself shows an approved buyer state.

## Current Access State

- The private login directory `.private/logins/` now exists with owner-only permissions.
- The named local credential path `.private/logins/wholefoods.txt` is present and was used for a private authenticated read-only portal inventory on 2026-04-27. Credential values were not printed or copied into broad docs.
- The Google Doc metadata is visible to the approved National Outreach Drive identity as `KOVAL SOP`, and non-secret capability metadata says the identity can access the file. Document export/read still failed with `appNotAuthorizedToFile` for the current Drive app/token. The SOP body was not imported into broad docs.

Live OPS import is blocked until at least one portal record shows buyer approval. The SOP document also still needs to be opened/authorized for the approved Drive app or supplied through another approved private source.

## 2026-04-27 Read-Only Inventory

Private artifacts:

- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.tsv`
- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.json`

Read-only crawl scope:

- `Status=Scheduled`
- Daily pages from 2026-04-01 through 2026-06-30
- Authenticated portal session using the private local credential file

Result:

- 42 event rows found.
- 5 request numbers found: `310465`, `310468`, `310470`, `310472`, `312022`.
- 0 buyer-approved/importable rows.
- 42 rows currently not importable because the portal request links carry `ApprovedByBuyer=Pending`.

Current not-approved request groups:

- `310465`: 13 rows across Edgewater Chicago, Lakeview, and Lincoln Park.
- `310468`: 8 rows across One Chicago Square, South Loop, Streeterville, and West Loop.
- `310470`: 8 rows across Evanston, Green Bay Road, Northbrook, and Sauganash.
- `310472`: 7 rows across Elmhurst, Naperville, Schaumburg, Wheaton, and Willowbrook.
- `312022`: 6 rows across Edgewater Chicago, Evanston, Lakeview, and Lincoln Park.

No OPS event, linked shift, external email, portal mutation, or confirmation send occurred from this inventory.

## 2026-04-27 Pending/OPS Reconciliation

After Request `312022` was imported from approval-email evidence, the remaining 36 April-May rows across requests `310465`, `310468`, `310470`, and `310472` were reconciled against OPS.

Result:

- 36 rows still show `Pending` on the saved portal request pages.
- 36 rows have matching OPS Outreach events already, mostly from the Connecteam import.
- Several portal-pending rows are dated before or on 2026-04-27, so the portal-pending field may be stale or incomplete as an operational truth.
- Future reports must show both columns: `Portal buyer field` and `Already in OPS`.
- Periodic portal refresh is needed, but approval emails and existing OPS/Connecteam schedule state must be considered alongside the portal field.

Private artifact:

- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_pending_ops_status_2026-04-27.html`

## OPS Import Rules

Use the existing OPS Outreach Events workflow:

- create under the Outreach surface;
- preserve account/store name and address;
- preserve tasting date, start/end time, SKU/product focus, buyer name when known, and external request number;
- link CRM account/contact/activity when deterministic;
- use OPS as the official schedule only after buyer approval is confirmed;
- create or leave linked shifts according to the existing Outreach staffing policy and coverage rules.

If an approved Whole Foods record lacks a deterministic CRM account/contact match, stage it as review-needed instead of guessing.

## WFM Product Request and COTeam Samples

For WFM account-facing tasting requests, list only KOVAL Bourbon unless Robert or the owner explicitly approves a broader product list. This keeps WFM selection and reservation simple because not all accounts carry every KOVAL product. Bourbon is the foot in the door; COTeam can taste additional products once they are on site.

For internal COTeam notes, add suggested samples when recent account sales data is available:

- check the account's recent product orders, using Salesreport as the preferred source surface;
- include products other than Bourbon that the account recently ordered;
- include what was sold and when it was last sold;
- phrase the note as an internal COTeam suggestion, not as an external WFM product request.
- do not recommend `KOVAL Millet` as a KOVAL tasting-prep product. Millet has moved to Thresh & Winnow; if Millet appears in old KOVAL invoice history, exclude it from KOVAL sample guidance unless Robert explicitly approves a Thresh & Winnow tasting context.

Initial reference surface for the integrated sales check: `https://www.koval-distillery.com/salesreport/salesinvoicereport.php`. Treat this as a rudimentary report reference until a routed Salesreport/OPS implementation adds a deterministic integrated check.

## Report Shape

Owner-facing confirmation:

```text
Whole Foods portal sync is complete.

Imported approved events: N
- OPS #... / Request #... / account / date time

Not imported because not approved yet: N
- Request #... / account if known / buyer approval pending

Not imported for review: N
- Request #... / exact blocker
```

Coverage reports to Robert and Sonat must be sent as HTML table emails, with a plain-text fallback. Highlight unassigned, open, partially assigned, or missing-linked-shift rows in light red so staffing gaps are visible at a glance.

Keep credentials, cookies, portal session values, private SOP text, and raw portal exports out of chat, email, git, and broad docs.
