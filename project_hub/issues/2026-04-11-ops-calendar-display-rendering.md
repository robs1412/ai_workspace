# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260411-OPS-CALENDAR-DISPLAY-01
- Date Opened: 2026-04-11
- Date Completed: 2026-04-11
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Investigate and fix the OPS calendar display regression at `/ops/index.php?view=calendar`.

## Symptoms

OPS Calendar month cells rendered event containers without visible default event text for standard calendar items.

## Root Cause

The FullCalendar `eventContent` hook returned `null` for non-Outreach items. In the v6 content hook, that suppresses the default event content. The page also referenced a stale FullCalendar CSS CDN URL that returned 404; the v6 global bundle injects its own CSS.

## Repo Logs

### ops

- Repo Log ID: OPS-CALENDAR-DISPLAY-20260411
- Commit SHA: 20b21fa1dcb7592f6b6dc34d4edfc7cb55cbddc6
- Commit Date: 2026-04-11
- Change Summary: Removed the dead FullCalendar CSS link and changed the non-Outreach `eventContent` return value to `true` so FullCalendar preserves default event rendering.

## Verification Notes

- Local: `php -l views/calendar_overview.php`
- Local: `build_calendar_payload()` JSON encode check passed.
- Local: authenticated calendar response included `Calendar Overview`, `id="calendar"`, no dead CSS link, and `return true;`.
- Local headless Chrome DOM dump showed `fc-event-title` and `fc-event-time` nodes after the fix.
- GitHub push: `main` updated from `2c86668` to `20b21fa`.
- Live pull: `/home/koval/public_html/ops` fast-forwarded to `20b21fa1dcb7592f6b6dc34d4edfc7cb55cbddc6`.
- Live: `php -l views/calendar_overview.php` passed.
- Live: deployed file has no `index.global.min.css` reference and includes the `return true;` default-rendering path.
- Live: `build_calendar_payload()` JSON encode check passed.
- Public unauthenticated URL checks were limited by site-level routing/security responses, so no secrets or credentials were used for browser login.

## Rollback Plan

Revert commit `20b21fa1dcb7592f6b6dc34d4edfc7cb55cbddc6` in `ops`, push `main`, then run `git pull --ff-only origin main` in `/home/koval/public_html/ops`.

## Follow-Ups

- If Robert still sees display issues after browser cache refresh, run an authenticated live browser check with approved test credentials.
