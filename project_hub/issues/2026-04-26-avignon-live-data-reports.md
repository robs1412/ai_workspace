# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260426-AVIGNON-LIVE-DATA-REPORTS-01`
- Date Opened: 2026-04-26
- Date Completed: 2026-04-26
- Owner: Avignon / Sonat
- Priority: Normal
- Status: Completed

## Scope

Create actual Avignon reports from live reporting data, publish them to live Salesreport/Contactreport paths, and send Sonat links. This replaced prior sample/demo pages with live-data pages.

## Symptoms

Robert clarified that Sonat needed actual report pages with live pulled data, not a summary of what Avignon would do or demo-only samples. `.230` local HTML access was not acceptable for delivery, so the reports needed to be pushed and pulled live.

## Root Cause

The first correction created static sample pages and sent live sample links, but did not query Salesreport/Contactreport data. The requested deliverable was live-data reporting output.

## Repo Logs

### salesreport

- Repo Log ID: `salesreport-avignon-live-data-reports-2026-04-26`
- Commit SHA: `bc5bf07`
- Commit Date: 2026-04-26
- Change Summary: Added `scripts/generate_avignon_live_reports.php`, `avignon-live-prior-month-performance-audit-2026-04-26.php`, and `avignon-live-distributor-support-readiness-2026-04-26.php`.

- Repo Log ID: `salesreport-avignon-live-report-gate-2026-04-26`
- Commit SHA: `0178b94`
- Commit Date: 2026-04-26
- Change Summary: Moved all five live Avignon reports under `/salesreport`, added `avignon_report_access.php`, included the Salesreport header/session gate, and limited access to the KPI admin usernames `admin`, `sonat`, `sebastiansaller`, and `mark`.

- Repo Log ID: `salesreport-avignon-strategic-outreach-reports-2026-04-26`
- Commit SHA: `409e791`
- Commit Date: 2026-04-26
- Change Summary: Added `scripts/generate_avignon_additional_reports.php`, `scripts/generate_avignon_outreach_biweekly_report.php`, and four more gated live report pages: win-back/inactive nudges, whitespace/POD opportunities, Illinois core SKU velocity, and Outreach Team bi-weekly overview.

### contactreport

- Repo Log ID: `contactreport-avignon-live-data-reports-2026-04-26`
- Commit SHA: `4a798be`
- Commit Date: 2026-04-26
- Change Summary: Added `avignon-live-street-intel-pulse-2026-04-26.php`, `avignon-live-tasting-opportunity-report-2026-04-26.php`, and `avignon-live-friday-drafts-decanters-2026-04-26.php`.

- Repo Log ID: `contactreport-avignon-live-report-redirects-2026-04-26`
- Commit SHA: `4d81ec2`
- Commit Date: 2026-04-26
- Change Summary: Converted old Contactreport Avignon live report URLs into redirects to the gated Salesreport report pages.

## Verification Notes

- Generator ran read-only against CRM/reporting DBs from the Salesreport workspace.
- Reports include March 2026 sales, April 2026 Contact Report activity/tastings through April 26, Illinois retail tasting targets, slipped accounts, and support-readiness signals.
- Local `php -l` passed for the generator and all five generated pages.
- Live `/home/koval/public_html/salesreport` pulled to `bc5bf07`; the pre-existing live `.htaccess` modification was preserved.
- Live `/home/koval/public_html/contactreport` pulled to `4a798be`.
- Live `php -l` passed for all five pages and the generator.
- Browser-style public URL checks returned HTTP `200` for all five report links.
- Sonat email sent: subject `Avignon live data reports`, task id `avignon-sonat-live-data-reports-2026-04-26`, Message-ID `<177724092474.60649.2649339175388744166@kovaldistillery.com>`.
- Robert approved the access-gate live pull. Live Salesreport then pulled to `0178b94` and live Contactreport pulled to `4d81ec2`.
- Live `php -l` passed for `avignon_report_access.php`, all five gated Salesreport pages, the generator, and all five Contactreport redirects.
- Browser-style unauthenticated checks for direct Salesreport links and old Contactreport links landed on `/login/index.php?referrer=salesreport` and did not expose report content.
- Sonat correction email sent: subject `Avignon live reports are now gated`, task id `avignon-sonat-gated-live-data-reports-2026-04-26`, Message-ID `<177724196570.93900.9938903576643379615@kovaldistillery.com>`.
- Robert approved the additional strategic/outreach report live pull. Live Salesreport then pulled to `409e791`; the pre-existing live `.htaccess` modification was preserved.
- Live `php -l` passed for both new generators and all four additional gated Salesreport pages.
- Additional report run findings at generation time: 25 win-back/inactive candidates, 25 whitespace/POD opportunity accounts, 20 slipping Illinois retail accounts, and 47 OPS Outreach events for 2026-04-26 through 2026-05-09, with 0 ready, 47 needing review, 11 open coverage, 15 missing Google links, 47 missing activity links, and 0 shift drops/swaps.
- Browser-style unauthenticated checks for all four additional Salesreport links landed on `/login/index.php?referrer=salesreport` and did not expose report content.
- Sonat additional-report email sent: subject `Avignon additional live reports and Outreach overview`, task id `avignon-sonat-additional-live-reports-outreach-2026-04-26`, Message-ID `<177724272423.22649.12105173729189084866@kovaldistillery.com>`.

## Rollback Plan

Revert `409e791`, `0178b94`, and `bc5bf07` in `salesreport`, and revert `4d81ec2` and `4a798be` in `contactreport`, push the revert commits, then fast-forward the live checkouts with `git pull --ff-only origin master`.

## Follow-Ups

- Keep the generator as the repeatable source for future Avignon live report refreshes.
- If Sonat wants distributor support reporting beyond market/category fallback, define the approved distributor-support source contract and required approval fields before adding commitments or allowance/pricing decisions.
