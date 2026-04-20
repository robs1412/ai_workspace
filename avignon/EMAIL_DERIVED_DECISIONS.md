# Email-Derived Decisions — avignon

Updated: 2026-04-20 16:00 CDT (Machine: Macmini.lan)

## Open

- `avignon-email-review-crm-addition-and-activity-update-requested`
  - Needed: Sonat sent a direct CRM/activity request that Avignon filed to `Handled` after generic ambiguous-review logging. Source Message-ID `<CALbLtzx71n0bqs1_GJ+7WvDgt6jxNC5Wwi9tQRpq2X5rZh2nzg@mail.gmail.com>`.
  - Next: Waiting on Robert to approve bounded source-detail recovery or on Robert/Sonat to provide a human-readable target table before any Portal/CRM write.
  - Decision: Session `8ef5557d` blocked this source because approved non-secret metadata lacks deterministic account/contact/activity target, field payload, activity date/type/content, existing-record match, and dedupe key. Sonat blocker report sent 2026-04-20, subject `CRM/activity recovery blocked: source details needed`, Message-ID `<177670759491.94577.6982548554446206105@kovaldistillery.com>`, draft `drafts/sonat-crm-activity-recovery-blocker-2026-04-20.txt`. Robert human-readable correction sent 2026-04-20, Message-ID `<177670777142.96602.16061256851726520967@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-human-readable-details-needed-2026-04-20.txt`. Robert source-detail path sent 2026-04-20, Message-ID `<177671017432.9834.12022155147795059@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-source-detail-path-2026-04-20.txt`; it treats original mailbox source-detail recovery as approval-gated. No CRM/Portal/OPS mutation occurred.

- `avignon-email-review-crm-addition`
  - Needed: Four April 20 Sonat direct CRM-addition messages were filed to `Handled` as duplicate ambiguous review without proper acknowledgement/status. Source Message-IDs `<CALbLtzyPwnuk=Msw0wgFtDsOEnNk5QhiD+E9ZP7tRuqQouKDgw@mail.gmail.com>`, `<CALbLtzxSioFqgNL61KHSHVxVu9ZSnYGujC3YeS-j+OBPs+v4Yw@mail.gmail.com>`, `<CALbLtzxCAaOdQZohyM0m67A6mCWbbMCjTSOaMTi7W+RR2k3_2Q@mail.gmail.com>`, and `<CALbLtzzm--wq-DqFsW8ePfVEAsgKAuiH1-gpB7Tehb=VUUDULg@mail.gmail.com>`.
  - Next: Waiting on Robert to approve bounded source-detail recovery or on Robert/Sonat to provide human-readable target tables before any Portal/CRM write.
  - Decision: Session `8ef5557d` blocked these four sources because approved non-secret metadata lacks deterministic account/contact/activity targets, field payloads, existing-record matches, and dedupe keys. Sonat blocker report sent 2026-04-20, subject `CRM/activity recovery blocked: source details needed`, Message-ID `<177670759491.94577.6982548554446206105@kovaldistillery.com>`, draft `drafts/sonat-crm-activity-recovery-blocker-2026-04-20.txt`. Robert human-readable correction sent 2026-04-20, Message-ID `<177670777142.96602.16061256851726520967@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-human-readable-details-needed-2026-04-20.txt`. Robert source-detail path sent 2026-04-20, Message-ID `<177671017432.9834.12022155147795059@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-source-detail-path-2026-04-20.txt`; it treats original mailbox source-detail recovery as approval-gated. No CRM/Portal/OPS mutation occurred.

- `avignon-email-review-ai-generated-bottle-images-policy-clarification-needed`
  - Needed: Avignon received an email that was not clearly safe to auto-handle. Subject: `Re: AI-generated bottle images -- policy clarification needed`.
  - Next: Review only in the approved mailbox/workspace context and decide whether to route, reply, or hold.
  - Decision: Confirm the owner/action for this email-derived item; do not send Sonat a generic review prompt unless a real Sonat decision remains.

