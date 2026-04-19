# Salesreport Market Events Live Deploy

- Master Incident ID: `AI-INC-20260418-SALESREPORT-MARKET-EVENTS-LIVE-DEPLOY-01`
- Date Opened: 2026-04-18
- Date Completed: 2026-04-18
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Deploy already-pushed Salesreport commit `fe268bc4126537432302452e2a41541d077d93b1` to the standard live Salesreport path so the Market Events Report is visible from the live menu, then verify live access-control behavior without exposing credentials, cookies, 2FA codes, session tokens, or private report data.

## Symptoms

Robert reported that the pushed Salesreport change was not yet visible on the live Salesreport menu and clarified that Salesreport uses the standard live `git pull` flow. For this class of already-verified safe Salesreport change, Robert approved automatic live pull going forward after the pushed change is verified and safe.

## Root Cause

The local repository and `origin/master` were already at `fe268bc`, but the live Salesreport worktree was still at `26006edd69a604cf2ab1cb85a1f11e7b4c007c8f`.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-20260418-MARKET-EVENTS-LIVE-DEPLOY-01`
- Commit SHA: `fe268bc4126537432302452e2a41541d077d93b1`
- Commit Date: 2026-04-18
- Change Summary:
  - Added protected `market_events_report.php`.
  - Added `Market Events Report` under `Advanced Sales Reports` in `_menu.php`.
  - Added gated `sonat-market-events-report-2026-04-18.php`.
  - Added `.htaccess` rewrite for the old `.html` Sonat URL.

## Deployment Notes

- Local repo path: `/Users/werkstatt/salesreport`
- Live SSH host/user: `koval@ftp.koval-distillery.com`
- Live path: `/home/koval/public_html/salesreport`
- Branch: `master`
- Pre-deploy live HEAD: `26006edd69a604cf2ab1cb85a1f11e7b4c007c8f`
- Fast-forward target: `fe268bc4126537432302452e2a41541d077d93b1`
- Deploy command: `cd /home/koval/public_html/salesreport && git pull --ff-only origin master`
- Post-deploy live HEAD: `fe268bc4126537432302452e2a41541d077d93b1`
- Live worktree note: existing untracked `sonat-market-events-report-2026-04-18.html` was preserved. The deployed `.htaccess` rewrite routes requests for that old URL to the gated PHP page.

## Verification Notes

- Local pushed state verified: `origin/master` resolves to `fe268bc4126537432302452e2a41541d077d93b1`.
- Local syntax checks passed:
  - `php -l market_events_report.php`
  - `php -l sonat-market-events-report-2026-04-18.php`
- Live syntax checks passed for the same two files after pull.
- Live file/menu checks:
  - `market_events_report.php` exists in `/home/koval/public_html/salesreport`.
  - `_menu.php` contains `Market Events Report` under `Advanced Sales Reports`.
  - `.htaccess` contains the rewrite for `sonat-market-events-report-2026-04-18.html`.
- Public unauthenticated checks on canonical URL `https://koval-distillery.com`:
  - `GET /salesreport/market_events_report.php` returns `302` to `../login/index.php?referrer=salesreport`.
  - `GET /salesreport/sonat-market-events-report-2026-04-18.html` returns `302` to `../login/index.php?referrer=salesreport`; it no longer serves the static report body unauthenticated.
  - `GET /salesreport/sonat-market-events-report-2026-04-18.php` returns `302` to `../login/index.php?referrer=salesreport`.
- Authenticated-render feasibility:
  - Full non-interactive credential login was attempted using local automation credentials without printing secrets. It did not reach 2FA or generate a fresh code; it redirected back to the login form.
  - A live PHP render check with a simulated authenticated Salesreport session confirmed `market_events_report.php` renders and contains `Market Events Report` plus user switcher controls.
  - A live menu render check confirmed the generated menu includes `Advanced Sales Reports` and `Market Events Report`.

## Rollback Plan

Use the standard live git rollback path if needed:

1. `ssh koval@ftp.koval-distillery.com`
2. `cd /home/koval/public_html/salesreport`
3. Review current state with `git status --short --branch`.
4. Revert the deployed commit with a normal revert commit or fast-forward to a vetted rollback branch; do not use destructive reset on live while untracked/local files exist.

## Follow-Ups

- Investigate why the Codex automation login POST redirected back to Login instead of reaching 2FA, if full browser-authenticated menu checks are required in a future slice.
- Preserve Robert's clarified Salesreport live behavior in durable workflow notes: Salesreport is a live-pull module, and already-pushed safe/verified Salesreport changes should be pulled live automatically for this class of visibility task.
