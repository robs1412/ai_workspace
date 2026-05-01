# National Outreach TODO

## Open

- Mitch Conti weekly upcoming tastings report is approval-gated.
  - Robert received the review-copy report on 2026-04-27 from National Outreach. Do not send to Mitch until Robert gives explicit go-ahead after review.
  - Requested future recipient after approval: `"Conti, Mitch" <Mitch.Conti@rndc-usa.com>`, cc Robert.
  - Cadence after approval: every Monday at 8:00am, upcoming tastings for that week.
  - 2026-04-30 Robert clarified this should not be a daily nag. OPS task `367856` and scheduled-action id `vanessa-mitch-weekly-draft-2026-05-04-0800` are set for Monday 2026-05-04 at 08:00 Central so Vanessa/National Outreach runs the draft/approval step at the scheduled time.
  - The scheduled action uses `nationaloutreach/scripts/build_mitch_weekly_report.php` to regenerate the live OPS Outreach Monday-Sunday report before emailing Robert the approval draft; it is not a static placeholder.
  - Calendar reminder: `KOVAL Outreach Events` event `o3ptm0amgvid448k84cicjni1g` at 2026-05-04 08:00 Central.

- Whole Foods portal -> OPS Outreach sync directive is active.
  - Import only buyer-approved Whole Foods events. Pending/not-approved portal items must be noted but not imported as confirmed OPS events.
  - WFM tasting requests should remain Bourbon-only in the account-facing request unless explicitly approved otherwise; internal COTeam notes and taster reminders should include suggested additional samples from recent account sales when available, including what sold and when it was last sold.
  - 2026-05-01 Robert clarified not to overbuild this: the chain report / Salesreport Chain Store Intelligence page is already sufficient for the reminder use case. The point is to give tasters a practical idea of what products accounts carry so they bring the right samples/materials.
  - Vanessa job recorded as OPS task `367872` / `Vanessa: add product-carry notes to tasting reminders`, due 2026-05-01, owner/assignee Codex user `1332`, creator Robert user `1`, `sendnotification=0`.
  - Credential blocker resolved: `.private/logins/wholefoods.txt` is present and a private authenticated portal crawl succeeded.
  - 2026-04-27 first approved import complete for approval email Request `312022`: OPS events `857`-`862`, linked shifts `5184`-`5189`.
  - 2026-04-27 coverage recheck complete: 42/42 WFM portal rows are in OPS, 0 missing, 42/42 have linked Outreach shifts, 28 fully assigned, 14 open/unassigned. Final HTML-table report with 14 light-red open/unassigned rows sent to Sonat and Robert from National Outreach.
  - Future WFM coverage reports should use `templates/whole-foods-ops-coverage-report.md`.
  - Remaining open sync work: future refreshes for April-June requests `310465`, `310468`, `310470`, and `310472`; these remain not approved/pending and must not be imported until approval evidence exists.
  - 2026-04-30 WFM Request `312318` completed through visible Workspaceboard OPS session `4e555ea9` (`OPS WFM Request 312318 import/reconciliation`). OPS imported seven approved KOVAL Bourbon rows as events `869`-`875` with linked shifts `5300`-`5306`.
  - Directive: `WHOLE_FOODS_TASTING_PLANNING.md`; project log: `../project_hub/issues/2026-04-27-whole-foods-ops-sync.md`.