- `avignon-email-review-add-activity-to-crm`
  - Needed: Sonat sent a direct CRM activity request that Avignon filed to `Handled` after generic ambiguous-review logging. Source Message-ID `<CALbLtzx03Rzzqnn1M+0yZifY6-4YfQeekeVgK3+zKyQQbN0JCQ@mail.gmail.com>`.
  - Next: Waiting on Robert to approve bounded source-detail recovery or on Robert/Sonat to provide a human-readable target table before any Portal/CRM write.
  - Decision: Session `8ef5557d` blocked this source because approved non-secret metadata lacks deterministic account/contact/activity target, field payload, activity date/type/content, existing-record match, and dedupe key. Sonat blocker report sent 2026-04-20, subject `CRM/activity recovery blocked: source details needed`, Message-ID `<177670759491.94577.6982548554446206105@kovaldistillery.com>`, draft `drafts/sonat-crm-activity-recovery-blocker-2026-04-20.txt`. Robert human-readable correction sent 2026-04-20, Message-ID `<177670777142.96602.16061256851726520967@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-human-readable-details-needed-2026-04-20.txt`. Robert source-detail path sent 2026-04-20, Message-ID `<177671017432.9834.12022155147795059@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-source-detail-path-2026-04-20.txt`; it treats original mailbox source-detail recovery as approval-gated. No CRM/Portal/OPS mutation occurred.

- `avignon-email-review-distillery-photo-library-for-ai-content-generation`
  - Needed: Avignon received an email that was not clearly safe to auto-handle. Subject: `Distillery photo library for AI content generation`.
  - Next: Review only in the approved mailbox/workspace context and decide whether to route, reply, or hold.
  - Decision: Confirm the owner/action for this email-derived item.

- `avignon-sonat-crm-intake-recovery-2026-04-17`
  - Needed: Ten Sonat-originated Avignon messages on 2026-04-17 with CRM-addition subjects were archived to `Handled` after generic `avignon-email-review-*` logging, without visible CRM/import routing or completion confirmation. Recovery execution has now completed all deterministic non-ambiguous CRM work: Importer session `86dc0b04` completed Import ID `56` for the 5 importer-safe rows, and Portal session `44b8a370` completed source `9` and source `5`.
  - Next: 2026-04-20 target-link recheck found a partial Sonat answer in prior mail. Do not route further Portal/Importer mutation until a worker verifies existing CRM records and treats source `10` either as a no-op or uses a specific confirmed target account/distributor.
  - Decision: Partially resolved by Sonat reply `<CALbLtzyj0A=Vs8z5ftYRYeP+V2c_Bup_iRBR=DCck=-LzbO_WA@mail.gmail.com>`. Source `1` points Alexis Harris to existing CRM handling under `Sophy Hotel - Hyde Park`; source `7` status closeout is complete/yes; source `10` says Stephen Beck is already in the system and should not be added again but does not name a distributor/account link target. If target-link work is still expected for source `10`, the exact needed answer is whether to leave Stephen Beck as-is/no link update or link/update the existing contact under a specific named CRM account/distributor. Frank owner-path report `frank-avignon-crm-recovery-corrected-path-2026-04-19` was sent to Robert with Message-ID `<177661098259.95485.12446032407156880410@kovaldistillery.com>`. Prior Sonat status/current-state/decision emails were sent under task ids `avignon-sonat-crm-intake-recovery-2026-04-17-status-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-follow-up-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-current-state-2026-04-18`, and `avignon-sonat-crm-intake-recovery-2026-04-17-target-link-decisions-2026-04-18`; the last Sonat email is now treated as a quality issue, not the current waiting state.
