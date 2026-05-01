# National Outreach Handoff

## 2026-05-01 AI Manager / Task Manager Handoff

- Robert asked to stop using this top-level terminal as the active owner. Ongoing National Outreach follow-through should be supervised by AI Manager, routed through Task Manager, and executed only by scoped visible AI workers.
- Eataly should not be continued from this chat. Vanessa already sent the approved options to Eataly: Thursday May 28 4-7 PM, Friday May 29 4-7 PM, and Saturday May 30 12-3 PM or 3-6 PM. Keep ownership with scheduled action `vanessa-eataly-date-confirmation-followup-2026-05-04-1000`, which must check for an Eataly reply before reminding Robert.
- Code/Git closeout from this lane is done for the isolated National Outreach guidance files: `ai_workspace` commit `2b2f5e9` / `Add National Outreach tasting prep guidance` was pushed to `origin/main`. It includes `ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md`, `scripts/build_mitch_weekly_report.php`, and `templates/taster-reminder-product-carry.md`.
- Remaining National Outreach source changes are mixed with broader worker/runtime/doc changes. Task Manager should route those as separate worker lanes, especially the large `../scripts/nationaloutreach_mail_cycle.py` diff, rather than bundling them into this closed top-level chat.

## 2026-05-01 Chat Closeout / Eataly Ownership

- Robert noted that the Eataly choice/instruction was already given to Vanessa in another active session and asked to close this chat while recording progress properly.
- Current National Outreach state already records the Eataly outcome: Vanessa replied externally to Israel Del Valle, cc Philippe Stengel, offering Thursday May 28 4-7 PM, Friday May 29 4-7 PM, and Saturday May 30 12-3 PM or 3-6 PM. Message-ID `<177764586042.73937.15837486335137527806@kovaldistillery.com>`.
- This chat should not continue Eataly coordination. Follow-up ownership remains with the active National Outreach/session path and scheduled action `vanessa-eataly-date-confirmation-followup-2026-05-04-1000`, which should check for an Eataly reply before reminding Robert.
- Progress from this chat that is complete: Vanessa product-carry tasting reminder workflow implemented, OPS task `367872` completed silently, `Product / sample prep` added to the Monday Mitch weekly draft generator, and direct reminder template `templates/taster-reminder-product-carry.md` added.
- Remaining technical closeout: review/stage/commit the dirty `ai_workspace` and `salesreport` changes through Code/Git Manager, preserving unrelated worker/runtime/doc edits.

## 2026-05-01 Active INBOX Cleanup / Replies Sent

- Reviewed the 11 active National Outreach INBOX messages that the repaired poller surfaced. Sent three required replies:
  - Eataly external reply to Israel Del Valle, cc Philippe Stengel, offering second-half May options: Thursday May 28 4-7 PM, Friday May 29 4-7 PM, and Saturday May 30 12-3 PM or 3-6 PM. Message-ID `<177764586042.73937.15837486335137527806@kovaldistillery.com>`.
  - Sebastian internal acknowledgement, cc Robert and Sonat, confirming Sebastian owns the Whiskey and Cigar Social permit path: Village of East Dundee local approval first, then CDTPL application to ILCC. Message-ID `<177764586306.73937.9962388653480725706@kovaldistillery.com>`.
  - Robert internal readback for Christine Cummins / OPS shift details and manual links. OPS readback found Christine assigned to Target - Elston on 2026-05-01 17:00-20:00, plus future shifts on 2026-05-03, 2026-05-15, and 2026-05-17. Message-ID `<177764586180.73937.411076157053032919@kovaldistillery.com>`.
- Added follow-up scheduled actions:
  - `vanessa-eataly-date-confirmation-followup-2026-05-04-1000`: check for an Eataly reply to the May 28/29/30 options before reminding Robert.
  - `vanessa-whiskey-cigar-permit-obtained-followup-2026-05-05-1000`: check for Sebastian permit-obtained confirmation before reminding Robert.
- The Google Sheets share notification, Portal overdue report notice, Portal daily overview, Robert's open-items directive email, Sonat's Eataly availability request, Robert's Eataly sales question, Robert's Eataly date approval, and Robert's KOVAL-provides-samples note were logged/covered by the replies, scheduled actions, existing TODO state, or existing OPS/Portal task state. No separate reply was needed for those source messages.
- Filed the reviewed active messages out of INBOX. Final runtime verification after filing: `mailbox_total=0`, `active_inbox_count=0`, `queued_sends_sent=0`, `mailbox_mutation=false` for the verification poll.

## 2026-05-01 Vanessa Product-Carry Tasting Reminders

- Robert clarified the practical goal for the Salesreport chain work: give tasters an idea of what products accounts carry so they bring the right samples/materials. The existing chain report / Salesreport Chain Store Intelligence page is already about 90% of what is needed for this reminder workflow.
- Operating rule recorded: Vanessa should include product-carry/sample notes in taster reminders and internal COTeam prep notes when account history is available. Use Salesreport Chain Store Intelligence / Chain Invoice Report as the normal source. For Binny's, yesterday's scraper run can be used as fresher current-placement context when needed, but do not overbuild a scraper-vs-invoice comparison for ordinary reminders.
- Implemented the rule in `nationaloutreach/scripts/build_mitch_weekly_report.php`: the Monday Mitch weekly tastings draft now has a `Product / sample prep` column and explanatory text. Existing OPS product notes populate the column; generic/empty notes fall back to checking Salesreport Chain Store Intelligence / Chain Invoice Report before sending the staff reminder; Connecteam import tags are stripped.
- Added `nationaloutreach/templates/taster-reminder-product-carry.md` for direct Vanessa staff-reminder wording.
- Created OPS task `367872` / `Vanessa: add product-carry notes to tasting reminders`. Readback after implementation: status `Completed`, due/date start `2026-05-01`, creator Robert user `1`, owner/assignee Codex user `1332`, `sendnotification=0`, `deleted=0`.
- Verification: `php -l nationaloutreach/scripts/build_mitch_weekly_report.php` passed. Generated sample report for week starting `2026-05-04` returned valid JSON, included `Product / sample prep`, showed Mariano's product guidance such as `Bourbon, dry gin`, and contained no `connecteam` import tags.
- Scope preserved: no external email was sent, no scraper run was started, and no CRM/OPS business data beyond the task record was mutated.

## 2026-05-01 Active INBOX Polling Fix

- Fixed the National Outreach mailbox cycle so INBOX presence is authoritative. A message being present in `seen-full-body.json` no longer causes it to disappear from polling while it remains in INBOX.
- Source and installed runtime are synchronized: `scripts/nationaloutreach_mail_cycle.py` and `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py`.
- The cycle now writes active state to `/Users/admin/.nationaloutreach-launch/state/active-inbox.json` and reports `mailbox_total`, `active_inbox_count`, `seen_inbox_active_count`, `active_inbox_logged`, `active_route_counts`, and a metadata-only active subject list in each cycle summary.
- Duplicate full review rows are throttled to 15 minutes for already-seen active INBOX messages, but every poll still reports the active INBOX count and metadata. Messages are marked `resolved_not_in_inbox` in active state only after they leave INBOX.
- Verification on 2026-05-01 09:24 Central: first manual no-send poll reported `mailbox_total=11`, `active_inbox_count=11`, `seen_inbox_active_count=11`, `active_inbox_logged=11`; immediate second no-send poll reported `mailbox_total=11`, `active_inbox_count=11`, `seen_inbox_active_count=11`, `active_inbox_logged=0`, proving active messages stay visible without log spam. `mailbox_mutation=false`; no queued send was run in the manual verification.
- LaunchDaemon readback after runtime sync: `system/com.koval.nationaloutreach-auto`, path `/Library/LaunchDaemons/com.koval.nationaloutreach-auto.plist`, program `/Users/admin/.nationaloutreach-launch/runtime/scripts/run_nationaloutreach_auto.sh`, run interval 60 seconds, last exit code 0.

## 2026-05-01 Sebastian Tasting Compliance Directive

