# Whole Foods Portal to OPS Outreach Sync

Master Incident ID: `AI-INC-20260427-WHOLE-FOODS-OPS-SYNC-01`
Date opened: 2026-04-27 CDT
Repos/surfaces: `ai_workspace`, future approved `ops`, WFM demo portal, National Outreach worker
Status: open; first approved import complete, future refreshes still needed for pending requests

## Goal

Start the National Outreach tasting-planning directive for syncing Whole Foods demo portal records into OPS Outreach while importing only buyer-approved events. Pending or otherwise not-approved events must be noted but not treated as scheduled OPS events.

## Scope Approved This Pass

- Record the directive and first sync rules.
- Verify non-secret access state for the portal and SOP.
- Identify the OPS target surface and approval boundary.
- Preserve Robert's four source links as trace references.

## Current Findings

- OPS already has an Outreach Events surface and documentation for Whole Foods tastings using the WFM demo portal.
- OPS guidance says Whole Foods tastings should preserve account name, account address, date/time, SKU focus, buyer name when known, and linked account/contact/activity context.
- The two explicit request links Robert supplied include `ApprovedByBuyer=Pending` in the URL:
  - Request `310470`
  - Request `310472`
- Those requests are not approved for import as confirmed OPS events unless the authenticated portal record shows a later approved buyer state.
- Unauthenticated WFM work-order URLs redirect to `AccessDenied.aspx`.
- The private login directory `.private/logins/` now exists with owner-only permissions. Robert supplied the named credential file there, and private authenticated portal inventory succeeded on 2026-04-27.
- The Google Doc metadata is visible as `KOVAL SOP`, and the SOP was later read through approved local/private Drive token handling. The SOP source remains private and was not copied into broad docs.

## 2026-04-27 Read-Only Portal Inventory

Private artifact paths:

- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.tsv`
- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.json`

Scope:

- Authenticated read-only crawl of scheduled daily pages from 2026-04-01 through 2026-06-30.
- Request-detail pages were fetched privately only to classify buyer approval state.

Result:

- 42 event rows found.
- 5 request numbers found: `310465`, `310468`, `310470`, `310472`, `312022`.
- 0 buyer-approved/importable rows found.
- 42 rows are currently not importable because their request links carry `ApprovedByBuyer=Pending`.

Initial inventory alone made no OPS mutation. After Robert supplied explicit approval email evidence for Request `312022`, the approved rows were imported.

## 2026-04-27 Approved Import

Approval evidence:

- Robert supplied the Whole Foods Market Event Schedule Approval email text for Request `312022`.
- Approved product: `0085078600601` / KOVAL Bourbon.
- Approved stores/dates: Lakeview, Evanston, Edgewater Chicago, and Lincoln Park.

OPS result:

- Imported six approved OPS Outreach event bookings: `857`, `858`, `859`, `860`, `861`, `862`.
- Created six linked unassigned Outreach shifts: `5184`, `5185`, `5186`, `5187`, `5188`, `5189`.
- Linked product `18368` (`KOVAL Bourbon [W 47% 6x750ML]`) by normalized UPC match.
- Linked accounts:
  - `24930` for store `10076` / Evanston at `1640 Chicago Ave`.
  - `9163` for store `10643` / Lakeview.
  - `45401` for store `10568` / Edgewater.
  - `1140` for store `10252` / Kingsbury / Lincoln Park.

Audit note:

- Evanston has multiple Whole Foods CRM/store records. The approved event is store `10076` at `1640 Chicago Ave`; Green Bay Road was intentionally not used for this request.
- Lakeview and Kingsbury/Lincoln Park have minor CRM billing-address differences from the portal/store-list address; event location preserves the portal/store-list address and the account-link note records the mismatch.
- A second run of the private import script produced zero created rows and six duplicate matches, confirming the request/store markers prevent duplicate import.

## 2026-04-27 Pending/OPS Reconciliation

Robert noted that some rows shown as portal-pending already happened, so the portal `ApprovedByBuyer=Pending` marker should not be treated as final business truth by itself.

Reconciliation result:

- Remaining portal-pending request groups: `310465`, `310468`, `310470`, `310472`.
- Remaining rows after excluding approved/imported Request `312022`: 36.
- OPS matches found: 36 of 36.
- Interpretation: these are still portal-pending/status-unclear rows in the saved request pages, but they are already present in OPS Outreach, mostly from the Connecteam import.

