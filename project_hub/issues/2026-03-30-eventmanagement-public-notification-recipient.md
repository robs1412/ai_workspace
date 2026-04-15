# Incident / Project Slice Log
Last Updated: 2026-03-30 09:26:35 CEST (Machine: RobertMBP-2.local)

- Master Incident ID: `AI-INC-20260330-EVENTMGMT-NOTIFY-01`
- Date Opened: `2026-03-30 09:19:20 CEST`
- Date Completed: `2026-03-30 09:26:35 CEST`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Replace the dead `eventsupport@koval-distillery.com` address in the public event reservation mail flow with the active destination `mark@kovaldistillery.com`.

## Symptoms

- Public event reservation submissions generated a bounce for `eventsupport@koval-distillery.com`.
- The bounced message subject was `New Event Reservation Request #11`.
- The request acknowledgement and lifecycle email copy still referenced the dead support address.

## Root Cause

`eventmanagement/public_submit.php` sent new reservation notifications and request-receipt reply handling to `eventsupport@koval-distillery.com`, which no longer resolves to a valid mailbox.

`eventmanagement/action_handler.php` also embedded the same dead address in outbound event-support lifecycle email copy.

## Repo Logs

### eventmanagement

- Repo Log ID: `EVENTMGMT-20260330-NOTIFY-01`
- Commit SHA: `818fd8e`, `be06ba5`
- Commit Date: `2026-03-30`
- Change Summary:
  - added `eventmanagement_support_email()` in `config.php` with default `mark@kovaldistillery.com`
  - updated `public_submit.php` so new reservation notifications and request-receipt reply handling use the shared support email helper
  - updated `action_handler.php` so outbound event-support email copy references the active support email
  - updated `TODO.md` with a completed module note for the recipient fix
  - pushed `eventmanagement/main` to `origin` at `be06ba5`

## Verification Notes

- `php -l config.php`
- `php -l public_submit.php`
- `php -l action_handler.php`
- `rg -n "eventsupport@koval-distillery.com|mark@kovaldistillery.com" .`
- `git push origin main` succeeded and updated `origin/main` to `be06ba5`
- Live deployment completed on `2026-03-30 09:26:35 CEST`:
  - host: `ftp.koval-distillery.com`
  - path: `/home/koval/public_html/eventmanagement`
  - `git pull --ff-only origin main` fast-forwarded cleanly from `6ab5a7d` to `be06ba5`
  - live branch: `main`
  - live HEAD: `be06ba5511656af194f8c69f8224feb3b0a95a6a`
  - live worktree also contains pre-existing untracked backup files:
    - `public_request.php.prepull-20260329-110424`
    - `public_submit.php.bak`
    - `public_submit.php.prepull-20260329-110424`
- No end-to-end post-deploy browser submission was run in this turn because doing so would create a real event request and outbound email.

## Rollback Plan

- Revert commit `818fd8e` in `eventmanagement`.
- Restore the previous hardcoded support-email values in `public_submit.php` and `action_handler.php`.

## Follow-Ups

- If this address should be adjustable without code changes later, add `EVENTMANAGEMENT_SUPPORT_EMAIL` to the module `.env` on the relevant environments.
- When convenient, run one controlled live submission or mailbox-only verification to confirm the new notification reaches `mark@kovaldistillery.com` without bounce.
