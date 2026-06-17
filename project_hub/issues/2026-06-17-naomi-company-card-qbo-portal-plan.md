# 2026-06-17-QB-creditcard-sync

Created: 2026-06-17
Owner: Robert
Primary worker/persona: Naomi Stern / Finance Operations Coordinator
Task Flow key: naomi-company-card-qbo-portal-sync-daily-2026-06-17
AI Manager inputs: 3297, 3298

Project name: Naomi Company Card QBO Portal Receipt Sync

## Goal

Build the full company-card receipt matching project now, not just the daily recurring Naomi task. The project connects Portal receipt uploads, QuickBooks company-card transactions, BID management reporting, cardholder reminder workflows, and category governance.

## Scope

The first implementation stage should deliver:

- A BID Intelligence report for management showing receipt and QuickBooks transaction matching.
- Filters for user, date, and statement date.
- A statement-date dropdown that includes historic statements plus Current for active charges.
- Manual matching and override controls for receipt/upload state.
- Daily 8:00 PM Naomi QBO transaction download and matching workflow.
- Portal support for QBO-backed missing-receipt placeholder state.
- Portal support for No receipt available as a marked exception.
- Missing-receipt reminder queue or approved send path.
- Category column added to the BID credit-card email summary text.
- Category-source review against the Google Doc named Categories of Credit Card Expenses.

The first implementation stage must not:

- Post transactions in QuickBooks.
- Sync Portal categories to QuickBooks.
- Make accounting/tax policy decisions without owner approval.
- Send reminder emails until the send path and wording are reviewed or already approved by the normal route.

## Source Systems

- Portal receipt upload: https://portal.koval-distillery.com/#/company-card-receipts/receipt/create
- Portal receipt view: https://portal.koval-distillery.com/#/company-card-receipts/all-receipts
- BID credit-card send-out page: https://bid.koval.lan/bid/creditcard.php
- Category source doc: https://docs.google.com/document/d/1TfaKMpXXSFeQ-PIqDyURTIjElxezerszySOrXbo4kBc/edit?tab=t.0

## Implementation Workstreams

1. BID data model and ingestion

- Add a durable BID-side data store for QBO company-card transactions, statement periods, match state, no-receipt exceptions, category overrides, and audit metadata.
- Import historic statement CSV rows from intelligence/creditcard_statements/statements.
- Add an importer path for daily QBO company-card transaction exports.
- Normalize matching fields: transaction date, posted date if present, amount, card last four, cardholder/user, merchant/description, statement period, and source id.

2. Portal receipt matching support

- Extend Portal receipt read data so BID can see receipt category, upload-file count, user, charge date, amount, notes, and reviewed state.
- Add or expose a receipt exception state for No receipt available.
- Allow QBO-created placeholder receipt records without an attached file, clearly marked as requiring follow-up unless No receipt available is selected.
- When an employee later uploads a matching receipt, update or reconcile the placeholder instead of creating duplicate work.

3. BID Intelligence report

- Add a new Intelligence report for receipt and QBO transaction matching.
- Filters: user, date, statement date.
- Statement dropdown: Current plus historic statement periods discovered from statement files and imported QBO rows.
- Report columns should include user/cardholder, transaction date, statement date, merchant/description, amount, Portal receipt id/link, receipt category, match status, file presence, reviewed state, exception marker, and reminder status.
- Highlight unmatched transactions and missing-file placeholders.
- Mark No receipt available rows with an exclamation indicator.
- Allow manual match and override actions with audit fields.

4. Daily Naomi run

- At 8:00 PM daily, download or consume QBO company-card transactions through the approved Naomi/QBO path.
- Match transactions against Portal receipts and existing BID match rows.
- Create/update QBO-backed placeholder receipt rows only through the approved Portal route.
- Queue missing-receipt reminders.
- Produce readback: imported count, matched count, unmatched count, no-receipt exceptions, placeholder updates, duplicates resolved, and exact blocker if QBO/Portal access fails.

5. Reminder workflow

- Build the reminder list first.
- Do not send reminders until the send route and copy are approved or already covered by a normal Naomi owner-visible send path.
- Reminder trigger: no receipt added and no No receipt available exception.
- Reminder should include transaction date, merchant/description, amount, cardholder, and Portal receipt upload link.

6. Category governance

- Read the Google Doc Categories of Credit Card Expenses.
- Compare it to current Portal receipt categories and QBO categories if accessible.
- Add recently added categories such as bar and food supplies if missing, after confirming where categories currently live.
- In this stage, use categories for reporting and email summaries only.
- Later stage: sync Portal categories to QBO after explicit approval.

7. Credit-card email summary

- Update https://bid.koval.lan/bid/creditcard.php so Email summary (text copied) includes classified receipt/category data.
- Add a category column to the copied text.
- Preserve current cardholder grouping and recipient behavior.
- If a transaction is unmatched, show Missing receipt or No receipt available rather than leaving the category ambiguous.

8. Faster receipt capture from reminders and /ops

- Add a fast receipt capture path for authenticated /ops users, linked from the summary reminder and from per-transaction reminder flows.
- The capture page should be one-click from the reminder context and should support drag image here and take image for receipt on mobile/desktop.
- The capture flow should read the receipt image for merchant, date, amount, tax/tip if present, and likely category.
- Create a Portal company-card receipt from the capture flow with the image attached when present.
- If the QBO transaction is already present, match the new receipt to that transaction immediately.
- If QBO is not yet present, log all available receipt metadata and transaction context so the daily Naomi/QBO matcher can attach or update the Portal receipt later.
- If the readout is unclear, missing, or not matching any transaction, keep the receipt visible in Portal for the user to fix and in BID for management review.
- Keep BID as the management review surface for all company-card transactions and matching status.
- Keep Portal as the user correction surface for missing, unclear, or unmatched receipt records.

