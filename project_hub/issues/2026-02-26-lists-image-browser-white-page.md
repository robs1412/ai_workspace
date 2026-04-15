# Lists Image Browser White Page

- Master Incident ID: `AI-INC-20260226-LISTS-KCFINDER-01`
- Date Opened: `2026-02-26`
- Owner: `Codex`
- Priority: `P1`
- Status: `Resolved (Pending user confirmation in UI)`

## Scope

- Resolve blank/white page in `/lists/admin` image browser.
- Ensure KCFinder loads without fatal include-path errors on live.

## Reported Symptoms

- In `/lists/admin`, image browser opened as blank white page.
- Direct endpoint request returned `500` with empty body:
  - `/lists/admin/plugins/CKEditorPlugin/kcfinder/browse.php?...`

## Root Cause

- Multi-part KCFinder integration drift:
  - legacy relative include behavior in KCFinder bootstrap/autoload/session paths
  - shared-login helper path pointed to `/lists/login` instead of sibling `/login`
  - KCFinder bootstrap started a plain session before shared-login init in some flows
  - popup auth init only ran when `$_SESSION['KCFINDER']['disabled']` was truthy, but real authenticated sessions often had `KCFINDER` without a `disabled` key

## Repo Logs

### LISTS

- Repo Log ID: `LISTS-KCFINDER-20260226-SQUASH-01`
- Commit SHA: `b9e1171`
- Change Summary:
  - Squashed KCFinder stabilization chain:
    - include/bootstrap path hardening
    - integration fixes for phpList root/config bootstrap
    - CKEditor URL cleanup (`cms=phplist` removal)
    - shared-login hydration path and startup-order fixes

- Repo Log ID: `LISTS-KCFINDER-20260226-FINAL-01`
- Commit SHA: `9e30127`
- Change Summary:
  - Treat missing `$_SESSION['KCFINDER']['disabled']` as uninitialized and apply popup auth/session config.

## Deployment Notes

- Local `lists/main` pushed through `9e30127`.
- Live pull completed on:
  - `/home/koval/public_html/lists`

## Verification Notes

- Verified on live with authenticated cookie flow:
  - `/admin/` loads dashboard
  - KCFinder browse endpoint now returns full browser HTML (not permission-error JS, not white page/fatal)
- `cms=phplist` direct endpoint remains non-production and may still fail; production editor path is non-`cms`.
- Final in-browser click confirmation from user still pending.

## Next Check

- User retest in `/lists/admin` editor popup from normal UI flow.
- If any regressions remain, capture exact URL + timestamp and correlate with:
  - `/home/koval/public_html/lists/error_log`
  - `/home/koval/public_html/lists/admin/plugins/CKEditorPlugin/kcfinder/error_log`