- Sebastian replied to Vanessa's Whiskey and Cigar Social regulatory check at 2026-05-01 07:56 Central, cc Robert and Sonat, with the Illinois tasting event compliance policy/SOP folder and the operative question: determine whether the event organizer or KOVAL is providing the samples.
- Verified Drive access using the National Outreach Google Drive account. Folder `1ab2Q28i0oiInLPpvi2vhDSpyTqYQ6CpG` listed two accessible Google Docs: `Illinois Tasting Event Compliance & Notification Policy` and `Illinois Tasting Event Compliance & Notification SOP`. Both exported successfully to owner-only private files under `.private/drive-exports/sebastian-tasting-compliance-2026-05-01/`.
- Recorded the reusable directive at `nationaloutreach/ILLINOIS_TASTING_COMPLIANCE_DIRECTIVE.md`: regular retail tastings such as Binny's, Mariano's, Whole Foods, and similar ordinary account tastings do not need Sebastian notification solely because a tasting is happening. For non-routine Illinois events, if KOVAL supplies or transports spirits samples directly, or if the sample-provider path is unclear, flag for Sebastian / CAO review. Preferred notice is 14 calendar days; minimum internal cutoff is 2 business days for Chicago and 3 business days for Illinois events outside Chicago.
- Applied the directive to Whiskey and Cigar Social: OPS notes say KOVAL is providing sample bottles and swag, and the organizer provides table, tasting cups, and canopy, so Vanessa's reply should proceed on the assumption that KOVAL is providing samples unless Sebastian wants that corrected.
- Vanessa replied to Sebastian, cc Robert and Sonat, subject `Re: Regulatory check: Whiskey and Cigar Social`, Message-ID `<177764278190.59416.16933325823818831448@kovaldistillery.com>`. The reply confirmed document access, summarized the directive, and stated the current KOVAL-provides-samples assumption for East Dundee unless Sebastian wants a different source-of-samples read.
- Filed Sebastian's source message to `Archive`; IMAP readback showed `moved=1`, `INBOX=0`, `Archive=1` for source Message-ID `<CAEbyOZ7KFK=GpJXYAtqUkw+ONm3KstKzUwT+kR9bwDrj7Y+CxA@mail.gmail.com>`.
- Follow-up state: Sebastian guidance is no longer pending; OPS reminder task `367857` was silently marked `Completed` after readback showed creator Robert user `1`, owner Codex user `1332`, deleted `0`. The scheduled reminder `vanessa-whiskey-cigar-sebastian-reminder-2026-05-02-1830` is obsolete and should not email Robert if the due runner sees the resolved state.
- 2026-05-01 Sebastian confirmed he will handle the Whiskey and Cigar Social permit: he needs to obtain local approval from the Village of East Dundee first, then submit the CDTPL application to ILCC, and will update Vanessa once the permit is obtained. No agency contact or permit filing was done by National Outreach.

## 2026-04-30 Shared Task-Flow Recorder

- National Outreach is integrated with the shared email-worker task-flow recorder. Source `../scripts/nationaloutreach_mail_cycle.py` and installed runtime `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py` write task-flow events for classified mail, scheduled-action due/resolved/failed/queued states, sent emails, and send failures. Queryable records go to existing OPS/CRM MySQL tables `koval_crm.ai_task_flow_packets` and `koval_crm.ai_task_flow_events` through `../scripts/task_flow_mysql_recorder.php`; local JSONL audit remains in the runtime state directory. This is shared with Frank and Avignon through `../scripts/shared_task_flow.py`. Current verification passed source and installed runtime Python compile checks, PHP syntax check, and MySQL recorder status. No live mailbox cycle, mailbox filing, email send, service restart, OAuth/auth, credential exposure, Portal/CRM business mutation, Papers write, deploy, commit, push, reset, or clean occurred in the final integration pass.

## 2026-04-30 Signature Closing Correction

- Robert clarified the signature correction: keep the full Vanessa/KOVAL signature block, but use a blank line after `Best,`; for example `Best,`, blank line, then `Vanessa`, followed by the full block starting with `Vanessa Sterling`.
- Updated Vanessa/National Outreach guidance and shared send-from guidance accordingly. The rule is not "short internal notes omit the full block"; it is "`Best,`, blank line, then first name before the normal signature block."
- Robert later confirmed the Maker's Mart Loretta/Rick email is a good Vanessa response model. Added it as durable guidance: concise account-facing context, exact missing-detail questions, older thread facts used as confirmable context, and no internal routing language. Signature correction remains mandatory: `Best,`, blank line, `Vanessa`, blank line, then `Vanessa Sterling` and the full KOVAL block.
- Robert corrected the scope: this signature rule was already shared across all email workers, not just Vanessa. The shared signature-format note, send-from registry, Frank docs, Avignon docs, and persona templates for Naomi, Ezra, Asher, and Venetia now explicitly use `Best,`, blank line, worker first name, blank line, then the full configured signature block. No runtime/send-helper change was made.
- Filed the closed Vanessa socials/signature-link reply into the operational `Archive` label after verifying Robert's confirmation was already out of INBOX and the signature/social-link guidance had been applied. Readback: source Message-ID `<CAAtX44b+J5iVguQGDe2cXuebaf89WcY2k-MQT1T3031J6n1XRw@mail.gmail.com>` is absent from `INBOX` and present in `Archive`.
- Robert clarified a shared open-item directive: recording open, missed, blocked, or waiting email-derived items is not enough. The responsible persona must send the owner an email about the item and include the original source email for review. Added the directive to `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`, `docs/email-workers/README.md`, `worker_roles/send-from-personas.md`, and `nationaloutreach/README.md`.
- Sent owner emails under the new directive:
  - Vanessa -> Robert, subject `Open National Outreach items with original emails for review`, Message-ID `<177759116169.40539.14585694113849626356@kovaldistillery.com>`. Covered Eataly, Whiskey and Cigar Social licensing, COT May staff mailing drafts, Mitch weekly report approval, and the historical Earth Day Google Chat miss; included the original source emails/source review copy in the body.
  - Naomi -> Robert, subject `Open QuickBooks/BID access item with original invite receipt`, Message-ID `<177759116069.40539.9847213200957640225@kovaldistillery.com>`. Covered the QuickBooks/BID access open item and included the original Intuit invite receipt in the body.
  - Ezra -> Robert, subject `Open special-project follow-up with source reference`, Message-ID `<177759115963.40539.16865066435067080591@kovaldistillery.com>`. Covered the Monday Google Doc status/top-five follow-up and included the original source reference because there is no source email for that item in the National Outreach mailbox state.
- Send verification: approved send cycle reported `queued_sends_sent = 3`, `queued_sends_failed = 0`; outbox empty; failed-send folder empty. Live National Outreach `INBOX = 1`, only `Re: Eataly May tasting dates - resent with dates`, waiting on Sonat's decision.
- 2026-04-30 later correction: Robert asked that Vanessa's response go to Sonat and Robert. Vanessa sent the internal Eataly decision note to both Sonat and Robert, subject `Eataly May tasting dates`, Message-ID `<177760427847.6647.4747216382838959523@kovaldistillery.com>`. The task-flow packet now points to OPS task `367855`, scheduled action `vanessa-eataly-sonat-reminder-2026-05-01-1830`, and calendar event `5u18o5908a85qlkvbouf2lo4a0`; status remains waiting on Sonat before any external Eataly reply.
- 2026-04-30 22:00 Central: Sonat replied to Vanessa and Robert asking Vanessa to cross-reference the Eataly May tasting slots with team availability and report whether KOVAL can accommodate one or more slots. The 60-second runner picked it up at 22:01, but the classifier initially routed it to `ezra-katz` because Sonat's standard footer contains legal-disclaimer text. Patched source and installed runtime classifier to strip quoted replies and `Confidentiality Notice:` footer text before route matching; compile check passed and the exact Sonat/Eataly message now classifies as `outreach-coordinator` / `routine-if-clear`. Appended corrected task-flow event `taskflow-6c3f62a33e2dfddd` as `working` on OPS task `367855`. No external Eataly reply was sent.
- 2026-05-01 correction: live INBOX and sent-log readback showed the Sonat availability request had been logged but not answered, and no external Eataly reply had been sent. Vanessa checked OPS COTeam assigned shifts and recorded unavailable time for every Eataly May window. Every slot has at least 9 practical available staff excluding Sebastian. Vanessa sent Sonat the internal availability readback with Robert copied, Message-ID `<177764436215.67020.7909395243028385833@kovaldistillery.com>`. External Eataly reply remains gated until Sonat chooses the dates to offer.
- 2026-05-01 Robert asked how much Eataly ordered in the last year, broken down by month. Vanessa queried Salesreport CRM invoices for Eataly Chicago account `36990`, 2025-05-01 through 2026-04-30, and replied internally to Robert with Sonat copied, Message-ID `<177764500578.70153.8505670869853151279@kovaldistillery.com>`. Readback: `$4,084.08`, 218 bottles, 9 invoices; last invoice 2026-03-31. External Eataly reply still has not been sent.

