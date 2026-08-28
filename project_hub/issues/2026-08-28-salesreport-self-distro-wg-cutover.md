# Salesreport Self-Distro WG Cutover

- Master Incident ID: `AI-INC-20260828-SALESREPORT-SELF-DISTRO-WG-CUTOVER-01`
- Date Opened: 2026-08-28
- Date Completed: 2026-08-28
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Correct the Current Direct WG totals embedded by `/order/onboarding-limit-planner.php?scope=dist` so a requested 2026 start date before July 1 does not add historical pre-direct activity.

## Symptoms

For the same August 28 end date, the Current Direct view returned different WG totals when the requested start date was January 1 versus July 1, even though the working self-distribution period began July 1, 2026.

## Root Cause

The custom and Year-to-date controls could move the Current Direct query before the July 1 warehouse cutover. The report then merged January-June CRM distributor history and pre-cutover store/tasting transfers into the working WG total.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-20260828-SELF-DISTRO-WG-CUTOVER-01`
- Commit SHA: `028e0b446eb615db035a615552cc4ad8b6f49ce3`
- Commit Date: 2026-08-28
- Change Summary: Clamp Current Direct and 2026 Jul-Dec date ranges to July 1, 2026; preserve the Jan-Jun historical reference tab; add a visible clamp notice and regression coverage.

## Verification Notes

- Local and live PHP lint passed for the report and helper.
- The focused helper regression test passed locally and live.
- Live checkout fast-forwarded to `028e0b446eb615db035a615552cc4ad8b6f49ce3`.
- Live DB-backed renders through August 28 now match for January 1 and July 1 requested starts: combined WG `939.89000`, store+tasting WG `449.09000`, and self-distro WG `490.80000`.

## Rollback Plan

Revert Salesreport commit `028e0b4` and fast-forward the live Salesreport checkout to the resulting commit.

## Follow-Ups

None.