- `avignon-email-review-lander-journal-your-input-needed-on-brand-voice-section-name`
  - Needed: Consolidated Lander Journal brand-voice/section-name thread review item. Earlier timestamped items for this same thread were duplicates created by the decision-email loop.
  - Next: Keep one local review item only; do not email Sonat again unless a fresh approval boundary is identified.
  - Decision: Determine internally whether Avignon can route/answer/file this thread, or escalate one concrete question if genuinely blocked.

- `avignon-email-review-new-ai-research-tools-with-fact-checking`
  - Needed: Avignon received an email that was not clearly safe to auto-handle. Subject: `New: AI Research Tools with fact-checking`.
  - Next: Review only in the approved mailbox/workspace context and decide whether to route, reply, or hold.
  - Decision: Confirm the owner/action for this email-derived item.

- `avignon-email-review-connecteam`
  - Needed: Avignon received an email that was not clearly safe to auto-handle. Subject: `Connecteam`.
  - Next: Review only in the approved mailbox/workspace context and decide whether to route, reply, or hold.
  - Decision: Confirm the owner/action for this email-derived item.

- `avignon-email-review-monthly-sales-report-which-saved-reports-to-include`
  - Needed: Avignon received an email that was not clearly safe to auto-handle. Subject: `Monthly sales report -- which saved reports to include?`.
  - Next: Review only in the approved mailbox/workspace context and decide whether to route, reply, or hold.
  - Decision: Confirm the owner/action for this email-derived item.
## Waiting On Sonat Email

No current Avignon email-derived items are waiting on Sonat email approval from Avignon inbox.

## Routed / Handled

- `avignon-direct-owner-sonat-CALbLtzwcFiUScRURX-DkwJ7mp27PFmV2TdDUj439MG75rMVi-g-mail-gmail-com`
  - Needed: Sonat direct-owner `CRM Addition` source was misfiled as `direct-owner-no-action` and recovered as active direct-owner work.
  - Next: Closed. Preserve duplicate protection; do not resurface unless a new source message arrives or Sonat/Robert explicitly reopens it.
  - Decision: Captured/routed acknowledgement sent to Sonat, Message-ID `<177671812569.61830.8920961406442089856@kovaldistillery.com>`. Portal worker `c0adcd3b` completed the routine CRM entry by creating account `367220`, contact `367221`, and association history row `5019`; read-back verification passed. Completion report sent Sonat-only, subject `CRM Addition complete: Paustis Wine`, Message-ID `<177671883829.74072.5914688977487091142@kovaldistillery.com>`, draft `drafts/sonat-crm-addition-paustis-wine-complete-2026-04-20.txt`. No Robert copy was required.

- `avignon-direct-owner-sonat-gabi-training-draft-2026-04-20`
  - Needed: Sonat asked Avignon to draft an email for Gabi about continuing training and adding filed training materials for Gabi to learn and consider. Source Message-ID `<CALbLtzyn5huDS5VXjeoe-rHqDtYDAWNjoTd0b6jDHAvTq4jJkg@mail.gmail.com>`; dedupe key `avignon-direct-owner-sonat-CALbLtzyn5huDS5VXjeoe-rHqDtYDAWNjoTd0b6jDHAvTq4jJkg-mail-gmail-com`.
  - Next: Wait for Sonat to provide the actual filed training materials/source packet or approve bounded source recovery before the Gabi email can be finalized with attachments/materials. Do not send to Gabi under this task.
  - Decision: Visible Avignon worker session `e6caa9bd` prepared `drafts/sonat-gabi-continuing-training-materials-2026-04-20.txt`. Local approved-file search found only references to `avignon-new-hire-training-template-reference-2026-04-12`, not the actual training packet. Sent Sonat the task-specific report/blocker, subject `Gabi training draft ready; materials packet needed`, Message-ID `<177671864897.72894.4011226924901203280@kovaldistillery.com>`, body draft `drafts/sonat-gabi-training-draft-report-2026-04-20.txt`. No mailbox body was printed or quoted; no OAuth/auth/token work, mailbox mutation, external reply to Gabi, CRM/Portal/OPS mutation, runtime/deploy, git commit, push, reset, or clean action occurred.

