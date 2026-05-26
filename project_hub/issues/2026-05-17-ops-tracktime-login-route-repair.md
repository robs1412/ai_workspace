# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260517-OPS-TRACKTIME-LOGIN-ROUTE-01
- Date Opened: 2026-05-17
- Date Completed: 2026-05-17
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Repair the OPS hourly login landing behavior for the National Outreach TrackTime follow-up so affected non-exempt staff land on the TrackTime surface instead of the generic dashboard when the login handoff uses the default OPS route.

## Symptoms

- National Outreach follow-up task `368517` reported Christine/Abbie/Dylan login or clock-in link confusion.
- The OPS login router still treated hourly users as missing a daily check-in and defaulted generic `/ops/start.php` handoffs to the dashboard instead of the TrackTime page.

## Root Cause

- `ops/login_router.php` marked `checkin` as missing for all users, even though `non_exempt` users use TrackTime rather than daily check-ins.
- Generic login handoffs pointing at `/ops/start.php` were honored literally for hourly users instead of being normalized to their TrackTime landing.

## Repo Logs

### ops

- Repo Log ID: RL-20260517-01
- Commit SHA: `19b53ae`
- Commit Date: 2026-05-17
- Change Summary: Added hourly-aware OPS default landing logic in `login_router.php`, normalized generic `/ops/start.php` login referrers to `/ops/index.php?view=my_clocks` for `non_exempt` users, and stopped counting missing daily check-ins against hourly staff during first-login routing.

## Verification Notes

- `php -l login_router.php` passed.
- Localhost route check with a simulated authenticated hourly OPS session returned `reason=missing_clock` and target `/ops/index.php?view=my_clocks` for a first portal-style login.
- Localhost route check with the same hourly session and explicit generic referrer `/ops/start.php` returned `reason=referrer` and target `/ops/index.php?view=my_clocks`.
- Live user data readback confirmed Christine Cummins (`1309`), Abbie Brenner (`1320`), and Dylan Collins (`1319`) are active `non_exempt` OPS users with `koval_ops=1`; Abbie's May 2 TrackTime entry remains present as log `58179`.

## Rollback Plan

- Revert OPS commit `19b53ae`.
- Re-run the localhost login-router JSON checks for first-login and generic-referrer cases to confirm the previous behavior is restored.

## Follow-Ups

- Optional live OPS pull remains separate and approval-gated.