- Vanessa / COT May schedule emails need routing.
  - 2026-04-29 Robert forwarded `Fwd: COT Team` to `vanessa.sterling@kovaldistillery.com`, cc Sonat, asking Vanessa to email individual COT team members who are scheduled for May so far.
  - 2026-04-29 correction from Robert: broad staff mailings like "email everyone for May" must be built/sent through PHPList in `/Users/werkstatt/lists`, not as individual National Outreach mailbox sends.
  - Live OPS readback found 14 assigned COT staff with May 2026 Outreach shifts. Vanessa should ask Robert blocker questions first, then route the approved mailing packet to `/lists` for PHPList audience/campaign handling.
  - 2026-04-30 routed to visible Workspaceboard Lists session `d220b31d` (`Lists Vanessa COT May staff mailing packet`) for PHPList packet/draft handling; send remains approval-gated.
  - 2026-04-30 correction: Robert flagged that Vanessa had not emailed him about the drafts. Vanessa sent Robert the review note with draft IDs `556` and `557`, Message-ID `<177756302444.77440.9233654883041090067@kovaldistillery.com>`.
  - 2026-04-30 follow-up: Vanessa sent Robert the full then-current draft bodies for `556` and `557` plus the phpList personalization explanation, Message-ID `<177756318419.77683.1657624334383249648@kovaldistillery.com>`.
  - 2026-04-30 correction/readback: use the OPS CRM integration PDO against `koval_plst1`, not the denied `phplist` schema. Campaigns `556` and `557` were sent on 2026-04-30 around 11:17 Central. Both are `status=sent`, list `73`, `processed=18`, and `bouncecount=0`.

- Vanessa / Consumer Outreach schedule follow-through needs OPS routing.
  - 2026-04-30 private review metadata shows Robert's `Fwd: 5-10 shift switch` to Vanessa and Claude's `Consumer Outreach Events - Schedule Confirmation`; both route to Outreach Coordinator.
  - Task Manager was instructed on 2026-04-30 to create/reuse the correct OPS/Outreach worker, verify live OPS state before any mutation, apply routine complete shift/schedule changes only when the packet is complete, and otherwise surface one concrete blocker.
  - 2026-04-30 correction: Robert flagged that Vanessa had not emailed him. OPS readback found Kevin McCarthy assigned to Mariano's Westchester on 2026-05-10, 2:00-5:00 PM, with the May 10 Schaumburg shift found in OPS open/unassigned. Vanessa sent Robert the first Kevin draft for confirmation in Message-ID `<177756302444.77440.9233654883041090067@kovaldistillery.com>`. Do not email Kevin until Robert confirms the draft.
  - 2026-04-30 Robert approved emailing Kevin and keeping Robert cc'd. Vanessa sent Kevin the confirmation, cc Robert, Message-ID `<177756318523.77683.12080747380140171382@kovaldistillery.com>`.
  - Do not expose private mailbox bodies in board notes. Use source metadata and OPS readback only.