- `avignon-direct-owner-completion-report-boundary-2026-04-20`
  - Needed: Robert reaffirmed Avignon's direct-owner handling boundary after follow-through fixes.
  - Next: Apply this to future direct Sonat work, and to Robert messages when Robert is acting as Avignon workflow manager/approver. Keep the source out of `Handled` until a visible routed worker completes or hits a real blocker, state is updated, and the required report has been sent or the send gate is explicitly logged.
  - Decision: Report target is Sonat by default; copy Robert only when task context, approval path, or active supervision requires it. Completion/blocker reports must include what was done, what changed, what was not done, remaining decisions or approval gates, and relevant session/task IDs. Approval boundary remains no credential/private-mailbox-body exposure in chat, no OAuth/token/auth work, no external replies, no unclear CRM/Portal/OPS mutation, and no guessing at pricing, account commitments, or CRM duplicate/target handling. This entry is docs/state only; no source item was filed to `Handled` by this update.

- `avignon-email-review-process-for-sample-requests`
  - Needed: Sonat sent a direct process-related request that Avignon filed to `Handled` after generic ambiguous-review logging. Source Message-ID `<CALbLtzwCqmadr7Wg2jnZC5MeyFLf2hNCgMdypva69P2UWwg_FQ@mail.gmail.com>`.
  - Next: Treat as resolved by Robert's clarification and recorded standing guidance. Regular product/sample requests go through Portal POS/Samples create; barrel-sample workflow is used only when Sonat explicitly says `barrel sample`.
  - Decision: Robert clarified on 2026-04-20 that the SOP Sonat sent was for Avignon to record a directive. Guidance recorded in `REQUEST_SAMPLES_GUIDANCE.md` and `AGENTS.md`: use `https://portal.koval-distillery.com/#/pos-and-samples/sample-request/create` for regular sample/product requests; if Sonat asks for products, it is not a barrel sample unless she says `barrel sample`. No Portal sample request was created because no specific sample-request payload was supplied. Prior blocker email to Sonat remains logged as a quality issue; no follow-up email to Robert was needed because the clarification was clear. OPS session `ede1f8c3` is reconciled/review-ready and should be parked, not treated as an active blocker.

- `avignon-sonat-handled-mail-recovery-2026-04-20`
  - Needed: Robert reported that Avignon had 10+ Sonat emails in `Handled` with no visible acknowledgement/completion trace.
  - Next: Keep duplicate protection in place. Wait for Robert to approve bounded source-detail recovery or for Robert/Sonat to supply specific CRM/activity target packets before any further Portal/CRM routing or mutation; the sample-process item is resolved as recorded standing guidance.
  - Decision: Audited 35 Sonat-origin `Handled` messages since 2026-04-17 at header/log level. Sent Sonat catch-up status with Robert copied, subject `Avignon handled-mail recovery status`, Message-ID `<177670584365.66611.2391124488123910456@kovaldistillery.com>`. Follow-through reports sent Sonat-only on 2026-04-20: CRM/activity six-source blocker, subject `CRM/activity recovery blocked: source details needed`, Message-ID `<177670759491.94577.6982548554446206105@kovaldistillery.com>`; sample-process blocker, subject `Sample-process recovery blocked: direction needed`, Message-ID `<177670763603.94833.14163510464486881700@kovaldistillery.com>`. Robert human-readable correction sent Robert-only because the CRM/activity blocker was too Message-ID-focused: subject `Avignon CRM recovery: human-readable details needed`, Message-ID `<177670777142.96602.16061256851726520967@kovaldistillery.com>`. Robert source-detail path sent Robert-only after Robert corrected the ask, subject `Avignon CRM recovery: source-detail recovery path`, Message-ID `<177671017432.9834.12022155147795059@kovaldistillery.com>`. Reconciliation: session `8ef5557d` output is routed/reported and review-ready while the CRM business blocker remains missing target packets or bounded source-detail approval; session `ede1f8c3` is resolved/review-ready as guidance recorded. No mailbox move/unfile/reclassify, source-body print, CRM/Portal/OPS mutation, external reply, credential/auth/OAuth, LaunchAgent/runtime, production, deploy, commit, push, reset, or cleanup occurred.

