# Dist / Order / Portal Project Plan - 2026-06-22

This document is the project plan for the Portal, /dist, and /order account compliance and ordering updates. Each section records Robert's input, what has been done, and what is still missing.

Published Google Doc: https://docs.google.com/document/d/166Y33XaRuV5EsSUQZqN224i9Gg7BeiSPO33epOYTWiM/edit?usp=drivesdk

## 2026-06-22 Status Checklist

- [x] DONE - Robert's latest task-mode input was recorded in DB-backed AI Manager input storage: input_id 3386, input_uuid ai-manager-chat-20260622143530-4785a1dd68c4.
- [x] DONE - Portal contact classifications include Marketing Contact and Event / Tasting Coordinator.
- [x] DONE - Portal contacts now have Preferred Communication Mode with options phone, text, and E-mail.
- [x] DONE - Portal accounts now have Preferred Ordering Mode with options portal, in-person, and phone.
- [x] DONE - Portal accounts now have account-level delivery time notes and delivery notes.
- [x] DONE - Portal accounts now have account-level pricing override fields: manual override, percent change, override value, and override notes.
- [x] DONE - Portal account form now has an account Pricing tab for every account; distributor accounts retain the distributor product price-list grid in that tab.
- [x] DONE - /dist account list and order screen now show preferred ordering mode, delivery notes, and pricing override notes.
- [x] DONE - /dist order preview can default from standard product case price and apply manual or percent account pricing overrides.
- [x] DONE - /order account list and selected-account order panel now show preferred ordering mode, delivery notes, and pricing override notes.
- [x] DONE - /order order-entry suggested prices now start from the pricing table tiers and apply manual or percent account pricing overrides.
- [x] DONE - /order has a Do Not Sell matched accounts page for the latest ILCC scan/match result.
- [x] DONE - ILCC scraper exports delinquency and cured CSV lists and records run dates in the planned run table.
- [x] DONE - Do Not Sell warning fields were added to Portal account payloads and /order account/order payloads.
- [x] DONE - Summary email design includes HTML tables for "added to do not sell" and "can now be sold to again".
- [x] DONE - Portal migrations were applied through the live OPS DB host and verified by `information_schema` readback.
- [x] DONE - First official ILCC write scan was run from the DB-allowed SSH host with email disabled; live run row `1` was verified.
- [x] DONE - Live /dist was pulled to commit `5d0bb42`.
- [x] DONE - Live /order was pulled to commit `f27b63b`.
- [x] DONE - /order now has a My Accounts section on `order.php` based on the current user's active sales hitlist and Portal-equivalent sales assignment fields.
- [x] DONE - /dist now has a Delivery Schedule page backed by `koval_crm.account_delivery_schedules`, with preferred day/window, allowed days/window, route zone, route stop order, driver notes, and source notes per self-distribution account.
- [x] DONE - /dist delivery availability now uses queryable individual time-frame rows in `koval_crm.account_delivery_schedule_windows`: account, window type, day number/name, start time, end time, and notes.
- [x] DONE - /dist self-distribution account views now check `koval_crm.account_do_not_sell` and show do-not-sell status/warnings for self-distribution accounts.
- [x] DONE - /order now has a top navigation link to `My Accounts`.
- [x] DONE - /dist now has account-level fulfillment timestamping with BOL, invoice, and delivered-items image uploads.
- [x] DONE - Portal backend container has `ilcc:do-not-sell-scan` registered.
- [x] DONE - Live daily scanner is installed as host cron at `30 7 * * *` using `/home/koval/ilcc-delinquency-cure/run_portal_ilcc_do_not_sell_scan.sh`.
- [x] DONE - Live daily scanner path was verified by run `2`; production notification path sent.
- [x] DONE - Completion email was sent to Robert, Sonat, Mark, and Sebastian: Message-ID `<178214680890.93153.2044048039276729454@kovaldistillery.com>`.
- [ ] TODO - Browser-check live /portal after confirming the correct Portal frontend deployment route.
- [x] DONE - Robert decided do-not-sell order behavior: show warning, allow override with required reason.
- [x] DONE - /order live now requires an override reason before saving an order for an active IL do-not-sell account.
- [x] DONE - /order Do Not Sell review page now labels weak `name_city` rows as `Needs review / Weak match, not blocked` instead of `Do not sell`.
- [x] DONE - /order Do Not Sell default view now shows only active/cured matches; weak review-only `name_city` rows are separated behind the `Review Only` filter.
- [x] DONE - /order Do Not Sell review table now shows the latest KOVAL invoice date and amount from KOVAL CRM invoices.
- [x] DONE - /order Do Not Sell review table now has a frozen header, sortable columns, and name search across Portal account and ILCC business names.
- [x] DONE - Live Portal Docker backend/frontend were deployed as `v20260622ordering` with account do-not-sell/order preference backend fields, an Overview do-not-sell warning note, and a dedicated account Ordering tab.
- [x] DONE - /order accounts page shows latest KOVAL CRM invoice amount.
- [x] DONE - /dist accounts page shows latest WH invoice amount.