## 2026-04-30 Naomi QuickBooks/BID Access Follow-up Readback

- Visible Workspaceboard session: `dd735a8c`.
- OPS task `367841` / `Follow up: Naomi QuickBooks invite acceptance` was verified active/not deleted, creator Robert user `1`, owner/assignee Codex user `1332`, status `Not Started`, due `2026-05-04`, priority `Normal`.
- QuickBooks current known state: Robert already sent Naomi Stern the QuickBooks invite, and the Intuit receipt arrived 2026-04-30 to `naomi.stern@kovaldistillery.com`; treat the external-account state as awaiting Naomi acceptance unless a future approved non-secret check shows accepted/active.
- BID readback: `bid_permissions_users` row `22` remains staged for canonical username `naomistern`, full name `Naomi Stern`, `user_id = NULL`, `allow_all = 1`, and all BID section flags enabled.
- Portal/CRM readback: no matching Portal/login user, CRM user, CRM contact, or Portal security rollout row was found for Naomi Stern / `naomistern` / `naomi.stern@kovaldistillery.com` in the checked tables.
- Current blocker: Naomi cannot actually use BID until a Portal/login user exists for `naomistern`; that account creation/welcome step must go through the approved Portal user-creation path.
- Task Manager session `f58e530f` was briefed after this readback to route the Portal user-creation/welcome step visibly if duplicate checks still show no active Naomi user. Required packet: Naomi Stern, `naomi.stern@kovaldistillery.com`, username `naomistern`, purpose BID access activation, related OPS task `367841`.
- Robert then redirected the access plan: use the general Codex user for now instead of creating/activating a Naomi Portal/login user. Task Manager `f58e530f` and Portal worker `aa3bdc5d` were updated with this owner decision; the Naomi-specific Portal user-creation route should close as redirected/no user created.
- Boundaries preserved: no QuickBooks admin access or mutation, credential/token handling, password reset, mailbox-body output, Portal/CRM/OPS mutation beyond readback, production data mutation, commit, push, deploy, or live pull.

## 2026-04-30 Naomi QuickBooks Signup Follow-up

- Robert completed the Naomi Stern Intuit/QuickBooks signup externally in a normal browser.
- Credential record remains private at `.private/logins/quickbooks-naomi-stern.txt`; do not print the password in chat/logs/docs.
- Codex attempted a clean headless login check after signup, but Intuit stopped the flow at a robot/challenge page before password entry. This is an automation/login-verification blocker, not evidence that the signup failed.
- Current path: use Robert's normal browser/session for QuickBooks access, or provide an approved non-headless/session/export path for Codex verification. OPS task `367841` can remain the Monday follow-up unless Robert confirms access is fully working and wants it closed.

## 2026-04-30 Naomi QuickBooks Access Confirmed / First Work Packet

- Robert confirmed Naomi now lands in the KOVAL QuickBooks company.
- Private credential record `.private/logins/quickbooks-naomi-stern.txt` status was updated to `active_confirmed_by_robert`; do not print the password in chat/logs/docs.
- OPS task `367841` / `Follow up: Naomi QuickBooks invite acceptance` was silently marked `Completed` with `sendnotification=0`. Readback before/after showed status changed from `Not Started` to `Completed`, owner/assignee Codex user `1332`, creator Robert user `1`, deleted `0`.
- Created OPS task `367854` / `Naomi QuickBooks first finance packet`, due `2026-05-01`, creator Robert user `1`, owner/assignee Codex user `1332`, status `Not Started`. After Robert narrowed the scope, the OPS subject/description were updated with notifications off to `Naomi QuickBooks current A/P and A/R packet`.
- Task Manager session `f58e530f` was briefed to route the first useful Naomi/QB work through a visible BID/Finance lane. Visible BID worker session `21cea790` / `Naomi QuickBooks first finance packet` was started and accepted the prompt. Robert then narrowed the first useful deliverable to current A/P and A/R only: Accounts Payable aging/current state, Accounts Receivable aging/current state, exact QuickBooks report names Naomi should export/confirm, the date/period to use, secure BID landing/handoff path, and top blockers/questions. Do not broaden into P&L, Balance Sheet, banking, payroll, vendor changes, money movement, or accounting/tax decisions until A/P and A/R are captured.
- Drafted the first Naomi request at `nationaloutreach/drafts/naomi-qb-ap-ar-request-2026-04-30.txt`; it asks only for current A/P Aging and A/R Aging and explicitly says not to make account/vendor/customer/payment/bank/payroll/accounting changes yet.
- Robert corrected the path: Naomi should get the A/P and A/R information out of QuickBooks and email it to Robert, not wait for a request draft. UI login automation is blocked by the Intuit sign-in/challenge flow, so the active path is now a read-only QuickBooks Online Accounting API setup. Official report endpoints to plan around: `AgedReceivables` for A/R Aging Summary and `AgedPayables` for A/P Aging Summary. BID session `21cea790` was updated to prepare the smallest OAuth/API setup packet: client/app credentials storage, realmId/company id capture, refresh-token storage, exact report calls, and Naomi-to-Robert output/email path. No raw secrets/tokens should be printed.
- Created Robert-owned OPS task `367858` / `Set up QuickBooks API for Naomi A/P and A/R reports`, due `2026-04-30`, with detailed OAuth/API setup notes and `sendnotification=0`. Today UI retry got through password and accepted SMS MFA codes, but Intuit then required passkey setup; the `Skip` button stayed disabled in headless Chrome. A headed Chrome retry cannot run from this service session (`SIGTRAP` display/runtime failure). Current UI blocker: passkey setup screen after valid MFA. Durable path remains QuickBooks API/OAuth setup.
- Robert noted the `Skip` button is present. Forced skip after valid MFA worked, and QuickBooks opened as Naomi. Exported current reports as of `2026-04-30`: A/R Aging Summary total `$361,861.67` (`Current 215,748.68`, `1-30 67,559.54`, `31-60 29,587.08`, `61-90 3,469.80`, `91+ 45,496.57`) and A/P Aging Summary total `$26,694.27` (`Current 24,961.87`, `1-30 1,593.24`, `31-60 283.23`, `61-90 -144.07`, no 91+ bucket shown). Private exports saved under `.private/finance/qbo-ap-ar-2026-04-30/exports/`: `ar-aging-2026-04-30.pdf`, `ar-aging-2026-04-30.xlsx`, `ap-aging-2026-04-30.pdf`, `ap-aging-2026-04-30.xlsx`.
- Reusable BID runbook recorded at `/Users/werkstatt/bid/data-management/finance-action-reports/QBO-NAOMI-LOGIN-EXPORT-RUNBOOK.md`. It documents the working Naomi QBO login flow, SMS MFA, forced passkey skip, report export controls, private export folders, BID landing folders, and the date warning that the first P&L attempt defaulted to `January-April, 2026` rather than April-only.
- Robert asked whether everything was in `/BID`. Copied A/R, A/P, Balance Sheet, and verified April-only P&L exports into BID finance landing folders. Corrected P&L by setting QuickBooks start date `04/01/2026`, end date `04/30/2026`, refreshing, and verifying heading `April 2026` before copying. Final BID files are recorded in the QBO runbook.
- Boundaries: no QuickBooks credential printing, no headless QuickBooks automation, no bank/payroll/vendor mutation, no money movement, and no accounting/tax decisions.

## 2026-04-30 Filing Correction / Missed Action Audit

