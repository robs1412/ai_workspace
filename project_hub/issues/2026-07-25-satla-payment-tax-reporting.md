# SATLA Payment And Local Tax Reporting

- Master Incident ID: `AI-INC-20260725-SATLA-PAYMENT-TAX-REPORTING-01`
- Date Opened: 2026-07-25
- Date Completed: 2026-07-25
- Owner: Robert
- Priority: Normal
- Status: Completed

## Scope

Add payment-method sorting/filtering and invoice-date filtering to SATLA Invoice Payments. Extend the existing Cook County reporting page with exact DIST and SATLA gallonage-tax rows, and add the equivalent Chicago reporting page.

## Symptoms

SATLA Invoice Payments did not show how each account intended to pay and could not be filtered by invoice date. Cook County reporting did not expose current DIST and SATLA tax sources together, and no matching Chicago page existed.

## Root Cause

The payment list did not join account onboarding payment methods. Local gallonage tax existed in lane-specific invoice/order data but had no shared Salesreport read model.

## Repo Logs

### order

- Repo Log ID: `ORDER-SATLA-PAYMENT-FILTERS-20260725`
- Commit SHA: `563d2e2`
- Commit Date: 2026-07-25
- Change Summary: Joined account onboarding payment method into SATLA invoice rows; added sortable Paying By, method filter, and invoice from/to filters.

### salesreport

- Repo Log ID: `SALESREPORT-LOCAL-TAX-LANES-20260725`
- Commit SHA: `136d0cb`
- Commit Date: 2026-07-25
- Change Summary: Preserved WH Cook schedules, added exact DIST and SATLA Cook tax tables, added the matching Chicago report, and linked both from Monthly Reporting.

## Verification Notes

- Live Order fast-forwarded to `563d2e2`; live Salesreport fast-forwarded to `136d0cb`.
- PHP lint passed for all six touched PHP files.
- Live SATLA payments readback: 104 invoices; payment methods 17 Fintech, 3 check, 2 ACH push, 82 not set.
- July 1-25 tax readback: DIST Cook 178.228600 gallons / $389.62; SATLA Cook 163.416815 gallons / $382.98; DIST Chicago 115.770600 gallons / $299.84; SATLA Chicago 15.454063 gallons / $41.41.
- Public unauthenticated route probes returned the expected auth-gated 406 response; deployed source readback confirmed the new controls and report headings.

## Rollback Plan

Revert the two scoped commits and fast-forward the corresponding live checkouts.

## Follow-Ups

- None.