- Eataly May tasting-calendar response is open.
  - 2026-04-30 inbox sweep found Eataly Chicago asking what May tasting dates KOVAL can help with. This is an external account reply and should be handled through Vanessa/Outreach after checking OPS staffing capacity and owner preference; do not auto-commit dates without approval.
  - 2026-04-30 Vanessa emailed Robert for a decision, Message-ID `<177758333004.82358.6154635019640039816@kovaldistillery.com>`.
  - 2026-04-30 Robert asked Vanessa to resend with the actual dates included. Vanessa resent the decision note with the Eataly May date options, Message-ID `<177758663983.96692.14146850970270087421@kovaldistillery.com>`. Source filed to `Archive`; wait for Robert's next decision before replying to Eataly.
  - 2026-04-30 Robert copied Sonat and said Sonat should decide; wait for Sonat's response before replying to Eataly.
  - 2026-04-30 correction: Vanessa sent the internal decision note to Sonat and Robert together, Message-ID `<177760427847.6647.4747216382838959523@kovaldistillery.com>`. No external Eataly reply should be sent until Sonat chooses dates or asks for OPS-supported options.
  - 2026-04-30 Sonat replied at 22:00 Central asking Vanessa to cross-reference Eataly's open May tasting slots against team availability and report whether KOVAL can accommodate one or more slots. The 60-second runner picked it up at 22:01, but the legal-disclaimer text in Sonat's footer caused a false `ezra-katz` classification. Runtime/source classifier patched to route active-message tasting/date replies to `outreach-coordinator`; task-flow event corrected to `working` on OPS task `367855`. No external Eataly reply sent yet.
  - 2026-05-01 correction: live INBOX/sent-log readback showed no external Eataly response and no internal availability readback had been sent after Sonat's reply. Vanessa checked OPS COTeam assigned shifts and recorded unavailable time for every Eataly May window, then replied internally to Sonat with Robert copied. Every slot has at least 9 practical available staff excluding Sebastian. Message-ID `<177764436215.67020.7909395243028385833@kovaldistillery.com>`. External Eataly reply remains gated until Sonat chooses the dates to offer.
  - 2026-05-01 Robert asked how much Eataly ordered in the last year, broken down by month. Vanessa queried Salesreport CRM invoices for Eataly Chicago account `36990`, 2025-05-01 through 2026-04-30, and replied internally to Robert with Sonat copied. Readback: `$4,084.08`, 218 bottles, 9 invoices; last invoice 2026-03-31. Message-ID `<177764500578.70153.8505670869853151279@kovaldistillery.com>`. External Eataly reply remains gated until Sonat/Robert choose dates to offer.
  - 2026-05-01 Robert approved requesting three good dates in the second half of May. Vanessa replied externally to Eataly, cc Philippe, offering Thursday May 28 4-7 PM, Friday May 29 4-7 PM, and Saturday May 30 12-3 PM or 3-6 PM. Message-ID `<177764586042.73937.15837486335137527806@kovaldistillery.com>`.
  - Follow-up state: waiting on Eataly confirmation. Scheduled-action id `vanessa-eataly-date-confirmation-followup-2026-05-04-1000` is set for Monday 2026-05-04 at 10:00 Central and checks for an Eataly reply before reminding Robert.
  - Reminder storage: OPS task `367855` plus scheduled-action id `vanessa-eataly-sonat-reminder-2026-05-01-1830` are set for 2026-05-01 at 18:30 Central. The scheduled action checks for Sonat's Eataly reply first; if resolved, it logs a skip instead of emailing Robert.
  - Calendar reminder: `KOVAL Outreach Events` event `5u18o5908a85qlkvbouf2lo4a0` at 2026-05-01 18:30 Central.

- LSRCC Summer Concert Series sponsorship is closed/no-action.
  - 2026-04-30 inbox sweep found an LSRCC sponsorship opportunity for Thursday evening concerts from 2026-06-11 through 2026-08-13, with $150-$1,500 sponsorship options and a 2026-05-10 maximum-exposure deadline. This needs a business/marketing spend decision before any response.
  - 2026-04-30 Vanessa emailed Robert for a decision, Message-ID `<177758333098.82358.9266946590112263793@kovaldistillery.com>`.
  - 2026-04-30 Robert asked Vanessa to forward the original. Vanessa sent Robert the original/summarized sponsorship item, Message-ID `<177758664076.96692.4248234058994302032@kovaldistillery.com>`.
  - 2026-04-30 Robert replied that Vanessa can file this one. No external response or sponsorship action is pending.

