# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-OPS-OUTREACH-CONNECTEAM-01`
- Date Opened: `2026-04-09`
- Date Completed: `2026-04-09`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Verify that imported Connecteam outreach events and linked shifts are visible in OPS locally first, then commit/push the OPS changes and pull the same revision to live OPS.

## Symptoms

- Staged Connecteam imports were already present in OPS outreach data, but outreach-calendar testing needed confirmation that the records were actually visible in the OPS UI.
- Localhost outreach list showed imported events, while the outreach calendar payload returned zero events.

## Root Cause

`build_outreach_calendar_payload()` was incorrectly calling `build_calendar_payload(true)`, which limits the source dataset to market-category events. Outreach filtering then ran against an empty/non-outreach base set, leaving the outreach calendar empty even though outreach events and linked shifts existed.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-04-09-CONNECTEAM-OUTREACH-VISIBILITY`
- Commit SHA: `89b20668dfa13de7c2f4540aebce92051792209c`
- Commit Date: `2026-04-09`
- Change Summary:
  - Added `scripts/connecteam_staging_parity.php` to normalize staged Connecteam exports, report parity against OPS outreach events plus linked shifts, and generate bridge/apply artifacts.
  - Fixed outreach calendar visibility by changing `build_outreach_calendar_payload()` to start from the non-market calendar payload before outreach-only filtering.
  - Updated `TODO.md` with the completed parity/visibility verification notes.

## Verification Notes

- Local parity script on localhost reported:
  - `Normalized Connecteam rows: 151`
  - `Matched event + linked shift: 151`
  - `Missing OPS Outreach event: 0`
  - `Matched event but missing linked shift: 0`
- Localhost outreach list HTML was fetched through an authenticated session and confirmed imported event names including:
  - `Child Link’s Annual Whiskey Tasting Fundraiser`
  - `Mariano's - Clybourn (New City)(534)`
  - `Binny's Grand (Downtown)`
  - `Binny's Logan Square`
  - `Binny's Naperville`
- Localhost outreach calendar AJAX payload after the fix returned `151` events and included imported titles such as:
  - `Let's Talk Womxn Event`
  - `Uncork It`
  - `Binny's Evanston`
  - `Binny's Marcey St`
- Localhost outreach calendar page HTML included the fixed `initialPayload` with imported outreach event titles and linked shift objects such as `shift_4928` for `Outreach: Binny's Joliet`.
- Push result: `origin/main` updated from `17b47b8` to `89b2066`.
- Live pull result:
  - host: `koval@ftp.koval-distillery.com`
  - path: `/home/koval/public_html/ops`
  - pull: fast-forward from `1486bc6` to `89b2066`
- Live browser note:
  - Chrome on this machine reached `https://www.koval-distillery.com/ops/index.php?view=outreach_calendar` and `...view=outreach_list`, but the active live session redirected to `view=list`.
  - This confirms a live browser/session routing or permission limitation for the current session, not a failed deploy. The deployed live checkout is on the target commit.

## Rollback Plan

- Revert commit `89b20668dfa13de7c2f4540aebce92051792209c` in `ops`.
- On live OPS: `cd /home/koval/public_html/ops && git pull --ff-only origin main` after the revert is pushed.

## Follow-Ups

- Verify live outreach-route visibility in-browser with a user/session that is expected to have Outreach access, since the current Chrome live session redirected to `view=list`.
- If broader import iterations continue, use the new parity script as the pre-deploy visibility check before each outreach testing wave.