## 1. Contact Classifications

Robert's input:
- In /portal contact classification add Marketing Contact.
- Add Event / Tasting Coordinator.

What was done:
- [x] DONE - Added Marketing Contact to the Portal contact classification defaults.
- [x] DONE - Added Event / Tasting Coordinator to the Portal contact classification defaults.
- [x] DONE - Added both values to the migration seed path so they can be created consistently.

Still missing:
- [x] DONE - Run the migration/seed on the live Portal DB.
- [ ] TODO - Verify both classifications in the live Portal contact picker.

## 2. Do Not Sell / Illinois Delinquency and Cure Lists

Robert's input:
- Scan the Illinois do-not-sell / delinquency list daily so accounts can be marked accordingly.
- Export the CSV delinquency and cured lists.
- Add dates when this was last done.
- Add a do-not-sell tag / notice field on the account.
- Reason A: license expired, calculated from license expiry.
- Reason B: on the IL list, updated from the daily Codex run.
- Both reasons should trigger a Do Not Sell warning on the account.
- Warning must display in Portal, /dist, and /order.
- Use the same field in /dist and /order to show and mark the account in red.
- Send email reminders when a customer is added to the delinquency list or put on the cured list.
- Automate via Codex daily.
- Source: https://ilccportal.illinois.gov/s/delinquency-cure-list

What was done:
- [x] DONE - Built a Playwright scraper that opens the ILCC public Delinquency/Cure List page and uses the site's own Export to CSV buttons.
- [x] DONE - Verified the scraper on 2026-06-22:
  - 2,130 delinquency rows exported.
  - 430 cured rows exported.
- [x] DONE - Added Portal storage design for:
  - account_do_not_sell
  - ilcc_delinquency_cure_runs
  - ilcc_delinquency_cure_entries
- [x] DONE - Added dated CSV export paths and run metadata fields.
- [x] DONE - Added Portal account warning fields:
  - License Expired
  - License Expiration Date
  - On IL Do Not Sell List
  - IL Do Not Sell Status
  - Do Not Sell Notice
  - IL Do Not Sell Checked At
  - Do Not Sell
  - Do Not Sell Warning
- [x] DONE - Added account form display for the Do Not Sell warning.
- [x] DONE - Added /order order list fields for Do Not Sell and Do Not Sell Warning.
- [x] DONE - Added account selector warning display for /order and /dist account searches.
- [x] DONE - Added summary email body with HTML tables:
  - Added to do not sell
  - Can now be sold to again
- [x] DONE - Added daily Portal job definition for 7:30 AM Central.
- [x] DONE - Re-checked the database connection through /ops using the OPS bootstrap / crm integration path.

Official live run from 2026-06-22 DB-host readback:
- Run id: 1.
- ILCC delinquency rows checked: 2,122.
- ILCC cured rows checked: 438.
- Illinois Portal accounts checked: 5,813.
- Conservative address-backed delinquency matches written as active do-not-sell: 135 accounts.
- Delinquency matches recorded for review only: 176 accounts.
- Conservative address-backed cured matches recorded: 49 accounts.
- Cured matches recorded for review only: 18 accounts.
- Active IL do-not-sell accounts after same-run overlap correction: 135.
- Cured account_do_not_sell records after same-run overlap correction: 39.
- Email sent: no; first run was intentionally no-email pending recipient/notification approval.

Second live run from the installed daily scanner path:
- Run id: 2.
- ILCC delinquency rows checked: 2,122.
- ILCC cured rows checked: 438.
- Matched delinquency accounts: 311.
- Matched cured accounts: 67.
- Review-only delinquency matches: 176.
- Review-only cured matches: 18.
- Newly blocked accounts: 0.
- Newly cured accounts: 10.
- Active IL do-not-sell accounts: 135.
- Email sent: yes.

