# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-OPS-OUTREACH-LIVE-GATING-01`
- Date Opened: `2026-04-09`
- Date Completed: `2026-04-09`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Resolve the remaining OPS production issue where live admin navigation did not show Outreach after login, while localhost still showed a contradictory `Distill America` status row in `market_calendar_sync`.

## Symptoms

- Live OPS admin menu hid `Outreach` links after login.
- Localhost `market_calendar_sync` showed two `Distill America` rows: one matched booking and one stale `Not in OPS` row.

## Root Cause

- Live OPS was still using hard feature-flag checks in `header.php` and `index.php`:
  `getenv('OPS_OUTREACH_ENABLED') === '1'`.
- The live checkout at `/home/koval/public_html/ops` had no `OPS_OUTREACH_ENABLED` entry in `.env`, so Outreach navigation and routes were treated as disabled on live even for admins.
- `market_calendar_sync` compared every Google feed row without suppressing stale legacy UIDs once a booking already had a current linked UID in `event_booking_google_links`.
- For `Distill America`, the market feed contained both the current linked UID `ops-market-305-1774007652@koval-distillery.com` and a stale legacy UID `ops-market-305@koval-distillery.com`, producing a contradictory extra `missing_ops` row.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-04-09-OUTREACH-GATING-SYNC-DEDUPE`
- Commit SHA: `5212588`
- Commit Date: `2026-04-09`
- Change Summary:
  - Added `ops_outreach_enabled()` in `bootstrap.php` to default Outreach to enabled unless explicitly disabled with `0/false/off/no`.
  - Switched `header.php` and `index.php` to use the shared helper.
  - Updated `market_calendar_sync` comparison logic in `index.php` to drop stale Google rows when the UID maps to an OPS booking that already has a different current linked UID for the same calendar type.
  - Updated OPS `TODO.md` completion log for the fix.

## Verification Notes

- Local lint:
  - `php -l bootstrap.php`
  - `php -l header.php`
  - `php -l index.php`
- Local admin render check:
  - simulated admin render of `header.php` returned `local_outreach_menu=present`
- Local sync data check:
  - simulated `market_calendar_sync` render for `2026-05-01..2026-06-05` returned only one `Distill America` row:
    - `{"status":"match","ops_id":305,"google_uid":"ops-market-305-1774007652@koval-distillery.com"}`
    - `distill_rows=1`
- GitHub push:
  - `origin/main` advanced from `6f4bbc8` to `5212588`
- Live deploy:
  - pulled `/home/koval/public_html/ops` with `git pull --ff-only origin main`
  - live checkout advanced to `5212588`
- Live admin render check:
  - simulated admin render of `header.php` returned `live_outreach_menu=present`
- Live sync data check:
  - simulated live `market_calendar_sync` render for `2026-05-01..2026-06-05` returned:
    - `{"status":"match","ops_id":305,"google_uid":"ops-market-305-1774007652@koval-distillery.com"}`
    - `distill_rows=1`

## Rollback Plan

- On live: `cd /home/koval/public_html/ops && git checkout 6f4bbc8`
- Restore previous behavior by reverting commit `5212588` locally and re-pushing if a full rollback is needed.
- If Outreach must be hidden again without code rollback, set `OPS_OUTREACH_ENABLED=0`.

## Follow-Ups

- Replace remaining manual/browser-only OPS QA dependencies with a working Chromium automation runtime on this workstation.
- Consider removing the now-legacy Outreach env gate entirely once rollout is confirmed stable across environments.