Reporting rule:

- Use an HTML table for owner-facing status reports.
- Include separate columns for `Portal buyer field`, `Linked in portal`, and `Already in OPS`.
- Add a timing note for rows dated before or on the current date because the portal field may be stale.
- Continue periodic portal refreshes and use approval emails plus OPS/Connecteam state alongside the portal field.

Private artifact:

- `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_pending_ops_status_2026-04-27.html`
- Revised HTML-table email sent to Sonat and Robert; private sent artifact `whole-foods-pending-ops-html-table-2026-04-27.sent-1777327159.json`.

## Durable Directive

Directive file: `nationaloutreach/WHOLE_FOODS_TASTING_PLANNING.md`

Operational rule:

- Import only buyer-approved Whole Foods events into OPS Outreach.
- Note pending/not-approved events in the import report.
- Send Sonat and Robert a confirmation after each import pass, including both imported approved events and events not imported because they are not approved yet.

## Remaining Work

- Continue future Whole Foods refreshes for April-June.
- Do not create duplicate OPS rows for request groups `310465`, `310468`, `310470`, or `310472`; all 36 remaining rows currently have OPS matches already.
- Do not treat portal `Pending` as conclusive if an approval email or OPS/Connecteam schedule evidence says the event is already scheduled or happened.
- Add a routed Salesreport/OPS implementation slice for COTeam suggested samples: for each WFM account, check recent account product orders, add internal notes with other products recently sold and the last-sold date, and keep the account-facing WFM tasting request Bourbon-only unless explicitly approved otherwise. Initial reference report: `https://www.koval-distillery.com/salesreport/salesinvoicereport.php`.
- Move the National Outreach local Drive token to the preferred durable secret path when the approved Infisical contract is available.
- Confirmation for this import was sent from National Outreach to Sonat and Robert; private sent artifact `whole-foods-request-312022-import-2026-04-27.sent-1777326591.json`.

## 2026-04-27 Coverage Recheck

Robert asked for another Whole Foods check and an updated Robert/Sonat report. A live authenticated WFM refresh found the same 42 April-June portal rows across request numbers `310465`, `310468`, `310470`, `310472`, and `312022`.

OPS coverage result:

- 42/42 portal rows have matching OPS Outreach events.
- 0 rows are missing from OPS.
- 42/42 have linked Outreach shifts.
- 28 rows are fully assigned.
- 14 rows still have open/unassigned linked shifts.

Corrected National Outreach report sent to Sonat and Robert: subject `Whole Foods OPS coverage update`, Message-ID `<177733985931.34791.17519709108206868262@kovaldistillery.com>`. Robert clarified the report must be an HTML table and open/unassigned rows should be light red; the National Outreach send helper was fixed to send queued `html_body` as an HTML alternative, and the final HTML-table version was resent with 14 highlighted rows. Final Message-ID `<177734005946.38159.11756804899585654178@kovaldistillery.com>`. Private artifact: `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_ops_coverage_2026-04-27.html`.

Durable templates saved:

- `nationaloutreach/templates/whole-foods-ops-coverage-report.md`
- `nationaloutreach/templates/binnys-ops-coverage-report.md`

## 2026-04-27 Binny's Coverage Report

Robert asked for the same coverage report for Binny's. The source set was the latest approved Connecteam normalized COT import packet, matched to OPS Outreach by Connecteam import key with a conservative date/time/title fallback where needed.

OPS coverage result:

- 39/39 Binny's source rows have matching OPS Outreach events.
- 0 rows are missing from OPS.
- 39/39 have linked Outreach shifts.
- 38 rows are fully assigned.
- 1 row still has a linked shift open/unassigned: `Binny's Joliet`, 2026-05-30 4pm-7pm.

National Outreach HTML-table report sent to Robert: subject `Binny's OPS coverage update`, Message-ID `<177734055890.39230.5962789951459023273@kovaldistillery.com>`. Private artifact: `.private/wholefoods-sync/binnys_ops_coverage_2026-04-27.html`.

## Not Done

- No pending/not-approved Whole Foods rows were imported.
- No portal mutation occurred.
- No credential, cookie, token, or private SOP text was printed or stored in broad docs.

## Next Safe Action

Next safe action is to re-run the authenticated portal inventory later to detect any newly approved request rows. Import only rows with buyer-approval evidence.