Still missing:
- [x] DONE - Apply the Portal DB migration live. Live readback now confirms:
  - account_do_not_sell: present
  - ilcc_delinquency_cure_runs: present
  - ilcc_delinquency_cure_entries: present
  - account_preferences: present
  - contact_preferences: present
  - ilcc:do-not-sell-scan job: present/enabled
- [x] DONE - Run the live command from a DB-allowed Portal/OPS host so it can write the first official run row.
- [x] DONE - Pull /dist and /order live.
- [x] DONE - Install and verify host-cron daily scanner using the browserless ILCC Aura endpoint fetch.
- [x] DONE - Send completion email to Robert, Sonat, Mark, and Sebastian.
- [x] DONE - Tighten matching before automatic account updates:
  - Address-backed matches are the only automatic do-not-sell/cured updates.
  - Weak exact-name/city matches are recorded to the run entries for review only.
  - Duplicate source rows are deduped by Portal account before account status updates.
  - Same-run delinquency/cure overlap now resolves with delinquency winning.
- [ ] TODO - Prefer license number match when Portal has account license numbers.
- [x] DONE - Verify live /order do-not-sell review page server-side under an admin session. Readback showed latest run, active IL do-not-sell accounts, email sent status, `Active/Cured`, `Review Only`, and `Latest KOVAL Invoice`.
- [x] DONE - Verify live /dist server-side under an admin session.
- [x] DONE - Confirm recipient list for current ILCC do-not-sell/cure summary emails: Robert, Sonat, Mark, and Sebastian.
- [x] DONE - Send the first summary email after live DB proof.
- [x] DONE - Verify red warning display in live /portal deployment route. Running frontend/backend images were updated to `v20260622ordering`; backend container source includes `account_do_not_sell`, `Preferred Ordering Mode`, and `Do Not Sell Warning`; compiled frontend assets include `Ordering`, `Do Not Sell Notice`, and `Preferred Ordering Mode`.

## 3. Ordering Block

Robert's input:
- Add a whole block for ordering.
- Make sure the do-not-sell status is visible in /order.
- Ordering should be treated as part of the project plan, not just a field patch.

What was done:
- [x] DONE - Added Do Not Sell and Do Not Sell Warning columns to the /order order table payload.
- [x] DONE - Added account selector warning display so blocked accounts can be seen while filtering/choosing accounts.
- [x] DONE - Added preferred ordering mode to the Portal account ordering block.
- [x] DONE - Added preferred ordering mode visibility to /dist and /order account views.
- [x] DONE - Added pricing override visibility to /dist and /order account/order views.
- [x] DONE - Added account pricing override application to /dist preview pricing and /order pricing-table suggestions.
- [x] DONE - The /order warning uses the same computed source field as Portal:
  - license expired
  - on Illinois delinquency list
  - manual Do Not Sell Notice

Still missing:
- [ ] TODO - Define the full ordering workflow rules:
  - Do-not-sell accounts should warn and require an override reason before order save.
  - Current override access follows the existing /order admin gate.
  - Should override attempts trigger email or in-app notice?
- [x] DONE - Add validation behavior for order save/submit once override rules are approved.
- [ ] TODO - Add test cases for:
  - license-expired account
  - IL delinquency account
  - cured account
  - manual notice only
  - cleared account

## 4. Delivery Times and Delivery Notes

Robert's input:
- Add a section on when delivery times are okay.
- Add notes for delivery.
- Include these as part of the project plan.

What was done:
- [x] DONE - Added this section to the plan as an explicit scope area.
- [x] DONE - Connected it to ordering because delivery timing and notes affect order creation, approval, and fulfillment.
- [x] DONE - Added account-level delivery time notes and delivery notes to Portal.
- [x] DONE - Added delivery time notes and delivery notes visibility in /dist and /order.
- [x] DONE - Added a related delivery schedule table for self-distribution accounts: `koval_crm.account_delivery_schedules`.
- [x] DONE - Added `/dist/schedule.php` for editing preferred delivery day/window, allowed delivery days/window, delivery frequency, route zone, stop order, driver notes, and source notes.
- [x] DONE - Added delivery schedule visibility to `/dist/accounts.php` and `/dist/order.php`.
- [x] DONE - Seeded current Illinois self-distribution accounts with schedule rows so every account is visible as either scheduled or `Needs schedule`.
- [x] DONE - Reworked `/dist/schedule.php` so delivery days/times are entered as individual queryable rows: `window_type`, `day_number`, `start_time`, `end_time`.