- `avignon-robert-frank-crm-target-link-check-2026-04-20`
  - Needed: Robert asked Frank to double check with Avignon whether Sonat's prior emails resolved the CRM target link. Source Message-ID `<CAAtX44YhuBQTJ=6xx6RBioG4WY==B994tZPjbW3bdBtNMbS5ew@mail.gmail.com>`; continuation permission/source Message-ID `<CAAtX44Zhz0i41owpAdyPBoWWNWLz_9=E=RVqu4KSKodeunf_iQ@mail.gmail.com>`.
  - Next: Report to Task Manager/Frank that Avignon found a partial answer in Sonat's prior email. Do not mutate CRM/Portal/OPS until the existing records are verified and source `10` is treated either as an explicit no-op or assigned a specific target account/distributor.
  - Decision: Partially resolved. Checked Avignon TODO/HANDOFF/decision ledger, non-private action-plan review, draft filenames, narrow sent/automation-log metadata, and minimum necessary Avignon Gmail records. Found Sonat reply `<CALbLtzyj0A=Vs8z5ftYRYeP+V2c_Bup_iRBR=DCck=-LzbO_WA@mail.gmail.com>`: source `1` points Alexis Harris to existing CRM handling under `Sophy Hotel - Hyde Park`; source `7` status closeout is complete/yes; source `10` says Stephen Beck is already in the system and should not be added again but does not name a distributor/account link target. Recorded durable dedupe state in TODO/HANDOFF; no private mailbox body text, CRM/Portal/OPS mutation, mailbox filing, external-sensitive email, credential/auth/runtime/deploy/git, or production state change occurred.

- `avignon-sonat-email-delivery-status-2026-04-19`
  - Needed: Robert replied to Frank's Avignon runtime review completion report, source Message-ID `<CAAtX44a0j6bXPbJNh=Q7Cmm34H91KfFZ6c2iEtLb-as8+ittxA@mail.gmail.com>`, approving what was necessary to get Sonat the Avignon emails.
  - Next: Treat the Sonat-facing status/catch-up report as completed; remaining CRM target/link decisions stay under the existing CRM recovery item, and Gmail push/OAuth/PubSub remains parked pending Monday polling-health verification.
  - Decision: Sent Sonat subject `Avignon email delivery status` with Robert copied through the approved Avignon route; Message-ID `<177665295551.68733.4913818806070436873@kovaldistillery.com>`. No credential/OAuth/Google Cloud/PubSub, LaunchAgent restart/cadence, mailbox-body read, CRM/Portal mutation, deploy, push, commit, reset, or external-sensitive send occurred.

- `avignon-sonat-meeting-with-robert-2026-04-20`
  - Needed: Sonat emailed Avignon on 2026-04-19 asking for a Monday morning meeting with Robert and a Google invite to Robert.
  - Next: Treat clear Sonat calendar/meeting/invite requests as directives, not ambiguous review; this is also a completion-confirmation traceability example for the Robert escalation.
  - Decision: Created `Meeting with Robert` on Sonat's calendar for Monday, April 20, 2026, 9:00-9:30 AM Central, invited Robert through Google Calendar, and sent Sonat confirmation `Meeting with Robert scheduled` under task id `avignon-sonat-meeting-with-robert-2026-04-20`; sent metadata recorded Message-ID `<177663586164.17202.3915562064317338952@kovaldistillery.com>`.

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
