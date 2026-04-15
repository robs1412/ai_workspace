# TODO — avignon

Updated: 2026-04-15 16:58:00 CDT (Machine: Macmini.lan)

## In Progress

- Email-derived decision/work items:
  - `avignon-new-hire-training-template-reference-2026-04-12`: Sonat sent a new-hire training email template/reference. Logged for Avignon future use and acknowledgement prepared/sent.
- Initial Avignon setup:
  - scaffold workspace files and operating rules
  - add Avignon to launcher/docs and Workspaceboard
- Follow up with Sonat on Angele inbox cleanup direction.
  - OPS/Portal task ID: `366462`
  - Due: `2026-04-12`
  - Context: Avignon emailed Sonat on 2026-04-10 with Frank/Codex cleanup session `56fd7397`, latest Angele counts, preserved categories, and the request to tell Avignon how to proceed.
  - Sonat responded on 2026-04-11: keep preserving the listed categories and focus on remaining hits for Abby, Jordan, and the marketing alias. Routed into Frank TODO as an Angele cleanup follow-up.

## Done

- Sent Sonat an Avignon morning overview on 2026-04-15 at 16:54 CDT, matching Robert's Frank overview format at a safe summary level; sent-log task id `avignon-morning-overview-2026-04-15`.
- Closed Sonat business-card CRM additions follow-up on 2026-04-15: Avignon worker `e9588b48` and importer worker `10b9346d` completed/reviewed import `52`, creating account IDs `366780`, `366784`, `366786`, `366789` and contact IDs `366781`, `366782`, `366783`, `366785`, `366787`, `366788`, `366790`; 7/7 account-contact links verified and private fields were not printed.
- Installed Avignon-specific 5-minute LaunchAgent scheduler on 2026-04-14: `com.koval.avignon-auto` runs every 300 seconds from `/Users/admin/.avignon-launch`, uses a machine-local Avignon credential reference, and logs runtime state locally to avoid synced Google Drive launchd/TCC failures. Verified launchd last exit code `0` and a clean inbox cycle with `0` messages.
- Marked `avignon-google-account-security-notifications-2026-04-12` handled/filed after Robert confirmed on 2026-04-13 that the 2026-04-12 Google account/security/device-management notifications were expected/OK. No Google admin/account action was taken.
- Handled Avignon inbox-cleaning pass on 2026-04-12: sent barrel personalization guidance to Sonat, acknowledged the new-hire training-template reference, routed the LJ Hospitality/Jamie Gilmore CRM attachment request to `EMAIL_DERIVED_DECISIONS.md`, and archived handled/routed source mail to `Handled`.
- Completed `avignon-crm-lj-hospitality-jamie-gilmore-2026-04-12` after Sonat approved by email: created the CRM account/contact link and prepared/sent a completion note to Sonat. No attachment contents were logged.
- Added Avignon profile support to the shared local sender plus explicit helper `scripts/send_avignon_email.py`: default Sonat audience guard, Avignon credential path, Avignon sent log, Avignon From/signature defaults, and README dry-run/send usage. Verification was dry-run/help/syntax only; no mail was sent.
- Logged Sonat's 2026-04-12 reply approving Avignon task-flow Option A, with digest/audit trail. Sent acknowledgement to Sonat with task id `avignon-task-flow-option-a-ack-2026-04-12` and archived the source reply to `Handled`.
- Recorded Robert's 2026-04-12 approval for medium-independent Frank/Avignon task flow: clearly bounded low-risk internal email tasks can be ingested, routed, executed, logged, and filed without waiting in the inbox; higher-risk/ambiguous categories still require approval.
- Checked MacMini Avignon mailbox/logs on 2026-04-11; Sonat's reply to `Avignon persona blurb` was received at 15:19 CDT, incorporated into `PERSONA.md`, and Avignon sent Sonat `Avignon task-flow decision options` at 18:14 CDT with task id `avignon-decision-options-task-flow-2026-04-11`.
- Routed Sonat's 2026-04-11 reply on the barrel buyer re-engagement list to Salesreport worker `a7a6d9f5`; Salesreport completed the cleaned review list and Avignon sent the completion notice to Sonat.
- Started Avignon persona/reference file at `PERSONA.md`; Sonat persona-blurb outreach was sent from Mac mini on 2026-04-11 with task id `avignon-2026-persona-blurb` after duplicate checks.
- Intro email sent from `Avignon.rose@kovaldistillery.com` to `sonat@kovaldistillery.com` with `robert@kovaldistillery.com` copied on 2026-04-10 after app-password refresh.
- Angele cleanup progress email sent from `avignon.rose@kovaldistillery.com` to `sonat@kovaldistillery.com` on 2026-04-10, referencing OPS/Portal task `366462` and Codex session `56fd7397`.
- Mirrored Frank's scheduled inbox loop guard into the shared runner configuration path for Avignon: Sonat replies to `Avignon inbox review...` and tracked `*-auto-escalation` review replies should be logged as local follow-up instead of being re-escalated, while Avignon self-mail should be logged with no action.

## Backlog

- Mirror relevant Frank workflow improvements into Avignon when operationally useful.
- Establish Avignon mailbox triage, task, and follow-up conventions for Sonat.