- Robert challenged the QuickBooks invite filing. Correction: the Intuit invite receipt should not have been treated as pure no-action residue; it confirms the invite was sent and creates a follow-up state: wait for Naomi Stern to accept.
- Created OPS task `367841` / `Follow up: Naomi QuickBooks invite acceptance`, due `2026-05-04`, creator Robert user `1`, owner/assignee Codex user `1332`, status `Not Started`, deleted `0`.
- Robert then clarified that Naomi QuickBooks/BID setup must run through Workspaceboard rather than hidden AI Manager or inbox work. Visible BID session `dd735a8c` completed the non-secret Portal/BID/OPS readback and recorded the current status/blocker.
- Robert also corrected the mailbox handling standard: every National Outreach message must be diligently investigated before filing, including full safe thread/body review and splitting multiple instructions into separate dispositions. This was added to the shared inbox-zero directive and National Outreach routing guidance.
- April 2026 audit pass: All Mail from 2026-04-01 through 2026-04-30 produced `490` unique messages. Private full-body audit artifacts are stored under `.private/mailboxes/nationaloutreach/april-2026-missed-action-audit/`; sanitized header audit artifacts are under `.private/mailboxes/nationaloutreach/april-2026-header-action-audit/`.
- Audit scoring found `88` high-priority manual-review items, `387` possible action/context items, and `15` likely no-action items. Cross-check against `nationaloutreach/mail-review.jsonl` showed the high-priority April items were already body-reviewed in the 2026-04-27 review except for a Google Chat missed-message notification and one Mariano's confirmation copy; the Mariano's confirmation also appears in the 2026-04-27 review under the original confirmation thread.
- Noted historical missed/underlogged item: a 2026-04-21 Google Chat missed-message notification from Sonat included a question about who was doing the Earth Day event at Accenture/The Reserve. A related `Fwd: Earth Day - The Reserve` email was body-reviewed on 2026-04-27 and routed as Outreach Coordinator; because the event is now historical, there is no current send to make from that old notification. The lesson is recorded so Chat notification emails are not treated as generic noise when they contain actionable text.
- 2026-04-30 two-week challenge readback: for 2026-04-16 through 2026-04-30, the April audit contains `226` messages, with `54` scored as manual-review. Exact message-id / durable-note cross-check found one unmatched manual-review item: the 2026-04-21 Google Chat missed-message notification from Sonat above. This means the correct answer is not "nothing missed"; at least that historical Chat notification was missed or underlogged at the time, even though the related Earth Day email was later reviewed.
- Current mailbox readback after the audit: National Outreach `INBOX = 1`, `Archive = 7000`. The one active INBOX item is the Eataly May tasting thread waiting on Sonat's decision.
- Audited National Outreach INBOX and same-day Archive headers after the archive sweep. Current findings:
  - LSRCC: Robert explicitly said Vanessa can file it. No action remains.
  - Eataly: Robert copied Sonat and said Sonat should decide; leave active until Sonat responds.
  - Whiskey and Cigar Social: Robert supplied the product list and requested two sends. Vanessa sent Joey the approved bottle list, cc Sebastian and Sonat, Message-ID `<177758766800.99675.13000835292086224815@kovaldistillery.com>`. Vanessa separately asked Sebastian about regulatory/tasting-license needs and timing rules, cc Robert and Sonat, Message-ID `<177758766896.99675.14001659385814241794@kovaldistillery.com>`.
  - Vanessa signature test: Robert replied that the link rendering is correct; no action remains.
  - Jacob Schmidt Board appeal reply was already captured in the legal packet state before the sweep; no new action found in this correction audit.
- Corrected lesson: filing is allowed only after durable state says whether the item is closed, waiting on someone, or converted into a follow-up task.

## 2026-04-30 Ezra Monday Google Doc Status Email Reminder

- Robert asked for Ezra to email Robert and Sebastian on Monday at 8:00 AM with the current status and top 5 things to do from the supplied Google Doc.
- Live OPS/Portal user lookup found no active Ezra/Ezra Katz user row, so the reminder was created as a Codex-owned OPS task rather than assigning it to a nonexistent OPS user.
- Created OPS task `367840` / `Ezra: email Robert and Sebastian status/top 5 from Google Doc`.
- Verified readback: status `Not Started`, start/due `2026-05-04`, `time_start=08:00:00`, `time_end=08:15:00`, `sendnotification=1`, creator Robert user `1`, owner/assignee Codex user `1332`, deleted `0`.
- Recipients recorded in the task: `robert@kovaldistillery.com` and `sebastian.saller@kovaldistillery.com`.
- Source document recorded in the task: `https://docs.google.com/document/d/1-2l-SAn1T8qVEKeFbPDgKiIEKDIYzppHjWoCR3b-c1g/edit?tab=t.0#heading=h.achbmitssp54`.
- Execution note: use Ezra Katz / Special Projects & Legal Affairs send-from persona. Keep the email practical: current status first, then the top five next actions. Use only approved/non-secret facts from the document or locally verified state.

## 2026-04-30 Shared Email-Worker Inbox-Zero Directive / National Outreach Archive Sweep

- Robert clarified that inbox zero applies to all email workers, not only Frank/Avignon. Recorded the shared directive in `docs/email-workers/2026-04-30-shared-inbox-zero.md`, linked it from `docs/email-workers/README.md`, added it to `worker_roles/send-from-personas.md`, and added National Outreach-specific guidance in `nationaloutreach/README.md`.
- Scope of the directive: Frank, Avignon, National Outreach, Vanessa Sterling, Naomi Stern, Ezra Katz, Asher, Venetia, Codex mail routed through National Outreach, and future approved email-worker personas. Active inbox target is `0` open / `0` unread; leave messages open only for real unprocessed work, blockers, decisions, or named dependencies.
- National Outreach mailbox structure decision: use one operational `Archive` folder for old/resolved shared-inbox residue instead of continuing worker-specific handled-folder sprawl. Worker/persona routing is recorded in durable logs, TODO/HANDOFF notes, and visible worker/task state.
- Header-only inventory found `6,991` National Outreach INBOX messages before 2026-04-27. April pre-setup messages had already been body-reviewed into `nationaloutreach/mail-review.jsonl` on 2026-04-27 without mailbox mutation.
- Moved all `6,991` pre-2026-04-27 INBOX messages to `Archive` and removed them from INBOX. Verification: `remaining_pre_2026_04_27_inbox = 0`.
- Reviewed the 7 remaining post-2026-04-27 INBOX messages. Actions taken:
  - Vanessa resent the Eataly May tasting decision note to Robert with the actual May date options included. Message-ID `<177758663983.96692.14146850970270087421@kovaldistillery.com>`.
  - Vanessa forwarded/summarized the original LSRCC Summer Concert Series sponsorship item to Robert as requested. Message-ID `<177758664076.96692.4248234058994302032@kovaldistillery.com>`.
  - Vanessa sent Robert a decision/blocker note asking what bottle list to send Joey Zeller for the 2026-05-14 Whiskey and Cigar Social. Message-ID `<177758664154.96692.1794101299596878343@kovaldistillery.com>`.
  - Robert's Jacob Schmidt reply was already captured in the Jacob appeal packet docs: docket `2609039`, mailed date `2026-04-28`, certified mail for both Board filing and claimant service.
  - Naomi's QuickBooks invite receipt was logged as no-action mailbox residue; Robert already sent the invite.
- Moved the 7 remaining INBOX messages to `Archive` after the above sends/logging. Final National Outreach readback: `INBOX = 0`; `Archive = 6998`.
- Private sweep log: `.private/mailboxes/nationaloutreach/archive_sweeps.jsonl`. No credentials, tokens, session cookies, or private body text were copied into public docs.

## 2026-04-30 Vanessa / Zachary Johnson Maker's Mart Confirmation

