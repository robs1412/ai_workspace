# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-OPS-OUTREACH-LIVE-01
- Date Opened: 2026-03-02
- Date Completed: 2026-03-02
- Owner: Codex / OPS migration track
- Priority: High
- Status: Completed

## Scope
Restore visibility of latest Outreach Calendar changes on live OPS.

## Symptoms
Outreach calendar changes were not visible on live (`https://www.koval-distillery.com/ops`).

## Root Cause
Live code was current, but runtime Outreach feature/config variables were not set:
- `OPS_OUTREACH_ENABLED` missing in live `.env`.
- `GOOGLE_OUTREACH_CALENDAR_FEED_URL` missing in live `.env`.

This caused Outreach routes/navigation to be gated off and left feed-backed sync empty.

## Repo Logs

### ops

- Repo Log ID: OPS-2026-03-02-OUTREACH-LIVE-VISIBILITY
- Commit SHA: c3805f9fc1c7aa8fc86ddd022d6a3be1cccb7ae2
- Commit Date: 2026-03-02 08:58:53 -0600
- Change Summary: Verified live is on latest `main`; applied live env fix to set `OPS_OUTREACH_ENABLED=1`.

## Verification Notes
- Live git check: `HEAD=c3805f9`, `main...origin/main` (no lag).
- Live `.env` check before fix: no Outreach keys present.
- Applied on live: `OPS_OUTREACH_ENABLED=1` in `/home/koval/public_html/ops/.env` (backup created).
- Post-fix runtime check: `OPS_OUTREACH_ENABLED=1` resolved.
- Applied follow-up config from local secure file (`outreachcal.txt`) to set `GOOGLE_OUTREACH_CALENDAR_FEED_URL` in local + live `.env` (value redacted).
- Live verification after follow-up: `LIVE_FEED_SET=1`, `LIVE_FEED_LEN=149`.

## Rollback Plan
- Set `OPS_OUTREACH_ENABLED=0` (or remove it) in live `.env`.
- Restore prior `.env` from timestamped backup created during change.

## Follow-Ups
- If users still cannot access Outreach views, confirm page permissions for affected user/role in OPS Permissions.
