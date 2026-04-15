# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-PORTAL-SHIFT-VACATION-01
- Date Opened: 2026-03-02
- Date Completed:
- Owner: Codex / Robert
- Priority: High
- Status: Open (Push blocked by git auth)

## Scope
Fix weekly shift user digest so approved vacation does not present full-day shift rows, and partial vacation overlaps show adjusted shift hours in the email detail table.

## Symptoms
- Users received weekly shift digest entries for dates where they had approved vacation.
- Example complaint: March 4 appeared as a shift day in email even though vacation was planned.

## Root Cause
`WeeklyShiftUserReportService` always emitted shift rows when a shift existed, only tagging vacation as a label. It did not apply suppression/precedence rules for approved full-day vacation.

## Repo Logs

### koval-crm

- Repo Log ID: RLOG-20260302-01
- Commit SHA: 09492c4685f90fe9f8d2f8f10b87f1b38446f07d
- Commit Date: 2026-03-02 10:46:17 -0600
- Change Summary:
  - Suppress shift rows in `digest.weekly_shifts_user` when approved vacation fully covers the day.
  - For partial vacation, retain row and reduce scheduled hours with explicit partial-vacation note.
  - Separate vacation-class log hours from worked hours in digest aggregation.

## Verification Notes
- `php -l backend/app/Services/WeeklyShiftUserReportService.php` passed.
- Manual push not completed due local git auth failure (HTTPS username prompt unavailable; SSH key not authorized).

## Rollback Plan
- Revert commit `09492c4685f90fe9f8d2f8f10b87f1b38446f07d` in `koval-crm`.

## Follow-Ups
- Restore GitLab auth on this machine (HTTPS token helper or SSH key).
- Push `dev` branch to origin.
- Run `ops:weekly-shifts-user-report --dry-run` on portal backend to verify rendered entries.