- Robert emailed Vanessa at 2026-04-30 13:35 PDT, subject `Fwd: Open COT shifts this weekend`, asking her to check whether Zachary Johnson was recorded for Maker's Mart, record him if missing, and send Zach a confirmation with Robert copied.
- Live National Outreach INBOX/body read found the source as IMAP `7024`, Message-ID `<CAAtX44ZD_68FL0AjBzA8PAj+s81u73CMgLNJ9KLUrreFRCGJRA@mail.gmail.com>`.
- OPS readback found event `668` / `Maker's Mart`, Saturday 2026-05-02 12:00-18:00, with linked shifts `4880` and `5190`. Shift `4880` was assigned to Stephen De Sena; shift `5190` was the second open slot.
- Zachary Johnson is active in OPS as user `1171`; no overlapping May 2 shift was found in the check window. Assigned Zachary Johnson to linked shift `5190`.
- Verification after write: shift `4880` remains assigned to Stephen De Sena; shift `5190` is assigned to Zachary Johnson.
- Vanessa sent Zachary Johnson a confirmation from `vanessa.sterling@kovaldistillery.com`, cc Robert, subject `Maker's Mart shift confirmed for Saturday`, Message-ID `<177758217722.76303.8733150605737434676@kovaldistillery.com>`.
- Source message filed to `Handled`; readback showed `INBOX=0`, `Handled=1` for the source Message-ID. No other OPS event, shift, PHPList, runtime, OAuth/auth, or external account state was changed.
- 2026-04-30 follow-up: Zach asked Vanessa for Maker's Mart event details, projected guest count, product pull guidance, and point of contact. Old National Outreach email history showed The Guesthouse Hotel, 4872 N. Clark St.; event time 12:00-18:00; Rick Verkler as GM; Loretta Wooge managing day-of logistics; Meghan Stover handling marketing; 6-foot table with black tablecloth available; bring KOVAL branded materials; product focus Cranberry Spritz cocktail, Cran Gin Liqueur, Bourbon, and Dry Gin, with ginger and coffee liqueurs also in stock. No projected guest count was found in the old thread.
- Robert approved sending both follow-ups. Vanessa emailed Loretta Wooge and Rick Verkler, cc Robert and Zach, asking for projected guest count, day-of point of contact, arrival/setup instructions, and any updated product priorities. Subject `Maker's Mart details for Saturday`, Message-ID `<177758976955.34228.8555190492595877312@kovaldistillery.com>`.
- Vanessa also emailed Zach, cc Robert, with the confirmed old-thread details and noted that Loretta/Rick were being asked for the missing guest-count/setup information. Subject `Re: Maker's Mart shift confirmed for Saturday`, Message-ID `<177758977058.34228.3580483730739992322@kovaldistillery.com>`.
- Filed Zach's Maker's Mart detail-request source after the follow-ups were sent. Readback: source Message-ID `<CAG_DyTJtO=xVoWH6NuFZnkQ9DjMAc8Q8rFcHZOihtpjeLS7xjQ@mail.gmail.com>` is absent from `INBOX` and present in `Archive`. Remaining National Outreach `INBOX` item is the Eataly May tasting thread waiting on Sonat's decision.

## 2026-04-30 Vanessa Signature Update

- Robert asked that Vanessa's signature include the KOVAL social links inline, matching Robert's email signature style.
- Updated `nationaloutreach/PERSONA.md`, `nationaloutreach/README.md`, and `worker_roles/send-from-personas.md` so future Vanessa external/staff-facing sends use the full signature with the linked social-label line `X | Instagram | Facebook`.
- Superseded spacing correction: Robert later clarified the closing should be `Best,`, blank line, then `Vanessa`, then a blank line before `Vanessa Sterling`; keep the full signature block.
- Robert's follow-up on 2026-04-30 extended the same corrected KOVAL signature format to other email workers. Current guidance keeps the phone number, website, and linked `X | Instagram | Facebook` social-label set on separate lines and avoids raw social URLs next to the labels.
- Did not resend the already-sent Kevin McCarthy email just to change the signature.

## 2026-04-30 Vanessa Shift Switch / COT Draft Correction

- Robert flagged that Vanessa had not emailed him about Kevin McCarthy's 5/10 shift switch or the COT phpList drafts.
- Live readback confirmed the issue: National Outreach sent-log had no Vanessa shift-switch/review note after 2026-04-27, and phpList campaigns `556` and `557` remained `draft`, `processed=0`, `sent=NULL`, linked to list `73` only.
- OPS readback found Kevin McCarthy currently assigned to Mariano's Westchester on Sunday, 2026-05-10, 2:00-5:00 PM, and the May 10 Schaumburg shift found in OPS was open/unassigned.
- Corrective Vanessa review note sent to Robert only, from `vanessa.sterling@kovaldistillery.com`, subject `Kevin 5/10 shift switch draft and COT mailing drafts`, Message-ID `<177756302444.77440.9233654883041090067@kovaldistillery.com>`, sent artifact `/Users/admin/.nationaloutreach-launch/state/sent/vanessa-kevin-shift-switch-and-cot-drafts-robert-20260430.sent-1777563025.json`.
- The email included the first Kevin draft for Robert confirmation and the phpList draft IDs `556` and `557`.
- No email was sent to Kevin, no phpList campaign was queued/sent, and no new OPS mutation was performed from this correction pass.
- Robert then approved emailing Kevin and asked to be kept cc'd. Vanessa sent Kevin McCarthy the May 10 Mariano's Westchester confirmation, cc Robert, Message-ID `<177756318523.77683.12080747380140171382@kovaldistillery.com>`, sent artifact `/Users/admin/.nationaloutreach-launch/state/sent/vanessa-kevin-may10-westchester-20260430.sent-1777563186.json`.
- Vanessa also sent Robert a review copy of phpList draft bodies `556` and `557` plus the explanation that individualized phpList sends use OPS-derived subscriber attribute `Upcoming COT Shifts` (`attributeid 21`) with placeholders `[FIRST NAME]` and `[UPCOMING COT SHIFTS]`; Message-ID `<177756318419.77683.1657624334383249648@kovaldistillery.com>`.
- Later readback correction via OPS CRM integration / `koval_plst1`: phpList campaigns `556` and `557` were sent on 2026-04-30 around 11:17 Central. Both are `status=sent`, list `73`, `processed=18`, with `18` sent user-message rows and `bouncecount=0`.

## 2026-04-30 Vanessa Routing / Naomi and Ezra Directives

- Live National Outreach mail cycle is installed as `system/com.koval.nationaloutreach-auto`, running from `/Users/admin/.nationaloutreach-launch/runtime/scripts/run_nationaloutreach_auto.sh` with `run interval = 60 seconds`; latest readback showed `last exit code = 0`.
- Recent Vanessa-addressed items in private review metadata include:
  - Robert's `Fwd: 5-10 shift switch`, routed as `outreach-coordinator`, `send_allowed=routine-if-clear`.
  - Claude's `Consumer Outreach Events - Schedule Confirmation`, routed as `outreach-coordinator`, `send_allowed=routine-if-clear`.
  - Robert's `Fwd: COT Team`, already corrected/routed to `/Users/werkstatt/lists` for PHPList handling rather than individual National Outreach sends.
- Added source and installed-runtime classifier routes for the new specialist roles. This original split was later corrected by Robert on 2026-04-30; current routing is Naomi for finance operations and Ezra for Special Projects & Legal Affairs.
- Security-sensitive finance/legal mail still routes to `security-guard` first when it includes credentials, OAuth/tokens, 2FA, bank/routing data, urgent payment pressure, private IDs, or suspicious requests.
- No mailbox filing, external send, queued send, credential output, OAuth/token change, LaunchDaemon cadence change, or live OPS/finance/legal mutation was performed by this routing-directive update.

## 2026-04-27 Setup

- `nationaloutreach@kovaldistillery.com` is the main shared AI-worker inbox.
- Outreach Coordinator is now named Vanessa Sterling, with send-from identity `vanessa.sterling@kovaldistillery.com` routed through the approved National Outreach mailbox/runtime path.
- Email Coordinator owns intake/routing.
- Outreach Coordinator owns outreach/tasting scheduling work routed from this inbox.
- `macee.maddox@kovaldistillery.com` is not an allowed send-from identity. Macee has left; use it only as inbound legacy-recipient context while reviewing old mail.
- Private credentials and setup logs stay under `.private/mailboxes/nationaloutreach/`.
- Mailbox setup verification created standard handling labels, verified IMAP/SMTP login, read no bodies, and sent no mail.

## 2026-04-27 LaunchDaemon Prep

- Runtime prepared at `/Users/admin/.nationaloutreach-launch/`.
- Runner: `/Users/admin/.nationaloutreach-launch/runtime/scripts/run_nationaloutreach_auto.sh`.
- Staged LaunchDaemon plist: `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist`.
- Staged install helper: `tmp/nationaloutreach-launch/install-launchdaemon.sh`.
- Initial manual runner verification succeeded in header-only mode: 200 headers, no body reads, no sends.
- Robert then approved full body read and send capability. Runtime was switched to `nationaloutreach_mail_cycle.py`.
- Full-body review verification succeeded for 300 recent INBOX messages. Bodies were stored only in owner-only private runtime state; chat/docs received metadata and route counts only.
- Send capability is enabled through approved queued drafts: place `*.approved.json` files in `/Users/admin/.nationaloutreach-launch/state/outbox/`; the cycle sends them by SMTP and moves them to private sent/failed state. No queued sends existed during verification.
- Robert ran the LaunchDaemon install helper. `com.koval.nationaloutreach-auto` is installed as a system LaunchDaemon.