## Acceptance Criteria

- Management can open a BID Intelligence report and filter by user, date, and statement date.
- Statement filter includes Current and historic statement periods.
- At least one historic statement can be imported and shown with match statuses.
- Portal receipt rows can be matched to transactions by user/card/date/amount/description signals.
- Manual match and override actions persist and are visible on reload.
- No receipt available is represented distinctly from missing receipt.
- Missing receipt rows are highlighted.
- Daily Naomi run produces a durable readback artifact and does not silently fail.
- Email summary copied from BID includes a receipt/category column.
- Reminder and summary links provide a fast authenticated receipt capture path with image upload/camera capture.
- Fast capture can create or update a Portal receipt and either match immediately to QBO or leave a pending match record for the daily Naomi run.
- The project plan and verbatim owner instructions remain available in AI Cloud.

## Verification Plan

- Run PHP syntax checks on changed BID and Portal backend files.
- Run any existing targeted tests or add small parser/model tests where the repo supports them.
- Verify BID report renders locally or on the accepted dev/live route.
- Verify filters preserve expected rows.
- Verify copied email text contains the category column.
- Verify fast receipt capture can accept image upload and camera capture from /ops while logged in.
- Verify image readout populates receipt fields but leaves uncertain values reviewable.
- Verify capture records created before a QBO transaction exists are later matched or updated by the Naomi/QBO run.
- Verify Portal APIs return no-receipt/missing-file state without breaking existing receipt pages.
- Verify Task Flow/handoff readback for the daily Naomi task.
- Before any live send or QBO posting stage, require an owner-visible proof checkpoint.

## Implementation Notes - 2026-06-17

- BID receipt matching report and per-row actions are deployed in the visible BID trees.
- The Remind action now attempts server-side sending through the Portal mailer route and reports specific blocker codes instead of the generic send_failed message.
- Direct local PHP mail is not currently usable for BID reminders because the server mail command is backed by msmtp without a default account for the BID/PHP runtime.
- Remote readback after deployment:
  - /srv/development/bid reports portal_api_credentials_missing.
  - /srv/bid reports portal_api_not_configured.
- Earlier local development readback also showed a mandatory Portal password-reset blocker for one configured API user. Treat that as local-context evidence only; the deployed server trees currently need the Portal API base URL and credentials configuration fixed first.
- No live reminder email was sent during validation.

## Implementation Notes - Portal Notification Route Follow-up

- Robert clarified that reminder sends should use the existing /portal send-report/notification route rather than BID local mail.
- BID commit 779fa30 switches the reminder payload to Portal `POST /notifications/send` with category/event `receipts.company_card_reminder`.
- Portal commit 7fb10a9b adds the `receipts.company_card_reminder` notification migration and Blade email template on the Portal `dev` branch.
- Do not deploy the BID route switch live ahead of the Portal template/rule deployment. The Portal migration should be deployed/run first, then BID can be synced so Remind sends through the correct Portal notification event.
- OPS task 372664 was created for Codex pickup on 2026-06-18 at 10:00 AM CDT. It covers the next items: Portal fast-capture support, QBO API pull by card user starting with Sonat, and BID summary email enhancement.

## Verbatim Robert Instructions

```text
ok... we need a new task for Naomi that repeats daily. It is a /portal and
  Quickbooks sync. currently our employees upload receipts here: https://
  portal.koval-distillery.com/#/company-card-receipts/receipt/create we also
  have a 'view' page https://portal.koval-distillery.com/#/company-card-
  receipts/all-receipts
 in addition we have a manual send out page where I download the monthly statements and send each card user a message to review the transactions once more. 
https://bid.koval.lan/bid/creditcard.php

in /bid ... we need a report under "Intelligence" for management to see
receipt and quickbooks transaction matching
make filterable by user, date, satement date (pre-populated drop down... should be historic statements and 'current' for active charges)
allow matching there for transactions and override of receipt upload (see below)

Naomi should download Quickbooks transactions at 8pm:
- match the receipts to active quickbooks charges
- add not properly classified receipts to portal from qbo (receipts ... allow non file presence but remind) ... could be people add the receipts later, then we need to to update this as duplicates
- send out a reminder E-mail if (no receipt was added) ... 
- allow drop down of 'no receipt available' for some transactions (these need to be marked though with an ! ) ... needs /portal change ... otherwise highlight line items that don't have an associated receipt
- (later stage... add in description but don't do this yet) ... post transactions in QB
- later stage: classify from receipts categories in /portal (sync /portal categories to QB) ... use this... 
  Categories of Credit Card Expenses  https://docs.google.com/document/d/1TfaKMpXXSFeQ-PIqDyURTIjElxezerszySOrXbo4kBc/edit?tab=t.0
  and update the document with items we have added recently (bar ... food supplies etc.) not sure if that is already allowed in /portal receipts or only available as a category in QB
- when generating the summary to send out https://bid.koval.lan/bid/creditcard.php... match to classified receipts (and add our own categories) as a column when I click ... "Email summary (text copied) add project doc in folder it with 2026-06-17-QB-creditcard-sync title
```

## Verbatim Robert Follow-up - Fast Receipt Capture

```text
we need a faster way to do this... the summary remidner that gets sent out and the remind function should have a quick way to add receipts that is more automated. when logged into /ops, we should have a one click ... drag image here or take image for receipt ... it should read out info from image, create portal receipt, see if QB log is already present, otherwise log what's possible and later match and update receipts in portal when available... then have the /bid platform for management review (as is now) for all transactions and the receipts in /portal for users to fix when there is something missing / unclear / not matching at all. - add to Google Doc as well
```
