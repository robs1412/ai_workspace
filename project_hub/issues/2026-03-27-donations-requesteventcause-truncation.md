# Incident / Project Slice Log
Last Updated: 2026-03-27 10:14:15 CET (Machine: RobertMBP-2.local)

- Master Incident ID: `AI-INC-20260327-DONATIONS-EVENTCAUSE-01`
- Date Opened: `2026-03-27 09:10:00 CET`
- Date Completed: `2026-03-27 10:14:15 CET`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Prevent donation approval/edit actions from failing when `requesteventcause` exceeds the current database column width.

## Symptoms

- Donations review screen showed SQLSTATE 22001 / MySQL 1406.
- Error text indicated `Data too long for column 'requesteventcause' at row 1`.
- Failure occurred while moving a request into the approved table and could also affect later edits to approved records.

## Root Cause

`donations/action_handler.php` inserted and updated `requesteventcause` without constraining it to the destination column width in `donationrequests_approved`.

The current UI also allowed longer values than that approved-table column can store.

## Repo Logs

### donations

- Repo Log ID: `DON-20260327-EVENTCAUSE-01`
- Commit SHA: `19fcf9a`
- Commit Date: `2026-03-27`
- Change Summary:
  - added shared helpers to resolve a column max length from `INFORMATION_SCHEMA` with a legacy-safe fallback of `100`
  - trimmed `requesteventcause` before approve/save writes so strict SQL mode cannot throw MySQL 1406
  - appended a success-note when truncation occurs
  - applied `maxlength` to the request detail form input using the same resolved limit
  - committed locally and pushed to `origin/master`
  - attached live `/home/koval/public_html/donations` to git with a timestamped backup and repo-specific deploy key
  - fast-forwarded live `donations` to `19fcf9a`

## Verification Notes

- `php -l config.php`
- `php -l action_handler.php`
- `php -l request_details.php`
- `php -l views/request_detail_view.php`
- `git push origin master` succeeded with `19fcf9a`
- Live SSH reachability and key auth were verified from this machine.
- Live backup created:
  - `/home/koval/public_html/donations.pre-git-20260327-100659`
- Live git deploy setup completed:
  - initialized `/home/koval/public_html/donations/.git`
  - set remote to `git@github.com-donations:robs1412/donations.git`
  - created live deploy key `donations-live-deploy-key`
  - added the deploy key to GitHub repo `robs1412/donations`
- Live deploy verification:
  - `cd /home/koval/public_html/donations && git pull --ff-only origin master`
  - result: `Already up to date.`
  - live HEAD: `19fcf9a`
- Shell-side live metadata verification against the configured donations DB host timed out from this environment, so runtime confirmation against the actual host remains to be done in-browser or from an environment with DB reachability.

## Rollback Plan

- Revert the helper additions in `donations/config.php`.
- Revert the pre-write normalization in `donations/action_handler.php`.
- Revert the `maxlength` wiring in `donations/request_details.php` and `donations/views/request_detail_view.php`.

## Follow-Ups

- Verify the exact `requesteventcause` width in the live donations schema and align the fallback value if the column differs from the legacy `100` character limit.
- If preserving full text is important, consider widening `donationrequests_approved.requesteventcause` rather than truncating on write.