## First Body-Read Review Counts

- Reviewed: 300 recent messages.
- Outreach Coordinator: 222.
- Marketing Manager: 49.
- Email Coordinator: 11.
- Internal Communicator: 5.
- Security Guard / sensitive-review: 13.

## 2026-04-27 Send-From Correction

- Robert clarified not to send as `macee.maddox@kovaldistillery.com` again because Macee has left.
- `macee.maddox@kovaldistillery.com` was removed from the National Outreach runtime send allow-list.
- Keep Macee only as old-mail inbound-recipient context while reviewing inherited threads.
- Allowed National Outreach account send-from identities are now `vanessa.sterling@kovaldistillery.com`, `nationaloutreach@kovaldistillery.com`, and `codex@kovaldistillery.com`.

## 2026-04-27 Vanessa Sterling Outreach Persona

- Robert named the Outreach Coordinator persona Vanessa Sterling and provided `vanessa.sterling@kovaldistillery.com`.
- Updated the send-from registry, Outreach Coordinator role, National Outreach persona/README, reusable coverage-report templates, operating-model prompt, and installed National Outreach send helper.
- Current approved Outreach send path: send as Vanessa Sterling `<vanessa.sterling@kovaldistillery.com>` through the National Outreach mailbox/runtime. `nationaloutreach@kovaldistillery.com` remains the shared inbox/runtime route and fallback sender.
- `codex@kovaldistillery.com` remains the separate Codex Local Agent route. `macee.maddox@kovaldistillery.com` remains disallowed for outbound sends.

## 2026-04-27 Codex / National Outreach Drive API Prep

- Prepared Drive API bundle: `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/`.
- OAuth login account: `nationaloutreach@kovaldistillery.com`.
- Codex send-from alias: `codex@kovaldistillery.com`.
- Default scopes: `drive.metadata.readonly` and `drive.file`.
- Local token target: `.private/google-oauth/nationaloutreach-google-drive-token.json`.
- Future Infisical secret name: `GOOGLE_DRIVE_CODEX_NATIONALOUTREACH_REFRESH_TOKEN`.
- OAuth was completed and the local owner-only token exists. Future cleanup preference is migrating the refresh token to the approved Infisical path.

## 2026-04-27 Whole Foods Tasting Planning Directive

- Robert asked National Outreach to start syncing Whole Foods portal events into OPS and to import only approved events.
- Directive recorded in `WHOLE_FOODS_TASTING_PLANNING.md`.
- Project log: `project_hub/issues/2026-04-27-whole-foods-ops-sync.md`.
- OPS target is Outreach Events, not general events.
- Requests `310470` and `310472` are treated as not approved based on Robert's supplied URLs showing `ApprovedByBuyer=Pending`; they should be noted in the import report but not imported as confirmed OPS events unless the authenticated portal later shows approved buyer status.
- Robert later supplied buyer-approval email evidence for Request `312022`. First approved import completed on 2026-04-27: OPS events `857`-`862`, linked Outreach shifts `5184`-`5189`, product link `18368` for KOVAL Bourbon, account links `24930`, `9163`, `45401`, and `1140`.
- Evanston was handled as two-store sensitive: approved store `10076` at `1640 Chicago Ave` was linked to CRM account `24930`; the separate Green Bay Road Evanston store was not used.
- Remaining pending/not-approved request numbers from the April-June crawl: `310465`, `310468`, `310470`, and `310472`.
- Confirmation was sent from `nationaloutreach@kovaldistillery.com` to `sonat@kovaldistillery.com` and `robert@kovaldistillery.com`; private sent artifact `whole-foods-request-312022-import-2026-04-27.sent-1777326591.json`.
- Robert corrected the pending-events report shape: use proper greeting/closing and HTML tables, and include `Already in OPS`. Reconciliation found all 36 remaining portal-pending rows have OPS Outreach matches already. Treat portal `Pending` as a portal field/status marker, not final business truth, especially for rows dated before/on 2026-04-27. Future sync/report passes should periodically refresh the portal and cross-check OPS before describing a row as not scheduled.
- Revised HTML-table status email sent from National Outreach to Sonat and Robert; private sent artifact `whole-foods-pending-ops-html-table-2026-04-27.sent-1777327159.json`.
- Private artifacts and scripts stay under `.private/wholefoods-sync/`. No credential, token, cookie/session value, or private SOP body was printed into chat/docs/git.

## 2026-04-27 Whole Foods OPS Coverage Recheck

- Robert asked to check Whole Foods again, verify everything is in OPS, and send Robert/Sonat an updated covered/not-covered report.
- Live authenticated WFM refresh completed against April-June scheduled rows: 42 portal rows, request numbers `310465`, `310468`, `310470`, `310472`, and `312022`.
- OPS verification result: 42/42 portal rows have matching OPS Outreach events; 0 missing from OPS; 42/42 have linked Outreach shifts; 28 are fully assigned; 14 still have linked shifts open/unassigned.
- Corrected report sent from `nationaloutreach@kovaldistillery.com` to `sonat@kovaldistillery.com` and `robert@kovaldistillery.com`, subject `Whole Foods OPS coverage update`, Message-ID `<177733985931.34791.17519709108206868262@kovaldistillery.com>`, sent artifact `/Users/admin/.nationaloutreach-launch/state/sent/whole-foods-ops-coverage-2026-04-27.sent-1777339860.json`.
- Private refreshed artifacts: `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.tsv`, `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_apr_may_jun_2026_inventory.json`, and `.private/wholefoods-sync/apr-may-jun-2026/wholefoods_ops_coverage_2026-04-27.html`.
- Robert later clarified future WFM coverage reports must be sent as HTML table emails and open/unassigned rows should be shaded light red.
- Fixed the National Outreach send helper so queued `html_body` content is sent as an HTML alternative, regenerated the WFM report with 14 light-red open/unassigned rows, and resent it to Sonat/Robert. Final HTML-table report Message-ID `<177734005946.38159.11756804899585654178@kovaldistillery.com>`, sent artifact `/Users/admin/.nationaloutreach-launch/state/sent/whole-foods-ops-coverage-2026-04-27.sent-1777340060.json`.

## 2026-04-27 Binny's OPS Coverage Report

- Robert asked for the same coverage report for Binny's.
- Source set: latest approved Connecteam normalized COT import packet, matched to OPS Outreach by Connecteam import key with date/time/title fallback where needed.
- OPS verification result: 39/39 Binny's source rows have matching OPS Outreach events; 0 missing from OPS; 39/39 have linked Outreach shifts; 38 are fully assigned; 1 still has a linked shift open/unassigned (`Binny's Joliet`, 2026-05-30 4pm-7pm).
- HTML-table report sent from `nationaloutreach@kovaldistillery.com` to `robert@kovaldistillery.com`, subject `Binny's OPS coverage update`, Message-ID `<177734055890.39230.5962789951459023273@kovaldistillery.com>`, sent artifact `/Users/admin/.nationaloutreach-launch/state/sent/binnys-ops-coverage-2026-04-27.sent-1777340559.json`.
- Saved durable report templates for future Whole Foods and Binny's coverage reports under `nationaloutreach/templates/`.

## 2026-04-27 Tasting Coverage Reports / Mitch Preview

- Robert asked for four current coverage reports from now through the end of May: Binny's, Mariano's, Whole Foods, and Other. Reports must be HTML tables and highlight unassigned/open rows in light red.
- Sent all four from `nationaloutreach@kovaldistillery.com` to Robert, cc Sonat.
- Sent a separate Robert-only review copy for the proposed Mitch Conti weekly upcoming tastings report. It was not sent to Mitch.
- Message IDs:
  - Binny's: `<177734250062.44365.17514399489366712214@kovaldistillery.com>`
  - Mariano's: `<177734250191.44365.4819296182580694660@kovaldistillery.com>`
  - Other: `<177734250316.44365.2715678582049129153@kovaldistillery.com>`
  - Whole Foods: `<177734250425.44365.13616315935953471321@kovaldistillery.com>`
  - Mitch review copy to Robert: `<177734249943.44365.17981630527134491020@kovaldistillery.com>`
