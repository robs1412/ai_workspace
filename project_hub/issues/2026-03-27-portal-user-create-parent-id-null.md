# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260327-PORTAL-USER-CREATE-01
- Date Opened: 2026-03-27
- Date Completed: 2026-03-27
- Owner: Codex
- Priority: High
- Status: Completed

## Scope

Create four production Portal user accounts for Store and Barback staffing without exposing passwords in chat.

## Symptoms

- Live Portal `user/create` failed during account provisioning.
- API create attempts did not insert partial rows but returned a database integrity error on `parent_id`.

## Root Cause

The production Portal `user/create` path is incompatible with the live `vtiger_users` schema because `parent_id` is `NOT NULL` and the controller payload path did not populate it. Direct DB inserts were required to complete the requested account creation safely.

## Repo Logs

### portal / koval-crm live production

- Repo Log ID: portal-live-2026-03-27-user-create
- Commit SHA: none
- Commit Date: n/a
- Change Summary:
  - Verified `auth/2fa/verify` behavior and confirmed repeated `/auth/login` calls invalidate older 2FA codes.
  - Confirmed `user/create` fails on live with `Column 'parent_id' cannot be null`.
  - Inserted users directly into `vtiger_users`, `vtiger_user2role`, `vtiger_users2group`, and `koval_additionaluser.salaries`.
  - Created users:
    - `1333` `gabrielethormann`
    - `1334` `angelasalinas-barback`
    - `1335` `sarahwelford-barback`
    - `1336` `nicholasyoungblood-barback`

## Verification Notes

- Verified each new username exists in live `vtiger_users`.
- Verified role links:
  - `gabrielethormann` -> `H11`
  - all three Barback users -> `H13`
- Verified group links:
  - `gabrielethormann` -> `124`
  - all three Barback users -> `172`
- Verified hourly rates:
  - `gabrielethormann` -> `23.00`
  - all three Barback users -> `24.00`
- Wrote a local restricted-permission markdown handoff with passwords under `ai_workspace/output/portal-account-passwords-2026-03-27.md`.

## Rollback Plan

- Delete user rows `1333` through `1336` from `vtiger_users`.
- Delete corresponding rows from `vtiger_user2role`, `vtiger_users2group`, and `koval_additionaluser.salaries`.
- Remove the local credential handoff file after distribution.

## Follow-Ups

- Patch the production Portal `user/create` flow so it always supplies a valid `parent_id`.
- Add an application-level regression check for live account creation against the current `vtiger_users` schema.
