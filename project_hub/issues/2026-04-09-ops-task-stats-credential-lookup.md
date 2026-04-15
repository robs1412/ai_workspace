# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260409-OPS-TASK-STATS-CREDS-01`
- Date Opened: `2026-04-09`
- Date Completed: `2026-04-09`
- Owner: `Codex`
- Priority: `High`
- Status: `Completed`

## Scope

Repair OPS Task Stats credential discovery after the recent credential safety move and verify Portal-backed statistics load again without exposing secrets.

## Symptoms

- `/ops/index.php?view=usage_stats` reported missing Portal/API credentials.
- The Task Stats feature depends on Portal API calls to `/users/weekly-statistics-period` and `/user/activity-tracking/grouped`.
- Direct credential names still existed in local OPS `.env`, so the regression pointed to path-dependent config discovery rather than removed secrets.

## Root Cause

`ops/config.php` only loaded environment variables from `__DIR__/.env`. After the credential safety move, runtime layouts that keep `.env` one directory above the served OPS tree no longer satisfied that assumption. In those layouts, `CRM_API_BASE_URL`, `CRM_API_USERNAME`, and `CRM_API_PASSWORD` stayed empty, so `crm_credentials_configured()` failed and Task Stats stopped before calling Portal.

## Repo Logs

### ops

- Repo Log ID: `OPS-2026-04-09-TASK-STATS-CREDS`
- Commit SHA: `ba20e9e`
- Commit Date: `2026-04-09`
- Change Summary:
  - Hardened `config.php` environment discovery to load `.env` from both the OPS repo root and a parent safety path, while preserving already-set process env vars.
  - Verified real Task Stats Portal fetches return rows again.
  - Added a synthetic regression check proving a parent-only `.env` layout now resolves the Portal credential constants.

## Verification Notes

- `php -l config.php`
- `php -r 'require "bootstrap.php"; ... ops_fetch_portal_weekly_statistics(...); ops_fetch_portal_activity_grouped(...);'`
  - Result: weekly stats returned `59` rows, grouped activity returned `28` rows, both with `null` errors.
- Synthetic parent-`.env` harness:
  - Temp layout with `ops/config.php`, stubbed `login/` includes, and credentials only in parent `.env`.
  - Result: `CRM_API_BASE_URL`, `CRM_API_USERNAME`, and `CRM_API_PASSWORD` all resolved successfully.

## Rollback Plan

- Revert commit `ba20e9e` in `ops` if the broader env lookup causes an unexpected regression.
- Restore the previous single-path loader in `config.php`.
- Re-verify Task Stats and other Portal-backed OPS features after rollback.

## Follow-Ups

- If any live runtime still serves OPS from a bridged path, confirm the deployed directory now has either a local `.env` or an approved parent `.env`.
- Consider extracting the OPS env loader into a shared helper so login/ops use one consistent discovery strategy.