- Approval gate: do not send Mitch Conti the weekly report until Robert approves after reviewing the preview. Requested future recipient after approval is `"Conti, Mitch" <Mitch.Conti@rndc-usa.com>`, cc Robert, every Monday at 8:00am for upcoming tastings that week.
- Until Robert gives go-ahead, remind Robert daily that Mitch weekly report approval is pending.

## 2026-04-29 Vanessa Inbox Review

- Ran a live National Outreach INBOX body-review cycle for the 30 newest messages. Reviewed 30, sent 0 queued messages, moved/filed 0 messages. Route counts: Outreach Coordinator 10, Email Coordinator 8, Internal Communicator 3, Security Guard 5, Marketing Manager 4.
- Current mailbox count after read-only check: INBOX has 7018 messages, 36 unread. The check did not mutate mailbox flags or labels.
- New WFM approval task: admin@interactionsmarketing.com sent `Event Schedule Approval for Koval Inc. dba KOVAL Distillery`, and Robert forwarded it to National Outreach. Request `312318` is approved for KOVAL Bourbon rows at Green Bay Road, Vernon Hills, Lakeview, Lincoln Park, and Edgewater Chicago across 2026-06-11 through 2026-06-14. Live OPS readback found no rows tagged `[wfm-request:312318]` yet.
- New Vanessa/COT task: Robert forwarded `Fwd: COT Team` to Vanessa, cc Sonat, asking Vanessa to email individual COT team members who are scheduled for May so far. Live OPS readback found 14 assigned staff with May 2026 Outreach shifts; this should be routed as an internal Vanessa send/draft task using current OPS schedule data.
- Other recent possible inbox tasks from metadata/body review: Eataly Chicago requested May tasting-date help; Jessica Dalka / Chicago Planner Magazine sent `Future of Sports Event`; 1871 sent ScaleUp May 7 marketing content; Ravenswood newsletter arrived. These are not as directly actionable as Robert's WFM/COT forwards and should be triaged under normal external-send/marketing approval gates.

## 2026-04-29 Vanessa / Lists Mailing Correction

- Robert corrected the COT May mailing route: broad staff mailings like "email everyone for May" must be done through PHPList in `/Users/werkstatt/lists`, not as a batch of individual National Outreach mailbox sends.
- Vanessa should email Robert with concrete blocker questions when the mailing target/content is unclear, then route the approved audience/campaign packet to Lists.

## 2026-04-30 AI Manager Routing

- Routed WFM Request `312318` to visible Workspaceboard OPS session `4e555ea9` (`OPS WFM Request 312318 import/reconciliation`). Brief requires current duplicate-check, KOVAL Bourbon-only OPS Outreach import/reconciliation, deterministic account/store linking, no external send, and completion/blocker readback.
- Routed Vanessa/COT May staff mailing work to visible Workspaceboard Lists session `d220b31d` (`Lists Vanessa COT May staff mailing packet`). Brief requires OPS-sourced May COT audience refresh, PHPList packet/draft handling, no send without Robert approval, and exact blocker questions if content/audience is unclear.

## 2026-04-30 Inbox Sweep Since 2026-04-27

- Reviewed National Outreach INBOX mail since 2026-04-27 after the Zachary Johnson/Maker's Mart correction.
- WFM Request `312318` is no longer open: OPS session `4e555ea9` imported the seven approved KOVAL Bourbon rows as events `869`-`875` and linked shifts `5300`-`5306`.
- Claude's Consumer Outreach handoff is no longer open: Hops & Grapes, Malt Row on Damen, and Ravenswood On Tap are recorded in OPS state; no external reply was sent from this sweep.
- Kevin's 2026-05-10 switch, Vanessa sender tests, COT PHPList draft notices, COT report notification correction, Jacob Schmidt Drive/document shares, Naomi/Ezra intros, and Vanessa signature/social-link directives were already handled or recorded in durable state.
- One external response item remains open: Eataly Chicago sent its May tasting calendar and asked what dates KOVAL can help with. This should be answered only after checking OPS capacity and owner preference; do not auto-commit dates.
- Filed 31 already-handled/no-action messages from 2026-04-27 onward to `Handled`.
- Left three messages open in INBOX: Eataly May tasting calendar response; LSRCC Summer Concert Series sponsorship opportunity; Robert's Naomi/QuickBooks/BID access question.
- Robert clarified the general operating rule: if an inbox item needs a business decision, Vanessa should email Robert the decision note unless there is already a recorded directive for that item class.
- Vanessa sent Robert decision emails for the first two open items:
  - Eataly May tasting dates, Message-ID `<177758333004.82358.6154635019640039816@kovaldistillery.com>`.
  - LSRCC Summer Concert Series sponsorship, Message-ID `<177758333098.82358.9266946590112263793@kovaldistillery.com>`.
- Naomi/QuickBooks/BID remains open because it is an access/permissions item, not a routine outreach decision. Needed from Robert: whether Naomi should receive a QuickBooks Online invite and which permission level/company scope to use; for BID, whether to create an OPS/BID access task for Naomi and what non-secret scope she should have. Do not share credentials in email/chat.
- Robert then approved inviting Naomi to QuickBooks and giving her full BID access; he was unsure which QuickBooks role to use.
- Current Intuit docs indicate `Company admin` is the complete-access QuickBooks Online role, while `Standard all access` can review company info but excludes admin tasks and payroll-level access. Recommended QB role if available: `Company admin`; fallback if Robert wants less than admin/payroll control: `Standard all access`.
- BID full access was granted for canonical future Portal username `naomistern` in `bid_permissions_users`: `allow_all=1` plus system, sales, purchases, foh, finance, market, payroll, and production flags. Readback row id `22`, user_id `NULL`, username `naomistern`, full name `Naomi Stern`.
- Live CRM readback did not find a current Naomi/naomistern Portal user, so the BID permission is pre-staged by username. If Naomi cannot sign in, the separate account setup step is to create/activate Portal user `naomistern` and send the welcome through the approved Portal user-creation path. No credentials were exposed or sent.
- Attempted to create an OPS follow-up task `Invite Naomi Stern to QuickBooks Online`, but the helper hit the known mandatory password-reset gate before returning an ID. No OPS task was created.

## 2026-04-30 Persona Signatures / Send-As Aliases

- Robert confirmed Vanessa, Naomi Stern, and Ezra Katz as Google send-as aliases for the shared National Outreach mailbox route. The installed helper treats all three as verified send-as aliases and still fails closed for unverified future persona aliases unless an explicit visible-Sender exception is used for a controlled test.
- Standard KOVAL persona signatures now include the KOVAL general line `312 878 7988` after `Chicago, IL 60613` and before the website. Vanessa's full signature keeps the inline X, Instagram, and Facebook line.

## 2026-04-30 Naomi / Ezra Role Correction

- Robert corrected the specialist split: Naomi Stern is now the Finance Operations Coordinator; Ezra Katz is now Special Projects & Legal Affairs. Updated role docs, canonical persona YAMLs, National Outreach README/TODO routing notes, and source plus installed National Outreach classifier routing.
- Sent Robert two new intro emails with Sonat copied:
  - Naomi: subject `Intro: Naomi Stern, Finance Operations`, Message-ID `<177757023629.11175.16720151096287987123@kovaldistillery.com>`.
  - Ezra: subject `Intro: Ezra Katz, Special Projects & Legal Affairs`, Message-ID `<177757023515.11175.16378801365318458196@kovaldistillery.com>`.

## 2026-04-29 National Outreach IMAP Bandwidth Guard

