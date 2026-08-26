# BID Financial Refresh And Menu Performance

- Master Incident ID: `AI-INC-20260826-BID-FINANCE-MENU-PERF-01`
- Date Opened: 2026-08-26
- Date Completed: 2026-08-26
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Refresh BID's DB-backed financial readouts from live read-only QBO evidence, repair the Financial Planning snapshot mapping drift, deploy the payroll reconciliation fix for OPS task `378164`, and reduce repeated shared-menu loading overhead.

## Symptoms

- BID Current QBO A/P and A/R were timestamped 2026-08-25 instead of the current live pull.
- The Financial Planning shadow importer stopped because workbook row insertions shifted approved row mappings by one row.
- Every full page navigation requested `/bid/ajax_nav.php` again; the measured unauthenticated endpoint baseline was roughly 0.61 to 0.83 seconds per request.

## Root Cause

- QBO source data required a new read-only snapshot and guarded BID import.
- Workbook source rows moved while the importer retained the prior fixed row numbers.
- Server-side menu output was cached, but browser page changes discarded `window.bidNavPromise`, causing another authenticated HTTP request for the same menu.

## Repo Logs

### bid

- Repo Log ID: `AI-INC-20260826-BID-FINANCE-MENU-PERF-01-BID`
- Commit SHA: `98d914245155ae1baeeb9d87620125054ed47ee9`
- Commit Date: 2026-08-26
- Change Summary: Correct payroll leave, duplicate clock, and quarterly bonus reconciliation.

- Repo Log ID: `AI-INC-20260826-BID-FINANCE-MENU-PERF-01-BID-PERF`
- Commit SHA: `d887575b28ddfe5a44b9fdbb7844fbb5f2035245`
- Commit Date: 2026-08-26
- Change Summary: Correct current Financial Planning row mappings and cache the shared menu per authenticated browser session for five minutes.

## Verification Notes

- Live QBO snapshot: A/P 93 rows / $135,829.32; collectible A/R 77 rows / $218,468.48; source timestamp 2026-08-26 09:54:22 CDT.
- Guarded QBO import updated four BID surfaces and independently read back the new timestamp and counts.
- Financial Planning dry run passed with 569 entries, 20 reconciled upcoming-expense rows, 54 recurring rules, zero warnings, and zero adjusted ending-cash variance.
- Both live BID checkouts read back commit `d887575`; release-file SHA-256 hashes match local, and remote PHP lint passed.
- Navigation behavior test read one network fetch on the first page and zero on the second page within the cache window.

## Rollback Plan

- Revert BID commit `d887575` through a new git revert commit and fast-forward both checkouts.
- QBO snapshot persistence is audited and repeatable; restore the prior snapshot only through the guarded importer if source truth requires rollback.

## Follow-Ups

- Financial Planning shadow scenario `1` read back with 569 active entries, 54 active recurring rules, 20 tracked upcoming reviews, and 1,953 audit rows.
- Record the final OPS/Task Flow handoff with live URLs and verification proof.