Still missing:
- [x] DONE - Define the delivery-time policy fields:
  - preferred or allowed time-frame type
  - delivery day number/name
  - start time
  - end time
  - delivery frequency
  - route zone
  - route stop order
  - driver notes
  - source notes
- [ ] TODO - Enter and verify the actual Lettuce/self-distribution delivery windows from the schedule Robert referenced, then map route days and stop order for the weekly morning delivery run.
- [ ] TODO - Decide whether additional order-level delivery notes are needed beyond the account-level defaults:
  - account-level default delivery notes
  - order-level delivery notes
  - internal-only fulfillment notes
  - customer-facing delivery instructions
- [ ] TODO - Decide whether delivery notes should print/export on order paperwork.
- [ ] TODO - Add validation for delivery time windows after policy is finalized.

## 5. Automation and Reporting

Robert's input:
- Automate via Codex daily.
- Export CSV lists and add dates when last done.
- Email a summary when accounts are added to do-not-sell or can be sold to again.

What was done:
- [x] DONE - Added the command and daily job definition.
- [x] DONE - Added dated CSV export design.
- [x] DONE - Added run table fields for last run date, counts, and email-sent status.
- [x] DONE - Added HTML table email content.
- [x] DONE - Verified the ILCC public export path live through Playwright.
- [x] DONE - Verified OPS database connection works through /ops bootstrap.

Still missing:
- [x] DONE - Apply migration on the live DB.
- [x] DONE - Run first official write scan.
- [x] DONE - Verify the daily scanner is active in live cron. The old Portal jobs-table row is disabled with status `host-cron` because the scraper requires Node outside the PHP container.
- [x] DONE - Verify summary email delivery path through live run `2` and send a separate completion email with Message-ID proof.
- [ ] TODO - Add an owner-facing report page or table if Robert wants review of weak matches before account status changes.

## 6. Frontend / Self Service

Robert's input:
- Start a self-service option using test account `KOVAL Test` / `KOVALTEST` for now.
- Add `/order/self.php` and `/dist/self.php`.
- Make it an easy order page:
  - reorder
  - see past orders
  - catalog-style frontend ordering
  - recent orders
  - popular products
  - QR code
  - easy scan
  - phone ordering
- Sonat order notes:
  - customer scans a QR code
  - signup should capture email and cell phone
  - send a welcome message
  - KOVAL can then text or email to ask whether they need an order
  - customers need a visual ordering surface
  - customers should not need a separate login every time
  - KOVAL should still be able to "go" to the customer to take orders in person, by phone, or by email
- Price / invoices / Heritage notes:
  - use pricing grid
  - delivery fee
  - Cook County gallonage: `$2.50 / GAL`
  - Chicago on-premise: `$2.68`
  - clarify how taxes should be charged
  - no delivery fee for EMA
  - pricing tiers based on one case, on-premise, and other price-list rules
  - create price lists
  - clarify whether liquor taxes apply only for Chicago on-premise accounts
- EZ order automation:
  - see past orders
  - order again
  - "are you out of this?" reminders
  - forgotten-order reminders
  - email reorder suggestions
  - introduce new products
  - add customers to a newsletter
- Order process:
  - Magic link account access should be the default low-friction path
  - magic link: "click here to open your account"
  - magic link should be valid for about 3 hours
  - otherwise normal login
  - expired link should offer "send a new magic link"

What was done:
- [x] DONE - Recorded Robert's self-service request as AI Manager input `3396`.
- [x] DONE - Added `/dist/self.php` as a first self-distribution self-service prototype for `KOVALTEST`.
- [x] DONE - Added `/order/self.php` as a first distributor-passing self-service prototype for `KOVALTEST`.
- [x] DONE - Both pages show:
  - welcome/account context
  - QR / Magic Link placeholder and target URL
  - pricing/fee modeling notes
  - recent orders / reorder area
  - catalog/product cards
  - order quantity fields
  - order draft summary with estimated product total
  - generated mailto draft for phone/email follow-up
  - order notes field for Sonat/customer/delivery/follow-up notes
  - explicit prototype label that no order is submitted yet