- Root cause found in source: `scripts/nationaloutreach_mail_cycle.py` fetched full message bodies before checking `seen-full-body.json`, so repeated cycles could re-download already-seen mail and consume Gmail IMAP download bandwidth.
- Source fix applied: the mailbox cycle now fetches message headers first, checks the dedupe key, and only downloads the full body for new items or explicit `--review-old` runs. It also uses `BODY.PEEK[]` to avoid flag mutation.
- Installed runtime fix applied to `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py` after the LaunchDaemon was found still registered at 60 seconds. The unsafe in-flight process was terminated, the installed copy was patched, and compile verification passed.
- Frank and Avignon standing pollers were checked and patched for the same class of bug. Their source mirrors and installed runtime copies now fetch headers first and only fetch full bodies for messages not already in their automation logs. Frank still limits the scan window; Avignon preserves header-only handling for previously logged INBOX residue.
- Verification: `python3 -m py_compile` passed for National Outreach, Frank, and Avignon source and installed runtime copies. Subsequent launchd readback showed National Outreach and Frank last exit `0`; Avignon continued normal scheduled polling with INBOX count `2` and no new decision items.

## 2026-04-30 Portal COT Report Assignment and Template Review

- Robert asked to check Portal reports assigned to Macee Maddox, assign them to Codex, analyze recent reports/templates, and send sample reports signed by Vanessa Sterling.
- Live Portal readback found Macee user `1265` inactive/deleted and recent historical COT report activity in categories `56` COT Activity - Weekly, `57` COT Activity - Monthly, and `58` COT Activity - Quarterly.
- Codex user `1332` was added as a responsible owner for categories `56`, `57`, and `58`; existing Sonat ownership was preserved and Macee's historical submitted reports were not rewritten.
- Copied 16 currently open reporting reminders from Sonat's live COT queue to Codex: 14 weekly periods from 2026-03-23 through 2026-06-28 and 2 monthly periods from 2026-04-01 through 2026-05-31.
- Durable analysis and sample report formats saved at `nationaloutreach/reports/cot-report-review-2026-04-30.md`.

## 2026-04-30 Portal COT Actual Report Submissions

- Robert clarified that actual reports should be submitted in Portal, not saved as Markdown copies.
- Submitted three Portal report rows as Codex user `1332` using Salesreport invoice data, Contact Report activity, and the advanced tasting-report pattern:
  - Report `7907`: COT Activity - Quarterly, period 2026-01-01 through 2026-03-31, report date 2026-03-31. Live source metrics: `$407,249.53` invoice value, 248 tastings, 6,949 tasting visitors.
  - Report `7908`: COT Activity - Monthly, period 2026-04-01 through 2026-04-30, report date 2026-04-30. Live source metrics: `$0` invoice value in the queried invoice table, 64 tastings, 3,094 tasting visitors. Linked to Codex report notification `6147841`.
  - Report `7909`: COT Activity - Weekly, Friday-ending window 2026-04-18 through 2026-04-24, report date 2026-04-24. Live source metrics: `$0` invoice value in the queried invoice table, 13 tastings, 337 tasting visitors.
- No separate Markdown report copy was created for this actual-submission pass.
- Follow-up task recorded in National Outreach TODO: after Portal period 2026-04-27 through 2026-05-03 is complete, submit the next weekly COT Activity report via Codex / Vanessa using Portal's own report period. Treat Codex report reminders sent to `codex@kovaldistillery.com` as National Outreach inbox work because that address routes to `nationaloutreach@kovaldistillery.com`.
- Robert corrected the weekly cadence: keep Portal time frames and set the submitter accordingly. Report `7909` was updated from the custom Friday window to Portal weekly period 2026-04-20 through 2026-04-26, report date 2026-04-26, submitter Codex user `1332` / `codex@kovaldistillery.com`; Codex notification row `6147831` is now linked to report `7909`. The next open weekly Codex notification is Portal period 2026-04-27 through 2026-05-03, row `6147832`.
- Robert reported no reviewer notification was received. Root cause: the report rows were created/updated through a DB-only path, which did not run Portal's report-submit notification side effect. A local Portal helper resend attempt created failed `reports.new_for_review` notification-log rows for reviewers because SMTP returned `550 5.7.1 Relaying denied`. Vanessa sent fallback emails with the live report links, first to Robert only, then to Robert with Sonat cc'd; final subject `COT Portal reports submitted for review`, Message-ID `<177757689465.32612.7659277224453039999@kovaldistillery.com>`. Future COT reports must use the real Portal submit/API flow so the report, reviewer notification logs, and reviewer emails happen together.
- Robert clarified the proper correction path: notifications must be triggered through live Portal, not through local helper SMTP. Report review notifications for reports `7907`, `7908`, and `7909` were then triggered through the live Portal `/notifications/send` runtime path; each report returned 4 sent and 0 failed for the current reviewer set. For future cadence, weekly reports should be submitted after the Portal weekly period closes, while monthly and quarterly reports should be submitted a few days after month/quarter end so late-entered Salesreport, Contact Report, and tasting data can be included.

## 2026-04-30 Open-Item Reminders and Calendar Routing

- Robert clarified that recording open inbox items is not enough: the responsible worker persona must email the owner about open/missed/blocked items, include the original source email for review, and create durable follow-up storage plus reminders.
- Shared directive updated in `docs/email-workers/2026-04-30-shared-open-item-owner-email.md`, `worker_roles/send-from-personas.md`, Frank, Avignon, and National Outreach docs. Rule: each reminder/scheduled action needs both an OPS/reasonable task record and a worker-executable scheduled-action or calendar record.
- Calendar reminder routing rule: Frank may use Frank's individual Google Calendar path; Avignon may use Avignon/Sonat's individual Google Calendar path; National Outreach may use the shared National Outreach calendar for Vanessa, Ezra, Naomi, and other shared-inbox personas. Calendar events supplement task state and do not replace OPS/task records. If calendar helper/scope/auth is blocked, log the blocker and use the local scheduled-action runtime.
- Source and installed National Outreach runtime patched at `scripts/nationaloutreach_mail_cycle.py` and `/Users/admin/.nationaloutreach-launch/runtime/scripts/nationaloutreach_mail_cycle.py` to read `/Users/admin/.nationaloutreach-launch/state/scheduled-actions.jsonl`, check due actions, perform optional reply-resolution checks, queue due approved email payloads, and log outcomes in `scheduled-actions-log.jsonl`.
- Active scheduled actions:
  - OPS task `367855`, scheduled-action `vanessa-eataly-sonat-reminder-2026-05-01-1830`, due 2026-05-01 18:30 Central. Checks for Sonat's Eataly reply before emailing Robert.
  - OPS task `367857`, scheduled-action `vanessa-whiskey-cigar-sebastian-reminder-2026-05-02-1830`, due 2026-05-02 18:30 Central. Checks for Sebastian's Whiskey and Cigar Social regulatory reply before emailing Robert.
  - OPS task `367856`, scheduled-action `vanessa-mitch-weekly-draft-2026-05-04-0800`, due 2026-05-04 08:00 Central. Runs the Mitch weekly report approval step at the scheduled time rather than sending separate daily nags.
- Added `nationaloutreach/scripts/build_mitch_weekly_report.php` and changed the Mitch scheduled action to kind `mitch_weekly_report_draft`. At run time, the National Outreach scheduler regenerates the live OPS Outreach Monday-Sunday report and queues the Robert-only approval draft from Vanessa; it does not rely on the older 2026-04-27 preview artifact.
- Live OPS readback confirmed all three tasks are Codex-owned/assigned and have the intended due dates/times with `sendnotification=0`: `367855` due 2026-05-01 18:30, `367857` due 2026-05-02 18:30, and `367856` due 2026-05-04 08:00.
- Calendar verification correction: National Outreach calendar access is verified through the existing OPS-linked calendar path. Frank's/OPS shared Google Calendar helper sees `KOVAL Outreach Events` (`c_ocjnu99l5tpghlvrovtifk1io8@group.calendar.google.com`) with owner access. Created matching calendar reminder events on that calendar:
  - Eataly decision check: event `5u18o5908a85qlkvbouf2lo4a0`, 2026-05-01 18:30 Central.
  - Whiskey/Cigar licensing check: event `0g2m6g52g5ec5ivguvua3k0ekc`, 2026-05-02 18:30 Central.
  - Mitch weekly tastings draft: event `o3ptm0amgvid448k84cicjni1g`, 2026-05-04 08:00 Central.
- PHPList readback correction: use the OPS CRM integration PDO against `koval_plst1`, not the denied `phplist` schema. Campaigns `556` and `557` were sent on 2026-04-30 around 11:17 Central. Both are `status=sent`, linked to list `73`, `processed=18`, with `18` `phplist_usermessage` rows in `sent` status and `bouncecount=0`.
