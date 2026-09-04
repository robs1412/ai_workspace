# Sales Assignment Attribution And Editor

- Master Incident ID: `AI-INC-20260904-SALES-ASSIGNMENT-ATTRIBUTION-EDITOR-01`
- Date Opened: 2026-09-04
- Date Completed: 2026-09-04
- Owner: Robert
- Priority: High
- Status: Completed and live

## Scope

Make current My Accounts assignments control the SATLA + DIST Sales by User report and add a one-pass mixed assignment editor to Sales Hitlist Admin.

## Symptoms

Sushi U.N.I remained credited to Robert in the August 5 through September 4 `entry_plus_activity` report after its active My Accounts assignment had been changed to Maria. The existing hitlist controls also required separate owner-by-owner batches for a mixed reassignment list.

## Root Cause

The report evaluated order `created_by` before active hitlist assignment and had no way to distinguish an explicitly unassigned account from an account with no assignment history. Sales Hitlist Admin supported same-owner bulk changes but not a single transaction containing different destination users and unassignments.

## Repo Logs

### salesreport

- Repo Log ID: `SALES-ASSIGNMENT-ATTRIBUTION-EDITOR-20260904`
- Commit SHA: `b06f4b44029789572e7752187eb70ea0c7699fa2`
- Commit Date: 2026-09-04
- Change Summary: Current hitlist assignment now overrides entry/activity attribution, the latest explicitly closed assignment reports as Unassigned, and assigned-account rows have editable owner selectors with one transactional Apply Changes action.

## Verification Notes

- Local and live PHP lint passed for `il_sales_by_user.php`, `il_sales_by_user_shared.php`, and `sales_hitlist_admindashboard.php`.
- Local and live `tests/il_sales_by_user_test.php` passed.
- The mixed-assignment handler completed a live-DB no-op POST/render test without changing the already-correct Sushi assignment.
- Rendered inline JavaScript parsed successfully.
- Both attribution modes returned 345 detail rows, 191 distinct sales references, and `$97,220.07` for August 5 through September 4, proving the precedence change did not alter report population or dollars.
- Live deployed readback attributes Sushi U.N.I only to Maria user `1351` with source `Current sales assignment`.
- Commit `b06f4b4` is pushed to `origin/master`; `/home/koval/public_html/salesreport` fast-forwarded cleanly to the same SHA.

## Rollback Plan

Revert Salesreport commit `b06f4b4`, push the revert, and fast-forward the live Salesreport checkout. Do not reset or overwrite unrelated local or live worktree changes.

## Follow-Ups

- Confirm the owner-facing authenticated report and assignment editor presentation during normal use.
