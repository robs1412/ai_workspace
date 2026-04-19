# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260418-SALESREPORT-MARKET-EVENTS-STATIC-HTML-CLEANUP-01`
- Date Opened: 2026-04-18
- Date Completed: 2026-04-18
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Remove the old ungated static Sonat market-events HTML snapshot from the live Salesreport web path while preserving the gated Market Events Report and gated Sonat PHP snapshot.

## Symptoms

Live Salesreport still had an untracked static file at `/home/koval/public_html/salesreport/sonat-market-events-report-2026-04-18.html` alongside the gated PHP snapshot.

## Root Cause

The gated PHP report and `.htaccess` rewrite had been deployed, but the previously generated static HTML snapshot remained physically present in the live document path as an untracked file.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-LIVE-STATIC-CLEANUP-20260418`
- Commit SHA: Not applicable; no repository change was needed for this cleanup.
- Commit Date: Not applicable.
- Change Summary: Moved only the live untracked static HTML snapshot out of the web path. Preserved `market_events_report.php`, `sonat-market-events-report-2026-04-18.php`, and `.htaccess`.

## Verification Notes

- Live file action: moved `/home/koval/public_html/salesreport/sonat-market-events-report-2026-04-18.html` to `/home/koval/salesreport_private_backups/2026-04-18-market-events-static-cleanup/sonat-market-events-report-2026-04-18.html`.
- Live preserved files verified after cleanup:
  - `/home/koval/public_html/salesreport/market_events_report.php`
  - `/home/koval/public_html/salesreport/sonat-market-events-report-2026-04-18.php`
- Live removed file verified after cleanup:
  - `/home/koval/public_html/salesreport/sonat-market-events-report-2026-04-18.html`
- Public verification for `https://koval-distillery.com/salesreport/sonat-market-events-report-2026-04-18.html`: `301 Moved Permanently` to `https://www.koval-distillery.com/406.shtml`, then `404 Not Found`; response body was the public Page Not Found page, not the report.
- Direct `https://www.koval-distillery.com/salesreport/sonat-market-events-report-2026-04-18.html` returned `404 Not Found`.

## Rollback Plan

If a rollback is explicitly approved, restore the backup file from `/home/koval/salesreport_private_backups/2026-04-18-market-events-static-cleanup/sonat-market-events-report-2026-04-18.html` to the live Salesreport directory. This should remain approval-gated because it would reintroduce a static report path.

## Follow-Ups

- None.
