# Eataly billing, shipping, reporting, and territory visibility

Date: 2026-07-27
Account: Portal 36990, Eataly Chicago LLC
Repos: `portal`, `order`, `dist`, `salesreport`

## Decision

Keep operational address meanings separate:

- Billing: New York, used on invoices.
- Shipping: Illinois, used for delivery eligibility and local tax.
- Reporting: Illinois, used for sales reporting and territory visibility.

Canonical US address writes use `United States` and full state names. Reads and
permission checks remain tolerant of legacy `US`, `USA`, and two-letter state
codes.

## Root cause

Julie had both New York and Illinois territory permission, but the account was
stored with country `USA` while territory data uses `United States`. Exact
country and state comparisons hid the account.

## Implementation

- Portal adds an explicit reporting location to account preferences and uses it
  as an alternate territory-visibility location.
- Portal normalizes future billing, shipping, and reporting writes.
- DIST uses shipping location for Illinois eligibility and local tax while
  displaying billing, shipping, and reporting locations separately.
- Self-service order checks use shipping state/city with billing fallback.
- Core Salesreport state reports use the reporting-address view, which falls
  back to billing location when no override is set.

## Eataly target values

- Billing: `New York`, `United States`
- Shipping: `Illinois`, `United States`
- Reporting: `Chicago`, `Illinois`, `United States`

## Verification

- PHP syntax checks across all changed backend/report files.
- Focused normalization and generated territory-SQL readback.
- Production database readback for exact account values, Julie visibility, and
  reporting view output.
- Live git readback for each deployed checkout.