- [x] DONE - `/dist/self.php` reads latest self-distribution/warehouse invoice history from `koval_distillery.invoice_history` / `vw_invoice_items`.
- [x] DONE - `/order/self.php` reads latest distributor-passing/CRM invoice history from `koval_crm.vtiger_invoice` / `vtiger_inventoryproductrel`.
- [x] DONE - Live `/dist` was pulled to commit `8404dd8`; live `/order` was pulled to commit `20bef7c`.
- [x] DONE - Live server-side render and browser-like HTTP checks confirmed both pages show `KOVALTEST`, `QR / Magic Link`, `Catalog`, and `Order Draft`.
- [x] DONE - Live server-side render confirmed each prototype currently loads 24 catalog products.
- [x] DONE - Recorded Robert's catalog/mobile refinement as AI Manager input 3400.
- [x] DONE - Limited the default catalog browsing view to the top 15 products on both `/dist/self.php` and `/order/self.php`.
- [x] DONE - Added product-name search so customers can expand browsing by typing a product name.
- [x] DONE - Added `Show all` / `Show top 15` catalog expansion controls.
- [x] DONE - Updated the self-service pages for mobile friendliness:
  - stacked mobile layout
  - full-width phone/email buttons
  - single-column catalog
  - mobile-safe sticky order draft
  - product name wrapping
- [x] DONE - Live `/dist` was pulled to commit `47c0ec8`; live `/order` was pulled to commit `99764a6`.
- [x] DONE - Mobile Playwright verification at 390px width confirmed:
  - `/dist/self.php`: 15 initially visible products, 142 total after Show all, search works, no horizontal overflow.
  - `/order/self.php`: 15 initially visible products, 129 total after Show all, search works, no horizontal overflow.
- [x] DONE - Recorded Robert's WH-sales/images/clickable-quantity refinement as AI Manager input 3403.
- [x] DONE - Changed `/dist` self-service product ranking from alphabetical browsing to WH-sales ranking using warehouse invoice history.
- [x] DONE - Added product image URLs to `/dist` self-service products from Portal product label images.
- [x] DONE - Replaced plain case number entry with larger dropdown plus minus/plus tap buttons on both `/dist/self.php` and `/order/self.php`.
- [x] DONE - Live `/dist` was pulled to commit `c5ad423`; live `/order` was pulled to commit `5eb7f30`.
- [x] DONE - Live WH-sales SQL readback confirmed the top `/dist` products now start with KOVAL Bourbon, KOVAL Cranberry Gin Liqueur, KOVAL Rye, KOVAL Dry Gin, and KOVAL Four Grain.
- [x] DONE - Mobile Playwright verification at 390px width confirmed:
  - `/dist/self.php`: first product `KOVAL Bourbon [W 47% 6x750ML]`, 12 visible images among the top 15, plus button sets 1 case, draft total updates to `$144.00`, no horizontal overflow.
  - `/order/self.php`: first product `KOVAL Bourbon [W 47% 6x750ML]`, 10 visible images among the top 15, plus button sets 1 case, draft total updates to `$144.00`, no horizontal overflow.
- [x] DONE - Recorded Robert's pricing-sheet correction as AI Manager input 3406.
- [x] DONE - Corrected `/dist/self.php` so displayed case prices and draft totals use the pricing sheet (`koval_crm.distribution_product_pricing_tiers`) instead of raw `vw_products` case price.
- [x] DONE - Corrected `/order/self.php` test-account pricing category fallback so `KOVALTEST` uses the `Vendor - Retail` pricing sheet instead of product fallback pricing.
- [x] DONE - Live `/dist` was pulled to commit `90305a3`; live `/order` was pulled to commit `c6f2d8a`.
- [x] DONE - Mobile Playwright verification at 390px width confirmed both `/dist/self.php` and `/order/self.php` show first product `KOVAL Bourbon [W 47% 6x750ML]`, pricing-sheet `data-price=225`, draft total `$225.00`, and visible `Pricing sheet` label.
- [x] DONE - Recorded Robert's IL payout/internal-order follow-up as AI Manager input 3410.
- [x] DONE - Updated `/salesreport/2026-IL-Product-Payout-Calculator.php` so delivery defaults to `$6.00` per invoice instead of `$11.50` per case.
- [x] DONE - Updated the IL payout calculator tax add-ons:
  - Cook County: `$2.50/GAL`
  - Chicago on-premise `Vendor - Bar`: `$2.68/GAL`
  - Existing IL statewide rates remain in the calculator.
