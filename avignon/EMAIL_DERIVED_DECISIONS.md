# Email-Derived Decisions — avignon

Updated: 2026-04-19 10:03 CDT (Machine: Macmini.lan)

## Open

- `avignon-sonat-crm-intake-recovery-2026-04-17`
  - Needed: Ten Sonat-originated Avignon messages on 2026-04-17 with CRM-addition subjects were archived to `Handled` after generic `avignon-email-review-*` logging, without visible CRM/import routing or completion confirmation. Recovery execution has now completed all deterministic non-ambiguous CRM work: Importer session `86dc0b04` completed Import ID `56` for the 5 importer-safe rows, and Portal session `44b8a370` completed source `9` and source `5`.
  - Next: Action-plan review completed 2026-04-19 and recorded at `drafts/avignon-crm-recovery-action-plan-review-2026-04-19.md`. Do not route further Portal/Importer mutation unless the exact target answers are supplied. Do not send the existing source-heavy private answer-sheet draft as-is.
  - Decision: Safe resolution is not possible from the currently recorded context. Source `1` remains blocked on target-account plus duplicate/existing-contact ambiguity; source `10` remains blocked on distributor/account ambiguity; source `7` is held as status/update-only for final closeout. If Robert approves another follow-up, send one concise Avignon note to Sonat with Robert copied for visibility using only this exact answer format: Source `1` target account or `create new`; Source `1` existing contact record to link/update or `create new`; Source `10` distributor/account or `create new`; Source `7` include as status/update-only in final closeout yes/no. Frank owner-path report `frank-avignon-crm-recovery-corrected-path-2026-04-19` was sent to Robert with Message-ID `<177661098259.95485.12446032407156880410@kovaldistillery.com>`. Prior Sonat status/current-state/decision emails were sent under task ids `avignon-sonat-crm-intake-recovery-2026-04-17-status-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-follow-up-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-current-state-2026-04-18`, and `avignon-sonat-crm-intake-recovery-2026-04-17-target-link-decisions-2026-04-18`; the last Sonat email is now treated as a quality issue, not the current waiting state.
- `avignon-email-review-lander-journal-your-input-needed-on-brand-voice-section-name`
  - Needed: Consolidated Lander Journal brand-voice/section-name thread review item. Earlier timestamped items for this same thread were duplicates created by the decision-email loop.
  - Next: Keep one local review item only; do not email Sonat again unless a fresh approval boundary is identified.
  - Decision: Determine internally whether Avignon can route/answer/file this thread, or escalate one concrete question if genuinely blocked.
## Waiting On Sonat Email

No current Avignon email-derived items are waiting on Sonat email approval from Avignon inbox.

## Routed / Handled

- `avignon-email-review-new-automated-social-media-content-pipeline-instagram-facebo`
  - Needed: Claude/Robert social media pipeline thread reported an internal Instagram/Facebook draft-generation workflow and ended with the pipeline ready when needed.
  - Next: Filed the 3 current inbox messages to `Handled`; no posting, account connection, approval, external send, credential, or production action was taken by Avignon.
  - Decision: Handled as an internal readiness/status thread; future generated social drafts still require normal content/approval guardrails before publication.

- `avignon-google-ads-task-1317-approval-2026-04-17`
  - Needed: Google Ads task #1317 remains owned by the Claude/Sonat owner path and involves spend/account approval outside Avignon's authority.
  - Next: Filed the 6 current inbox residue messages to `Handled` after confirming no fresh Avignon action was needed. Avignon must not activate, configure, spend, or close Google Ads work.
  - Decision: Routed/handled for Avignon; any remaining campaign approval belongs in the Claude/Sonat thread, not as an Avignon inbox blocker.

- `avignon-email-review-google-ads-1-000-credit-current-state-action-needed`
  - Needed: Google Ads credit/current-state item may involve advertising account/spend decisions.
  - Next: Routed ownership to Claude and Sonat; Avignon must not take spend, account, admin, or configuration action.
  - Decision: Robert confirmed on 2026-04-17 that ownership is Claude and Sonat.

- `avignon-decision-email-loop-cleanup-2026-04-16`
  - Needed: Avignon generated repeated timestamped decision items and emails for the same Lander Journal thread, including replies to Avignon's own decision-needed messages.
  - Next: Runtime patched to suppress decision-email replies, dedupe ambiguous reviews by stable subject key, and record local decision items without sending Sonat email unless explicitly enabled.
  - Decision: Loop artifacts consolidated/handled; source inbox was already empty at manual verification.

- `avignon-email-review-20260415035142-crm-tasks`
  - Needed: Sonat followed up asking whether Avignon had completed the CRM additions request.
  - Next: Avignon completed the CRM additions via Importer board session `10b9346d` and sent Sonat a concise completion update.
  - Decision: Handled under the approved low-risk internal CRM-addition task flow.
- `avignon-email-review-20260414160440-crm-additions`
  - Needed: Sonat asked Avignon to add Boston vendor-lead CRM accounts and associated contacts from a text-only email; no normal attachment payload was present.
  - Next: Importer board session `10b9346d` created Import ID `52`, four accounts, and seven contacts, with account-contact verification `7/7`.
  - Decision: Completed under the approved low-risk internal CRM-addition task flow; no email body or contact values logged here.
- `avignon-google-account-security-notifications-2026-04-12`
  - Needed: Avignon inbox received Google account/security and device-management notifications. These touched account access/security, so they were held for Robert or approved admin verification.
  - Next: No Google admin/account action from Avignon. Treat the source notifications as handled/filed.
  - Decision: Robert confirmed on 2026-04-13 that the 2026-04-12 notifications were expected/OK.
- `avignon-email-review-20260412194954-re-approval-needed-lj-hospitality-jamie-gilmore-crm-entry`
  - Needed: Sonat replied to the LJ Hospitality / Jamie Gilmore approval-request email.
  - Next: Avignon treated the reply as approval and completed the CRM write.
  - Decision: Approval reply handled.
- `avignon-crm-lj-hospitality-jamie-gilmore-2026-04-12`
  - Needed: Sonat asked Avignon to create a CRM account for LJ Hospitality Group and add Jamie E. Gilmore as a contact attached to that account. Robert required explicit Sonat email approval before the write.
  - Next: Sonat approved by email; Avignon created the account/contact link and sent a completion note to Sonat.
  - Decision: Completed after Sonat email approval.
- `avignon-barrel-personalization-guidance-2026-04-12`
  - Needed: Sonat asked how to personalize the barrel re-engagement emails.
  - Next: Avignon sent guidance explaining the account-note or general-rule path and confirmed draft-only handling until send approval.
  - Decision: No approval needed for this guidance reply.
- `avignon-new-hire-training-template-reference-2026-04-12`
  - Needed: Sonat sent a new-hire sample training email/template for Avignon to keep ready for future use.
  - Next: Avignon logged the template-reference work item and acknowledged receipt to Sonat.
  - Decision: No approval needed for this internal reference capture.
