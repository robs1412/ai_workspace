# National Outreach Handoff

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