- [x] DONE - Updated the calculator UI labels and note to say `Delivery / invoice`, `Delivery Total`, `Delivery / Case`, and to explain the Cook County / Chicago on-premise add-ons.
- [x] DONE - Updated `/dist/self.php` and `/order/self.php` so pricing-sheet quantity tiers adjust the displayed card price and draft total as case quantity changes.
- [x] DONE - Updated internal `/order/order.php` so a salesperson opening a non-standard test/sales account falls back to `Vendor - Retail` pricing-sheet rows instead of raw product fallback pricing.
- [x] DONE - Live `/salesreport` was pulled to commit `b13c156`; live `/dist` was pulled to commit `17176e1`; live `/order` was pulled to commit `ed73f2b`.
- [x] DONE - Live source/readback verified calculator strings for `delivery_per_invoice`, `$6.00 per invoice`, Cook `$2.50/GAL`, Chicago `$2.68/GAL`, and the deployed tax constants.
- [x] DONE - Mobile Playwright verification at 390px width confirmed both `/dist/self.php` and `/order/self.php`:
  - first product `KOVAL Bourbon [W 47% 6x750ML]`
  - one case uses `$211.50`
  - two cases changes displayed case price to `$202.50`
  - two-case draft total becomes `$405.00`

Latest build step:
- [x] DONE - Recorded Robert's approval to implement the shared pricing/tax/delivery calculator and internal salesperson catalog as AI Manager input `3414`.
- [x] DONE - Extracted shared Illinois ordering math into `/order/lib/IlOrderCalculator.php` so `/salesreport`, `/order`, and `/dist` use one pricing/tax/delivery helper instead of drifting local copies.
- [x] DONE - Wired `/salesreport/2026-IL-Product-Payout-Calculator.php` to the shared helper for `$6.00` per-invoice delivery, Cook County `$2.50/GAL`, Chicago on-premise `$2.68/GAL`, and quantity/tax constants.
- [x] DONE - Wired `/order/self.php`, `/order/lib/DistData.php`, `/dist/self.php`, and `/dist/lib/DistData.php` to the shared helper so customer self-service, salesperson/internal ordering, and distributor/self-distribution previews use the same pricing-sheet quantity tiers.
- [x] DONE - Added an internal salesperson catalog mode to `/order/order.php` that mirrors `/order/self.php` cards/search/top-products while keeping internal order controls:
  - account pricing tier selector
  - do-not-sell override reason
  - manual price override
  - save draft order
  - contact/account notes
- [x] DONE - The internal salesperson catalog includes product cards, product images when available, product-name search, `Show all` / top-15 browsing, case quantity controls, pricing-tier updates by quantity, and `Add to Draft` that fills the normal internal order line table.
- [x] DONE - Live `/order` was pulled to commit `217ba73`; live `/dist` was pulled to commit `51a7bbc`; live `/salesreport` was pulled to commit `860cc3b`.
- [x] DONE - Live lint passed for `/order/lib/IlOrderCalculator.php`, `/order/lib/DistData.php`, `/order/order.php`, `/order/self.php`, `/dist/lib/DistData.php`, `/dist/self.php`, and `/salesreport/2026-IL-Product-Payout-Calculator.php`.
- [x] DONE - Live SSH source/readback confirmed `/order/order.php` contains `Salesperson Catalog`, `data-sales-catalog-search`, `data-sales-add-to-draft`, `dist-sales-product-card`, and `distPriceForQuantity`.
- [x] DONE - Live SSH source/readback confirmed `/salesreport`, `/order`, and `/dist` call the shared calculator functions `koval_il_order_tax_rates`, `koval_il_order_delivery_total`, and `koval_il_order_price_for_quantity`.
- [x] DONE - Mobile Playwright verification at 390px width confirmed both `/dist/self.php` and `/order/self.php`:
  - first product `KOVAL Bourbon [W 47% 6x750ML]`
  - one case uses `$211.50`
  - two cases changes displayed case price to `$202.50`
  - two-case draft total becomes `$405.00`
- [x] DONE - Recorded Robert's approval to continue with self-service magic link / QR work as AI Manager input `3419`.
- [x] DONE - Added shared magic-link token storage and validation in `/order/lib/SelfServiceMagicLink.php`:
  - stores token hashes only
  - 3-hour default expiry
  - one-time token validation marks `used_at`
  - supports both `/order` and `/dist` surfaces
  - default KOVAL Test email comes from Robert's CRM user email and is masked in UI/readback
