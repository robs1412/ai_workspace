# National Outreach TODO

## Open

- Mitch Conti weekly upcoming tastings report is approval-gated.
  - Robert received the review-copy report on 2026-04-27 from National Outreach. Do not send to Mitch until Robert gives explicit go-ahead after review.
  - Requested future recipient after approval: `"Conti, Mitch" <Mitch.Conti@rndc-usa.com>`, cc Robert.
  - Cadence after approval: every Monday at 8:00am, upcoming tastings for that week.
  - Until Robert gives go-ahead, remind Robert daily that approval is pending.

- Whole Foods portal -> OPS Outreach sync directive is active.
  - Import only buyer-approved Whole Foods events. Pending/not-approved portal items must be noted but not imported as confirmed OPS events.
  - WFM tasting requests should remain Bourbon-only in the account-facing request unless explicitly approved otherwise; internal COTeam notes should include suggested additional samples from recent account sales when available, including what sold and when it was last sold.
  - Follow-up implementation needed: add an integrated Salesreport-backed check for recent account product orders to feed the COTeam suggested-samples note. Reference report: `https://www.koval-distillery.com/salesreport/salesinvoicereport.php`.
  - Credential blocker resolved: `.private/logins/wholefoods.txt` is present and a private authenticated portal crawl succeeded.
  - 2026-04-27 first approved import complete for approval email Request `312022`: OPS events `857`-`862`, linked shifts `5184`-`5189`.
  - 2026-04-27 coverage recheck complete: 42/42 WFM portal rows are in OPS, 0 missing, 42/42 have linked Outreach shifts, 28 fully assigned, 14 open/unassigned. Final HTML-table report with 14 light-red open/unassigned rows sent to Sonat and Robert from National Outreach.
  - Future WFM coverage reports should use `templates/whole-foods-ops-coverage-report.md`.
  - Remaining open sync work: future refreshes for April-June requests `310465`, `310468`, `310470`, and `310472`; these remain not approved/pending and must not be imported until approval evidence exists.
  - Directive: `WHOLE_FOODS_TASTING_PLANNING.md`; project log: `../project_hub/issues/2026-04-27-whole-foods-ops-sync.md`.

## Done

- 2026-04-27: Created local National Outreach worker folder and persona for `nationaloutreach@kovaldistillery.com`; private mailbox setup verified separately without reading bodies or sending mail.
- 2026-04-27: Imported approved Whole Foods Request `312022` into OPS Outreach from Robert-supplied approval email evidence; created six event bookings and six unassigned Outreach shifts; linked CRM accounts and KOVAL Bourbon product where deterministic.
- 2026-04-27: Sent Binny's OPS coverage report to Robert: 39/39 in OPS, 0 missing, 39/39 linked shifts, 38 fully assigned, 1 open/unassigned (`Binny's Joliet`, 2026-05-30 4pm-7pm). Saved reusable Whole Foods and Binny's HTML-table report templates.
