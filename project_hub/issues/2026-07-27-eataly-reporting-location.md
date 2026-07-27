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

## Portal login incident and repair

The first `v20260727reporting` frontend image was built without
`VUE_APP_API_URL`. Its compiled login client therefore posted to the relative
`/undefined/auth/login` path and displayed the generic unexpected-error modal.
The reporting-location backend was healthy; this was a frontend build-input
failure.

- Immediately restored the known-good `v20260714` frontend while keeping the
  reporting-location backend and Eataly data intact.
- Portal commit `17b16edb` now requires the production API URL in the build
  script, passes it explicitly into Docker, and fails the image build if the
  URL is absent from the compiled application bundle.
- Portal commit `417c7f2f` makes the compiled-bundle check compatible with the
  production image's BusyBox tools.
- Corrected frontend image `v20260727reportingfix3` was built, validated,
  transferred, and deployed. Build-history commit: `59a06735`.
- Live readback shows the corrected image running, its application bundle
  contains the configured Portal API URL, the undefined API expression is
  absent, and the reporting-location fields are present in compiled assets.
- The backend login endpoint on the production container route returns
  structured JSON for a bounded invalid-user probe instead of an application
  error.
- Final Eataly readback remained unchanged: New York billing; Chicago,
  Illinois shipping and reporting; `United States` in all three country fields.