- [x] DONE - Added `/order/login.php` and `/dist/login.php` as public self-service request pages for the `KOVALTEST` account.
- [x] DONE - Added `/order/magic.php` and `/dist/magic.php` to validate magic tokens, create account-scoped self-service sessions, and redirect into `self.php`.
- [x] DONE - Replaced the QR placeholder on `/order/self.php` and `/dist/self.php` with live QR canvases that encode the public magic-link request URLs:
  - `/order/login.php?account_id=150267`
  - `/dist/login.php?account_id=150267`
- [x] DONE - Live `/order` was pulled to commit `82e51af`; live `/dist` was pulled to commit `cc74d07`.
- [x] DONE - Live DB readback confirmed `koval_crm.self_service_magic_links` has KOVALTEST hashed test-link rows for both `order` and `dist`, using masked email `r***@kovaldistillery.com`.
- [x] DONE - Live HTTP POST tests confirmed both request forms return `Magic link prepared ... No email was sent by this test form.`
- [x] DONE - Live magic-open tests confirmed both `/order/magic.php` and `/dist/magic.php` validate a new unprinted token with browser-like user agent and return `302 Location: self.php`; DB readback confirmed used rows for both surfaces.
- [x] DONE - Mobile Playwright verification at 390px width confirmed both live self-service pages render nonblank `140x140` QR canvases with the expected public request URL.

Still missing:
- [x] DONE - Replace the CSS QR placeholder with a real per-account QR image or QR-generation endpoint.
- [x] DONE - Add magic-link token issuance, expiry, and validation with a 3-hour default lifetime.
- [ ] TODO - Add expired-link flow to request a new magic link by email or cell phone after the send channel is approved.
- [ ] TODO - Add signup/contact capture for email, cell phone, SMS consent, and newsletter opt-in.
- [ ] TODO - Add welcome message sending and readback proof.
- [ ] TODO - Add actual order submission after pricing, tax, delivery fee, and do-not-sell override rules are finalized.
- [ ] TODO - Model delivery fee rules, including EMA no-delivery-fee exception.
- [ ] TODO - Model Cook County and Chicago on-premise gallonage/tax rules.
- [ ] TODO - Create and apply account price lists / pricing tiers beyond the current pricing-grid read.
- [ ] TODO - Define Heritage invoice assumptions and where those invoice totals should display.
- [ ] TODO - Add SMS/email reminder workflow:
  - reorder suggestions
  - out-of-stock / are-you-out prompts
  - forgotten-order reminders
  - new product introductions
- [ ] TODO - Decide whether the self-service pages should remain open by account magic link only, require normal login fallback, or support both.
- [x] DONE - Add browser QA on phone viewport once the real magic-link route exists.

## 7. Implementation and Verification Log

