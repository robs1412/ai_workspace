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

## Completion

- Portal commit `a3e8b1b7` deployed as backend/frontend image
  `v20260727reporting`; both containers are running and internal frontend/backend
  checks return HTTP 200.
- Order commit `558bf37` is live.
- DIST commit `84f6593` is live and remains an ancestor of live commit
  `7b7da76`.
- Salesreport commit `509ef7c` is live.
- Account `36990` readback:
  - Bill to: New York, New York, United States.
  - Ship to: Chicago, Illinois, United States.
  - Reporting: Chicago, Illinois, United States.
- The reporting-address view returns Chicago, Illinois, United States.
- Julie user `1307` has one exact reporting-location permission match for the
  account.
- Seven account audit rows record the canonical billing, shipping, and
  reporting corrections.
- Live DIST includes account `36990`, uses Illinois as delivery state, and the
  live self-service helper resolves Chicago as delivery city.
