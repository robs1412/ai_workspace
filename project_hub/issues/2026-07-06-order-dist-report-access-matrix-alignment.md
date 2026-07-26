# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260706-ORDER-DIST-REPORT-ACCESS-MATRIX-01`
- Date Opened: 2026-07-06
- Date Completed: 2026-07-06
- Owner: Robert
- Priority: urgent access repair
- Status: completed

## Scope

Align active `/order` and `/dist` user access with the Salesreport and Contactreport access matrix enforcement added on 2026-07-05.

## Symptoms

Kevin McCarthy and other Order/DIST users could authenticate to Order/DIST but were blocked from Salesreport or Contactreport after the report headers began enforcing `koval_additionaluser.accessmatrix.matrix_salesreport` and `matrix_contactreport`.

## Root Cause

Order/DIST access is controlled by `koval_crm.distribution_user_groups` plus the admin ID fallback, while Salesreport and Contactreport now check `koval_additionaluser.accessmatrix`. Several active Order/DIST users had blank or zero report matrix flags.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-ACCESS-MATRIX-20260705`
- Commit SHA: `7924bede25c162134b85692272971b219807bdbc`
- Commit Date: 2026-07-05
- Change Summary: Salesreport header now requires `../login/access_salesreport.php`.

### contactreport

- Repo Log ID: `CONTACTREPORT-ACCESS-MATRIX-20260705`
- Commit SHA: `93f49f7e2334b3242c21ae58048d388c9e75d1ef`
- Commit Date: 2026-07-05
- Change Summary: Contactreport header now includes `../login/access_contactreport.php`.

### database

- Repo Log ID: `ACCESSMATRIX-ORDER-DIST-ALIGN-20260706`
- Commit SHA: not applicable; DB-only access matrix update.
- Commit Date: not applicable
- Change Summary: Updated `koval_additionaluser.accessmatrix` for active Order/DIST users, setting `matrix_salesreport = '1'` and `matrix_contactreport = '1'` where either flag was not already `1`.

## Verification Notes

- Pre-update readback: active Order/DIST users `26`; missing Salesreport flag `14`; missing Contactreport flag `18`; missing matrix rows `0`.
- Kevin McCarthy readback before update: user id `1328`, username `kevinmccarthy`, group `sales_person`, Salesreport blank, Contactreport blank.
- Update affected `18` accessmatrix rows.
- Post-update readback: active Order/DIST users `26`; missing Salesreport flag `0`; missing Contactreport flag `0`; missing matrix rows `0`.
- Kevin McCarthy readback after update: user id `1328`, username `kevinmccarthy`, group `sales_person`, Salesreport `1`, Contactreport `1`.

## Rollback Plan

If owner decides Order/DIST users should not have report access, restore the prior non-`1` values for the affected users from database backup or explicitly set report flags back to the owner-approved values for the Order/DIST user set.

## Follow-Ups

- Consider adding a small admin readback report that shows Order/DIST group membership next to report matrix flags so future access drift is visible before enforcement changes.