What was verified:
- Google Doc update path works by direct document ID.
- ILCC page renders and exports CSV from the public site.
- OPS DB connection works through /ops bootstrap / crm integration path.
- New ILCC tables, account/contact preference tables, contact classification seed, and ILCC job row are present on the live DB checked through OPS.
- First official live scan wrote run `1`; live readback confirmed 2,122 delinquency rows, 438 cured rows, 311 deduped delinquency matches, 67 deduped cured matches, 135 active delinquent accounts, and 39 cured records.
- Same-run overlap correction was applied so zero automatic delinquency matches remain unblocked.
- Live scanner wrapper wrote run `2`; live readback confirmed email_sent=1 and active IL do-not-sell count remained 135.
- Live /order server-side admin render verified `Do Not Sell Matches`, latest run `#1`, matched rows, and active IL do-not-sell count before run `2`; live /dist server-side admin render verified the ordering page.
- Completion email sent to Robert, Sonat, Mark, and Sebastian with Message-ID `<178214680890.93153.2044048039276729454@kovaldistillery.com>`.
- Live /order was pulled to commit `788dcf9` to clarify weak ILCC matches. Rendered readback confirms Aba and Athena examples now show `Needs review / Weak match, not blocked`.
- Live /order was pulled to commit `0aa57fa` to require do-not-sell override reason on order save.
- Live /order accounts render includes `Latest KOVAL Invoice`.
- Live /order was pulled to commit `f27b63b` to hide weak review-only ILCC rows from the default Do Not Sell view. Server-side admin render of `/order/do-not-sell.php` confirmed `#267434`, `PORKCHOP`, `THE GRAND CABARET`, `#270189`, `THE HEN`, and `Athena Greek Resturant` are not present in the default `Active/Cured` view, while `Latest KOVAL Invoice`, `Review Only`, and `Active/Cured` are present.
- Server-side admin render of `/order/do-not-sell.php?list_type=review` confirmed those Aba/PORKCHOP and Athena/THE HEN examples remain available only under `Review Only` as `Needs review / Weak match, not blocked`.
- Live /order was pulled to commit `7857a68` to add the frozen table header, sortable columns, and Portal/ILCC name search on `/order/do-not-sell.php`. Live host readback confirmed `position: sticky`, `data-do-not-sell-search`, sortable `data-sort-column` headers, JavaScript sort/search hooks, and stylesheet version `20260622-1`.
- Live Portal backend/frontend were built and deployed from `/home/koval/dockerportal/portal-builds/portal-v20260622ordering` with Docker tag `v20260622ordering`. Before deploy, running live Portal images were still `v20260620selfdist` and did not contain the do-not-sell/order-preference strings. After deploy, backend readback inside `koval-crm-backend` confirmed `account_do_not_sell`, `Preferred Ordering Mode`, and `Do Not Sell Warning`; frontend readback inside `koval-crm-frontend` confirmed compiled assets containing `Ordering`, `Do Not Sell Notice`, and `Preferred Ordering Mode`.
- Live /dist was pulled to commit `7f0aa70` and accounts render includes `Latest WH Invoice`.
- Live /order was pulled to commit `e9908ee` to add the My Accounts section on `order.php`. Live DB readback for user `1` returned 16 active order-eligible hitlist accounts, including Portal-equivalent assignment name/date and latest KOVAL invoice date/amount. Server-side admin render confirmed `My Accounts`, `Name Search`, `data-my-accounts-table`, `Latest KOVAL Invoice`, and Portal account links.
- Live /dist was pulled to commit `54e2ad2` to add the Delivery Schedule page and related table. Live DB readback confirmed `koval_crm.account_delivery_schedules` has 12 rows and `/dist` sees 11 active self-distribution schedule accounts. Server-side admin render confirmed `/dist/schedule.php` has `Delivery Schedule`, `Route Planner`, `Account Search`, `preferred_delivery_day`, `route_zone`, and `source_notes`; `/dist/accounts.php` shows the Delivery Schedule column; `/dist/order.php` shows Delivery schedule for selected accounts.
- A transaction rollback save test on live `/dist` confirmed the delivery schedule save path writes inside the transaction and rolls back cleanly after commit `54e2ad2`.
- Live /dist was pulled to commit `1d6fd6d` to normalize delivery schedule time frames. Live DB readback confirmed `koval_crm.account_delivery_schedule_windows` exists with columns `id, account_id, window_type, day_number, day_name, start_time, end_time, notes, updated_by, created_at, updated_at`. Server-side admin render confirmed `/dist/schedule.php` now shows `Delivery Time Frames`, `window_type[]`, `window_day_number[]`, `window_start_time[]`, and `window_end_time[]`. A rollback test wrote queryable rows like `preferred:Tuesday:09:00:00-11:00:00` and rolled back to zero test rows.
- Live /order was pulled to commit `2baee68` to add the `My Accounts` nav link. Server-side admin render confirmed `order.php#my-accounts` and `id=\"my-accounts\"`.
- Live /dist was pulled to commit `619e215` after adding self-distribution do-not-sell checks and account fulfillment. Live DB readback confirmed 11 active self-distribution accounts, 0 currently on the IL do-not-sell list, and fulfillment tables `account_delivery_fulfillments` plus `account_delivery_fulfillment_files`. Server-side admin render confirmed the /dist accounts do-not-sell column/status, /dist fulfillment page, BOL upload, invoice upload, delivered-items image upload, and recent fulfillments section.
- Local PHP syntax checks passed for the touched backend files.

Known blockers:
- Local Portal artisan command cannot connect to MariaDB from the current host because the DB server rejects this host; live DB work used the OPS SSH/bootstrap path.
- Live /portal browser verification needs the actual Portal deployment route; no `/portal` checkout exists under the live OPS web root checked during this pass.
- Authenticated browser QA with the Codex automation account reaches the live /order and /dist routes but receives expected admin-only `403`; server-side admin-session render verified the intended pages for the requested admin users.

Next recommended sequence:
- Identify the correct Portal frontend deployment route and browser-check the Portal warning display.
- Review the 135 active IL do-not-sell accounts and 176 weak delinquency review matches from run `1`.
- Approve automatic strong-match blocking.
- Decide whether override attempts should trigger a separate email or in-app notice beyond saving the override reason on the draft order.