- Naomi QuickBooks/BID access setup is closed; first useful finance work is now open.
  - Robert confirmed Naomi now lands in the KOVAL QuickBooks company.
  - Credential record remains private at `.private/logins/quickbooks-naomi-stern.txt`; do not print the password in chat/logs/docs.
  - OPS setup follow-up task `367841` / `Follow up: Naomi QuickBooks invite acceptance` was silently marked `Completed` with `sendnotification=0` on 2026-04-30.
  - Robert redirected Portal/BID login setup: use the general Codex user for BID/OPS work for now instead of creating/activating a Naomi Portal/login user.
  - New OPS work task `367854` / `Naomi QuickBooks current A/P and A/R packet`, due 2026-05-01, owner/assignee Codex user `1332`, creator Robert user `1`, status `Not Started`.
  - Visible BID worker session `21cea790` / `Naomi QuickBooks first finance packet` is started for this deliverable.
  - Robert narrowed the first useful deliverable: start with current A/P and A/R only. Capture Accounts Payable aging/current state, Accounts Receivable aging/current state, exact QuickBooks report names Naomi should export/confirm, the date/period to use, secure BID landing/handoff path, and top blockers/questions. Do not broaden into P&L, Balance Sheet, banking, payroll, vendor changes, money movement, or accounting/tax decisions until A/P and A/R are captured.
  - First request draft for Naomi is at `nationaloutreach/drafts/naomi-qb-ap-ar-request-2026-04-30.txt`; send only after Robert approves the internal send path/recipients.
  - 2026-04-30 correction: Naomi should extract the A/P and A/R data from QuickBooks and email Robert the readout. UI login automation is blocked by Intuit sign-in/challenge behavior, so the active next path is read-only QuickBooks Online Accounting API setup for `AgedReceivables` and `AgedPayables`; BID session `21cea790` was updated to prepare the OAuth/API setup packet and Naomi-to-Robert output path.
  - Robert-owned OPS task `367858` / `Set up QuickBooks API for Naomi A/P and A/R reports` was created due 2026-04-30 with detailed setup notes. Today UI retry reached valid SMS MFA, then blocked at Intuit passkey setup because the `Skip` button stayed disabled in headless Chrome; headed Chrome cannot run from this service session. Durable path remains API setup.
  - 2026-04-30 follow-up: Robert pointed out the `Skip` button is present; forced skip worked after valid MFA. QuickBooks opened as Naomi and current A/R and A/P Aging Summary reports were exported to private files under `.private/finance/qbo-ap-ar-2026-04-30/exports/`. A/R total `$361,861.67`; A/P total `$26,694.27`.
  - Reusable login/export runbook recorded in BID: `/Users/werkstatt/bid/data-management/finance-action-reports/QBO-NAOMI-LOGIN-EXPORT-RUNBOOK.md`.
  - Final copied BID files include A/R, A/P, Balance Sheet, and verified April-only P&L PDFs/XLSX files in `/Users/werkstatt/bid/intelligence/finance/{ar,ap,balancesheet,profitloss}/`.

- National Outreach specialist classifier routing is active.
  - 2026-04-30 correction: source and installed runtime now route finance-operations/cash-controls/payables/receivables/month-end/reconciliation items to `naomi-stern`, and special-project/legal-affairs/document-follow-through/counsel-ready business packet items to `ezra-katz`.
  - 2026-04-30 correction: classifier now strips quoted replies and `Confidentiality Notice:` footer text before applying route patterns, preventing ordinary legal-disclaimer boilerplate from overriding active tasting/date content into `ezra-katz`.
  - Security Guard still takes priority for credentials, OAuth/tokens, 2FA, bank/routing data, urgent payment pressure, private IDs, or suspicious requests.
  - Naomi and Ezra routes are advisory/triage only; no external legal/regulatory reply, money movement, finance-record mutation, or live-system mutation without separate approval and proper workspace routing.

- Ezra Monday Google Doc status email reminder is active.
  - OPS task `367840` is set for Monday 2026-05-04 at 08:00 Central: Ezra should email Robert and Sebastian Saller with the current status and top 5 things to do from the Google Doc source.
  - Recipients: `robert@kovaldistillery.com` and `sebastian.saller@kovaldistillery.com`.
  - Source: `https://docs.google.com/document/d/1-2l-SAn1T8qVEKeFbPDgKiIEKDIYzppHjWoCR3b-c1g/edit?tab=t.0#heading=h.achbmitssp54`.
  - Task is Codex-owned/assigned because Ezra does not currently exist as an OPS/Portal user in the live user lookup. Use Ezra's National Outreach send-from persona when executing.

