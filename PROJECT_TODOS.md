# Project TODO Breakdown

Source: `project_list-import.txt`  
Last Updated: 2026-02-27 10:36:44 CST (Machine: Macmini.lan)

## Priority 1 (Stability + Access)

- Fix SSO between OPS and Portal:
  - Reproduce "SSO not working from OPS" and "logged out next day" behavior.
  - Capture session cookie/domain/expiry mismatch details.
  - Define and apply canonical session policy across `/login`, `/ops`, `/portal`.
- Localhost Apache service cleanup:
  - Identify root-owned `httpd` conflicts and launch-agent conflicts.
  - Standardize one local startup path.
  - Confirm env changes are reliably applied.

## Priority 2 (Data Integrity + Audit)

- Portal production audit trails:
  - Add extended modification history for bottling and distillation records.
  - Decide whether picklist-only changes are excluded.
  - Build report for prior-month bottling/distillation edits.
- Bottling reconciliation report:
  - Report mismatches between shipped quantities and bottled quantities.
- Mash grain anomaly report:
  - Flag mashes under `2000 lb` grain.
  - Define grain/product mismatch logic and thresholds.

## Priority 3 (Core Product Work)

- BID ETL pipeline:
  - Define extract sources, transform rules, and load targets.
  - Build repeatable import job and error handling.
- Manage COT team from OPS (Connecteam replacement):
  - Define MVP parity scope (tasks, shifts, notifications, check-ins).
  - Implement in OPS and phase out Connecteam dependency.
- Market module improvements in OPS:
  - Create account/contact flows in OPS.
  - Decide if activity sync to `salesreport` is one-way or two-way.
  - Keep entry-vs-reporting boundaries explicit.

## Priority 4 (Usage, Reporting, Enablement)

- User activity overview:
  - Unified per-user view for Portal, OPS, salesreport, contactreport, BID, automation.
  - Include task stats, shift/check-in stats, and optional Gmail/Gemini admin metrics.
- Salesreport user adoption:
  - Track usage by login and access needs (including Derek/Benjamin Green access details).
- Lists enhancements:
  - DONE 2026-04-14: phpList sent-campaign CRM activity workflow deployed from `/Users/werkstatt/lists` commit `d35aabe1b249052539446b407a8061e00b6b03b0` and live pulled to `/home/koval/public_html/lists`.
  - DONE 2026-04-14: campaign sends can be logged as one account-tied CRM `E-mail` activity per campaign/account, owned by campaign owner, idempotent via `koval_plst1.phplist_koval_send_activity` unique `(messageid, accountid)`.
  - DONE 2026-04-14: sent campaign rows expose `Log CRM E-mail Activities`, which opens a dry-run preview before confirmed `Create CRM Activities`; no campaign send or phpList list-membership change is part of this flow.
  - DONE 2026-04-14: active, non-deleted CRM users with role `Sales Manager` have mapped phpList non-superuser access; Jamie was removed from phpList Full Access.
  - DONE 2026-04-14: first apply for campaign `545` created `87` CRM E-mail activities and `87` tracking rows after Robert confirmed `KOVALTEST`/`Test123` were acceptable; follow-up dry-run returned `0` pending candidates.
- Trainual/video documentation:
  - Record market event workflow and day-to-day usage tutorials.
  - Create manual for barrel sample page.

## Priority 5 (Operations + Recurring Tasks)

- Systems usage cadence:
  - Monthly importer roster update check.
  - Distributor inventory recurring check/send.
  - Monthly task stats send-out (dashboard recurring task).
  - Market Events / Events / Task Stats monthly review.
  - PHPList, Shopify, Square signup stats review.
  - Monthly/quarterly warehouse + distribution sales reports.
  - BID info refresh cycle.

## Priority 6 (External/Platform Integrations)

- Advertising + analytics:
  - Resolve Google Ads issues.
  - Implement web analytics funnel reporting for `koval-distillery.com`.
- IT governance docs alignment:
  - Review/update:
    - `https://papers.koval/teams/it/task-queue.html`
    - `https://papers.koval/teams/it/roadmap.html`
    - `https://papers.koval.lan/teams/it/dashboard.html`
  - Decide on GitLab removal/transfer plan.

## Priority 7 (Security Program)

- Google Cloud credential hardening:
  - Inventory all service account keys and API keys.
  - Remove dormant keys (>30 days inactivity).
  - Enforce API restrictions (API + referrer/IP/bundle scopes).
  - Apply least-privilege IAM reduction.
  - Enforce key rotation/expiry policy.
  - Consider disabling new user-managed SA key creation.
  - Validate Essential Contacts and billing anomaly/budget alerts.

## Open Decisions Needed

- Should these be merged into `TODO.md` now, or tracked in this file as a staging backlog first?
- What are the top 3 items to start this week?
- For the audit trail scope, should picklist-only changes be excluded by default?
- For OPS <-> salesreport data flow, should OPS be canonical source of entry data?
- Should Google Cloud security hardening be treated as its own incident/project hub initiative?