- Portal COT reports via Codex/Vanessa need recurring submission follow-through.
  - Portal user `1332` / Codex now has `codex@kovaldistillery.com`, routed to the National Outreach inbox. Treat Portal report reminder mail for Codex as National Outreach / Vanessa COT report intake.
  - Reports must be submitted in Portal, not just sent as Markdown/email attachments.
  - Submission path rule: use Portal's real submit/API flow so the report row, reviewer notification log, and reviewer email are created together. Do not use DB-only report inserts/updates for future submissions; they skip Portal notification side effects.
  - Notification trigger rule: if a notification must be resent or triggered after the fact, call the live Portal runtime/API notification path. Do not use local PHP helper SMTP from the worker shell; it can render the email but may fail relay outside the Portal production runtime.
  - Use Salesreport invoices, Contact Report activity, and the advanced tasting-report pattern for actual report content.
  - Use Portal's own report periods. Do not create custom Friday-ending windows unless Portal itself creates that period.
  - Next action: after Portal period 2026-04-27 through 2026-05-03 is complete, submit that weekly COT Activity report as Codex / Vanessa and link the Codex notification row.
  - Ongoing cadence: submit weekly COT reports after the Portal weekly period closes. Submit monthly and quarterly reports a few days after the last day of the month/quarter so Salesreport, Contact Report, and tasting data have time to be entered.
  - Current completed Portal report ids: quarterly Q1 2026 `7907`, monthly April 2026 `7908`, weekly Portal period 2026-04-20 through 2026-04-26 `7909`.
  - 2026-04-30 notification correction: direct DB submission created the reports but did not trigger reviewer emails. A local Portal helper resend attempt created failed `reports.new_for_review` notification-log rows because SMTP returned `550 5.7.1 Relaying denied`; Vanessa sent fallback link emails, first to Robert only, then to Robert with Sonat cc'd, final Message-ID `<177757689465.32612.7659277224453039999@kovaldistillery.com>`.
  - 2026-04-30 live Portal notification correction: report review notifications for reports `7907`, `7908`, and `7909` were triggered through the live Portal `/notifications/send` runtime path; each report returned 4 sent and 0 failed for the current reviewer set.

## Done

- 2026-05-01: Cleared the 11-message National Outreach active INBOX set after body review, required sends, and follow-up storage. Sent Eataly second-half May options, Sebastian permit-path acknowledgement, and Robert's Christine/OPS manual readback; filed the reviewed active messages out of INBOX; final runtime poll reported `mailbox_total=0`, `active_inbox_count=0`.
- 2026-05-01: Implemented Vanessa's standing tasting-prep job: use Salesreport Chain Store Intelligence / Chain Invoice Report as the practical product-carry source for taster reminders and internal COTeam prep notes. Created and silently completed OPS task `367872` with creator Robert (`1`), owner/assignee Codex (`1332`), due `2026-05-01`, `sendnotification=0`. Updated the Monday Mitch weekly tastings generator so its output has a `Product / sample prep` column and strips Connecteam import tags from staff-facing guidance. Added `templates/taster-reminder-product-carry.md` for direct staff reminder wording. This is reminder/sample guidance only; do not overbuild scraper comparison for the ordinary taster-reminder use case.
- 2026-05-01: Hardened National Outreach active INBOX polling. Seen messages that remain in INBOX are now counted and surfaced on every cycle, tracked in private `active-inbox.json`, and marked resolved only after they leave INBOX. Verified no-send manual polls: `mailbox_total=11`, `active_inbox_count=11`, `seen_inbox_active_count=11`; second poll kept the same active count while suppressing duplicate full review rows.
- 2026-05-01: Recorded the Illinois tasting compliance directive from Sebastian's guidance, verified National Outreach Drive access to the linked policy/SOP docs, sent Vanessa's reply to Sebastian with Robert and Sonat copied, filed Sebastian's source message to `Archive`, and completed OPS reminder task `367857`. Corrected the directive afterward: regular retail tastings such as Binny's, Mariano's, Whole Foods, and similar ordinary account tastings do not need Sebastian notification solely because a tasting is happening.
- 2026-04-27: Created local National Outreach worker folder and persona for `nationaloutreach@kovaldistillery.com`; private mailbox setup verified separately without reading bodies or sending mail.
- 2026-04-27: Imported approved Whole Foods Request `312022` into OPS Outreach from Robert-supplied approval email evidence; created six event bookings and six unassigned Outreach shifts; linked CRM accounts and KOVAL Bourbon product where deterministic.
- 2026-04-27: Sent Binny's OPS coverage report to Robert: 39/39 in OPS, 0 missing, 39/39 linked shifts, 38 fully assigned, 1 open/unassigned (`Binny's Joliet`, 2026-05-30 4pm-7pm). Saved reusable Whole Foods and Binny's HTML-table report templates.
