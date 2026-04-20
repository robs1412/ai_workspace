# TODO — avignon

Updated: 2026-04-20 16:00 CDT (Machine: Macmini.lan)

## In Progress

No active Avignon-local implementation item.

## Waiting Next Step

- Avignon direct-Sonat follow-through runtime alignment closeout:
  - Installed-only runtime patch applied to `/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py` on 2026-04-20 in worker session `646cea2f` / `Avignon direct Sonat follow-through runtime alignment`.
  - The patch adds direct Sonat and Robert-as-Avignon-approver detection, creates a visible Avignon workspace worker session before acknowledgement, records source/dedupe/owner/session/report state, keeps pending direct-owner items out of `Handled`, and sends completion/blocker closeout only after the routed session reaches a finished/blocked state.
  - Code/Git follow-up fix applied: previously logged non-direct INBOX residue now preserves the old archive-to-`Handled` behavior; direct-owner monitor/hold/closeout logic applies only to direct-owner records or direct-owner states.
  - Code/Git second follow-up fix applied: Workspaceboard status timeout/connection/API failures while monitoring pending direct-owner sessions now return a non-archivable `session-status-unavailable` hold instead of crashing the cycle.
  - Live incident fix applied after Robert reported a 12:59 CDT email still open at 13:33 CDT: Robert-as-approver closeout targets are recomputed as Robert-only instead of trusting stale stored `to Sonat, cc Robert` metadata, and previously logged pending direct-owner rows preserve owner/session/current-state metadata instead of degrading into generic residue.
  - Second live incident fix applied after Robert's `Activity check`: direct-Robert acknowledgements now pass the approved non-primary send flag when the report target is Robert-only, and direct-owner no-action classification now catches short `ok/thank you/thanks/got it` replies so they are filed instead of routed.
  - Verification passed: `python3 -m py_compile`, installed/source hash match `8596be8e28a302e15644bed2581aaff50ff3ba1ee1523b1d50cd12eb7f02614a`, Avignon log showed live cycles around the 15-second interval, duplicate `Activity check` sessions were closed, Robert received completion report `<177671344565.35603.10510580350308148588@kovaldistillery.com>`, and final Avignon INBOX/unread verified `0` / `0`.
  - Git closeout completed for the earlier source mirror: commit `6da393e` / `Preserve Avignon inbox runtime source mirror` was pushed to `origin/main`. The current second live incident patch is ready for source-mirror commit/push after final review.
  - Remaining gates: LaunchAgent restart/reload, deploy, mailbox OAuth/auth, CRM/Portal/OPS mutation, and any broader workflow policy change all require separate explicit approval.

- Gmail push parked follow-up:
  - Monday, 2026-04-20: verify Frank/Avignon 15-second polling health before any Gmail API push/OAuth/PubSub work resumes.
  - Robert pause directive from 2026-04-18: keep Frank/Avignon email handling on the current 15-second polling path until Monday, 2026-04-20.
  - First Monday action: verify polling health from non-secret LaunchAgent/runtime metadata.
  - Resume Gmail API push/OAuth/PubSub only if still needed and only from the M4 ERTC Google auth context.
  - Before Monday approval: no Google Cloud/PubSub/IAM mutation, no OAuth token work, no mailbox content read, no runtime cadence change, and no deploy/push/live pull for the Gmail push slice.
  - Do not attempt more Google auth changes before Monday unless Robert explicitly reopens it.

- CRM recovery next action:
  - Status: Avignon target-link recheck completed 2026-04-20 after Robert granted permission to inspect minimum necessary Sonat/Avignon email records. Earlier 2026-04-19 action-plan review is superseded only for the newly found Sonat answer.
  - Completed work: Importer session `86dc0b04` completed Import ID `56` for the 5 importer-safe rows; Portal session `44b8a370` completed source `9` and source `5`.
  - Review artifact: `drafts/avignon-crm-recovery-action-plan-review-2026-04-19.md`.
  - Newly found Sonat answer: source `1` points Alexis Harris to existing CRM handling under `Sophy Hotel - Hyde Park`; source `7` status closeout is complete/yes; source `10` says Stephen Beck is already in the system and should not be added again.
  - Remaining blocker before CRM mutation: if source `10` still requires a target link/update, confirm whether to leave Stephen Beck as-is/no link update or link/update the existing Stephen Beck contact under a specific named CRM account/distributor.
  - Before any further CRM mutation, a Portal/Importer worker should verify the existing records and use only the bounded answer above; do not infer a source `10` account link from the old Lanterna prompt.
  - Avignon worker `b583edb6` should use the private Frank context capture at `/Users/werkstatt/ai_workspace/frank/drafts/claude-avignon-context-frank-mail-2026-04-19.private.txt` and metadata at `/Users/werkstatt/ai_workspace/frank/drafts/claude-avignon-context-frank-mail-2026-04-19.meta.json`, plus private Avignon source artifacts, without printing private bodies/contact fields.
  - If Robert approves another follow-up, send one concise Avignon note to Sonat with Robert copied for visibility; copy Claude only if Robert explicitly wants Claude in the CRM decision thread.
  - Do not run phpList actions, broad imports, unrelated mailbox filing, credential work, destructive changes, or external-sensitive sends under this routine CRM authority.

- Sonat handled-mail recovery routing:
  - Source: Robert priority continuation on 2026-04-20 that Avignon filed 10+ Sonat emails to Handled without visible acknowledgement/completion trace.
  - Audit result: 35 Sonat-origin `Handled` messages since 2026-04-17 were audited at header/log level. Seven clear direct Sonat work requests were missing proper acknowledgement/status and are now captured under task id `avignon-sonat-handled-mail-recovery-2026-04-20`.
  - Sent catch-up status to Sonat with Robert copied: subject `Avignon handled-mail recovery status`, Message-ID `<177670584365.66611.2391124488123910456@kovaldistillery.com>`, draft `drafts/sonat-handled-mail-recovery-status-2026-04-20.txt`.
  - Portal CRM/activity worker: session `8ef5557d`, title `Portal Avignon Sonat CRM recovery work`, workspace `portal`, owns six source Message-IDs: `<CALbLtzx03Rzzqnn1M+0yZifY6-4YfQeekeVgK3+zKyQQbN0JCQ@mail.gmail.com>`, `<CALbLtzyPwnuk=Msw0wgFtDsOEnNk5QhiD+E9ZP7tRuqQouKDgw@mail.gmail.com>`, `<CALbLtzxSioFqgNL61KHSHVxVu9ZSnYGujC3YeS-j+OBPs+v4Yw@mail.gmail.com>`, `<CALbLtzxCAaOdQZohyM0m67A6mCWbbMCjTSOaMTi7W+RR2k3_2Q@mail.gmail.com>`, `<CALbLtzzm--wq-DqFsW8ePfVEAsgKAuiH1-gpB7Tehb=VUUDULg@mail.gmail.com>`, and `<CALbLtzx71n0bqs1_GJ+7WvDgt6jxNC5Wwi9tQRpq2X5rZh2nzg@mail.gmail.com>`.
  - Portal CRM/activity worker result: session `8ef5557d` completed after Robert approved bounded source-detail recovery. See Done entry for final non-secret record IDs and completion email.
  - OPS sample-process worker: session `ede1f8c3`, title `OPS Avignon Sonat sample process recovery`, workspace `ops`, owns source Message-ID `<CALbLtzwCqmadr7Wg2jnZC5MeyFLf2hNCgMdypva69P2UWwg_FQ@mail.gmail.com>`.
  - OPS sample-process clarification: session `ede1f8c3` originally blocked from approved non-secret metadata only and sent a Sonat blocker report, but Robert clarified on 2026-04-20 that the SOP was for Avignon to record standing guidance. Regular Sonat requests for products/samples use the Portal POS/Samples create page; barrel workflow is used only when Sonat explicitly says `barrel sample`. Guidance is now recorded in `REQUEST_SAMPLES_GUIDANCE.md`; no follow-up question to Sonat is needed for this recovered SOP item.
  - OPS worker reconciliation: session `ede1f8c3` output is reconciled as guidance recorded and is review-ready/parked, not an active blocker.
  - Routed-status acknowledgement decision: intentionally skipped as superseded by task-specific blocker reports once both worker results returned.
  - Task-specific reports sent: CRM/activity blocker Message-ID `<177670759491.94577.6982548554446206105@kovaldistillery.com>`; sample-process blocker Message-ID `<177670763603.94833.14163510464486881700@kovaldistillery.com>`.
  - Next: preserve duplicate protection. The six CRM/activity sources and sample-process guidance item are no longer waiting on Sonat direction.
  - Runtime/operating gap documented: direct Sonat work requests are still being classified as generic ambiguous review and then filed as `Handled` residue. Future runtime work should implement the documented Frank-like direct-primary-owner behavior before filing: visible route, captured acknowledgement, completion report, durable state.
  - Human-readable blocker correction recorded: future Avignon/Frank decision or blocker emails must state human-readable subject/name/company/action needed/current blocker/recommended next step first; Message-IDs and source IDs are trace references only, not the decision surface.
  - No mailbox move/unfile/reclassify, CRM/Portal mutation, external reply, credential/auth/OAuth, LaunchAgent/runtime, production, deploy, commit, or push was performed by this audit.

## Done

- 2026-04-20: Completed recovered Sonat direct-owner CRM Addition for Paustis Wine.
  - Source Message-ID `<CALbLtzwcFiUScRURX_DkwJ7mp27PFmV2TdDUj439MG75rMVi-g@mail.gmail.com>`; dedupe key `avignon-direct-owner-sonat-CALbLtzwcFiUScRURX-DkwJ7mp27PFmV2TdDUj439MG75rMVi-g-mail-gmail-com`; Avignon intake session `8c9e97c2`; Portal worker `c0adcd3b`.
  - Portal completed deterministic duplicate checks, created CRM account `367220`, created CRM contact `367221`, linked the contact to the account, and created association history row `5019`.
  - Sonat completion report sent subject `CRM Addition complete: Paustis Wine`, Message-ID `<177671883829.74072.5914688977487091142@kovaldistillery.com>`, draft `drafts/sonat-crm-addition-paustis-wine-complete-2026-04-20.txt`. No Robert copy was needed.
  - No private contact fields were printed in chat; no external email, destructive/bulk action, merge/delete, OAuth/auth/token work, deploy/restart, commit/push/reset/clean, or unrelated CRM change occurred from Avignon.

- 2026-04-20: Corrected Sonat's Gabi continuing-training draft with filed materials and Avignon SOP/persona source.
  - Source Message-ID `<CALbLtzyn5huDS5VXjeoe-rHqDtYDAWNjoTd0b6jDHAvTq4jJkg@mail.gmail.com>`; dedupe key `avignon-direct-owner-sonat-CALbLtzyn5huDS5VXjeoe-rHqDtYDAWNjoTd0b6jDHAvTq4jJkg-mail-gmail-com`; draft `drafts/sonat-gabi-continuing-training-materials-2026-04-20.txt`.
  - Correction: the earlier `materials packet needed` blocker was wrong. Robert pointed out that Sonat had already sent the links/materials and separate Avignon SOP/persona guidance. Bounded handled-mail recovery found and recorded the relevant sources: April 11 `New Hire Sample Training Email`, April 12 `Re: New Hire Sample Training Email`, April 11 `Re: Avignon persona blurb`, April 11 `Re: Avignon task-flow decision options`, and the April 20 `Sample email` request.
  - Private operational source packet: `drafts/gabi-training-source-synthesis-2026-04-20.private.md`; public-safe index: `GABI_TRAINING_SOURCE_INDEX.md`.
  - Corrected Sonat-facing draft/report: `drafts/sonat-gabi-continuing-training-materials-corrected-2026-04-20.txt`; sent to Sonat, subject `Corrected Gabi training draft`, Message-ID `<177671939004.75578.4686539983907647172@kovaldistillery.com>`. No email was sent to Gabi; Sonat must approve or edit before any Gabi send. No private body/Drive-link output in chat, auth/OAuth/token, CRM/Portal/OPS mutation, runtime/deploy, git reset/clean, or destructive action occurred.

- 2026-04-20: Reaffirmed Avignon direct-owner completion/report boundary.
  - Robert clarified that direct-owner work must not be filed to `Handled` until the visible route has either completed or hit a real blocker, Avignon TODO/HANDOFF/decision state is updated, and the required report is sent to Sonat by default with Robert copied only when the task context or approval path requires it. The report shape is what was done, what changed, what was not done, remaining decisions or approval gates, and relevant session/task IDs. This was docs/state only; no mailbox body read, email send, CRM/Portal/OPS mutation, OAuth/auth/token work, external reply, runtime change, deploy, commit, push, reset, or clean occurred.

- 2026-04-20: Fixed Avignon direct-Robert polling crash and restored inbox-zero behavior.
  - Root cause: Avignon was polling, but Robert-only direct-owner acknowledgement/report sends did not pass the explicit non-primary send flag unless a Cc existed, so the cycle crashed and retried. Patched installed runtime and source mirror so any non-Sonat direct-owner recipient gets the flag. Also classified short `ok/thank you/thanks/got it/sounds good` direct replies as no-action.
  - Verification: `python3 -m py_compile` passed; installed/source SHA-256 matched `8596be8e28a302e15644bed2581aaff50ff3ba1ee1523b1d50cd12eb7f02614a`; live log continued around the 15-second interval; stderr stopped updating after the pre-fix crash loop; Robert received Avignon's completion report; Robert's `Ok, thank you` reply filed to `Handled`; duplicate `Activity check` sessions were closed; final Avignon INBOX/unread `0` / `0`.
  - No OAuth/auth/token, LaunchAgent reload/restart, deploy, CRM/Portal/OPS mutation, external send, reset, clean, or destructive action occurred.

- 2026-04-20: Completed six recovered Sonat CRM/activity items and sent Sonat the required report.
  - Worker/session: `8ef5557d` / `Portal Avignon Sonat CRM recovery work`; private packet `drafts/crm-activity-source-detail-packets-2026-04-20.private.json`; redacted summary `drafts/crm-activity-source-detail-summary-2026-04-20.md`.
  - Completed CRM actions: activity `367205` for Jessica Claude/Martignetti recap; account `367206` Breakthru VA and contact `367207` Amanda Proper; account `367208` Bascom's Chop House and contact `367209` Cory Alan Whitehurst; linked existing contact `367148` Birk Walton to RNDC FL `14342`; activities `367210` and `367211` for Cory/Birk barrel-program follow-up/discussion; contacts `367212` Michael Cavin and `367213` Dan Schaden under RNDC MI `64246`; contact `367214` Jose Garcia under Favorite Brands `130091`; updated existing Vinocopia account `367202` with missing private source fields and verified existing Matt Holland contact `367203` remains linked to Vinocopia.
  - Verification: Portal worker confirmed listed records are active and linked as intended. No duplicates were created for Jessica Claude, Birk Walton, Vinocopia, or Matt Holland; no external send, destructive/bulk action, merge/delete, credential/OAuth/auth work, deploy/restart, commit/push/reset/clean, or private field disclosure occurred.
  - Completion report sent to Sonat with Robert copied: subject `CRM recovery complete: six items handled`, task id `avignon-sonat-crm-recovery-completion-2026-04-20`, Message-ID `<177671241834.23190.8046335433489445221@kovaldistillery.com>`, draft `drafts/sonat-crm-recovery-completion-2026-04-20.txt`.

- 2026-04-20: Closed Avignon live polling incident for Robert's 12:59 CDT INBOX report.
  - Confirmed polling was running but not completing the item because direct-owner monitor state was stale/corrupted and Robert-supervised target metadata had been wrong. Patched installed runtime and mirrored source so Robert-as-approver closeouts are Robert-only and pending direct-owner state keeps owner/session/current-state fields.
  - Filed Robert's 12:59 correction source to `Handled` after Robert-only response `<177671017432.9834.12022155147795059@kovaldistillery.com>`; filed Robert's 13:35 "thank you / let's get this fixed" continuation as attached to the existing fix. Final Avignon INBOX check: `0`.
  - Git source mirror was committed/pushed as `6da393e`. No new manual-closure email, external reply, CRM/Portal/OPS mutation, OAuth/auth, LaunchAgent restart, deploy, reset, or clean occurred.

- 2026-04-20: Sent Robert the Avignon CRM source-detail recovery path.
  - Sent Robert-only subject `Avignon CRM recovery: source-detail recovery path`, task id `avignon-robert-crm-recovery-source-detail-path-2026-04-20`, Message-ID `<177671017432.9834.12022155147795059@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-source-detail-path-2026-04-20.txt`.
  - The Robert correction source can be filed handled after logging; CRM recovery remains blocked pending Robert-approved source-detail recovery or a human-readable target table. No Sonat copy, source-body print, mailbox move, CRM/Portal/OPS mutation, auth/OAuth, LaunchAgent restart, deploy, commit, push, reset, or clean occurred.

- 2026-04-20: Sent Robert Avignon follow-through status.
  - Sent Robert-only subject `Avignon status: follow-through and current blockers`, task id `avignon-robert-follow-through-status-2026-04-20`, Message-ID `<177671005248.8797.6359110235608129687@kovaldistillery.com>`, draft `drafts/robert-avignon-follow-through-status-2026-04-20.txt`.
  - No Sonat copy, mailbox move, CRM/Portal/OPS mutation, auth/OAuth, LaunchAgent restart, deploy, commit, push, reset, or clean occurred.

- 2026-04-20: Sent Robert the human-readable Avignon CRM recovery correction.
  - Sent Robert-only subject `Avignon CRM recovery: human-readable details needed`, task id `avignon-robert-crm-recovery-human-readable-correction-2026-04-20`, Message-ID `<177670777142.96602.16061256851726520967@kovaldistillery.com>`, draft `drafts/robert-crm-recovery-human-readable-details-needed-2026-04-20.txt`.
  - Recorded persistent operating note that Avignon/Frank blocker and decision emails must not rely on old Message-IDs alone; they must include human-readable subject/name/company/action needed/current blocker/recommended next step and use source IDs only as trace references.

- 2026-04-20: Recorded Avignon request-samples guidance from Robert.
  - Robert clarified that `Process for Sample Requests` was an SOP/persona directive to record standing guidance. Regular Sonat requests for products/samples use Portal `https://portal.koval-distillery.com/#/pos-and-samples/sample-request/create`. If Sonat means a barrel sample, she will say `barrel sample`; do not infer barrel workflow from product/sample wording alone.
  - Added `REQUEST_SAMPLES_GUIDANCE.md` and updated Avignon role guidance. The prior sample-process blocker is resolved as guidance recorded; no email to Robert was needed because the clarification was clear. No Portal sample request was created because no specific sample request payload was supplied.

- 2026-04-20: Implemented installed Avignon direct-owner runtime alignment.
  - Patched installed `avignon_inbox_cycle.py` so direct Sonat work and Robert-as-Avignon-approver instructions follow visible route -> acknowledgement -> durable state -> completion/blocker report -> handled filing mechanics. Applied Code/Git follow-up fixes preserving old archive behavior for previously logged non-direct residue and holding pending direct-owner items safely when Workspaceboard status is unavailable. Source preserved under `runtime-source/avignon-launch/scripts/`; commit, push, reinstall/restart, and live-cycle verification remain approval-gated.

- 2026-04-20: Recorded shared Frank/Avignon direct-owner follow-through directive for Avignon.
  - Avignon must acknowledge, route, follow through, and send completion or blocker reports for direct Sonat work before filing handled. Runtime/code alignment remains the active In Progress item above.

- 2026-04-20: Sent Avignon handled-mail recovery status to Sonat.
  - Audited 35 Sonat-origin `Handled` messages since 2026-04-17 without printing private bodies. Found 7 clear direct Sonat work requests that lacked proper acknowledgement/status; sent one internal catch-up status to Sonat with Robert copied.
  - Sent subject `Avignon handled-mail recovery status`, task id `avignon-sonat-handled-mail-recovery-2026-04-20`, Message-ID `<177670584365.66611.2391124488123910456@kovaldistillery.com>`.
  - No mailbox move/unfile/reclassify, CRM/Portal mutation, external reply, credential/auth/OAuth, LaunchAgent/runtime, production, deploy, commit, or push was performed.

- 2026-04-20: Mirrored Robert-approved external-sender handling directive for Avignon.
  - Approval source Message-ID `<CAAtX44ZtTzCMqg-eZgO2X5rfkf+hhF2CzOzv+uyHe=T0GN7QRw@mail.gmail.com>`; confirmation Message-ID `<CAAtX44YfMtfrf_dA69mw7uLZvuBO=j-kZraJYskdLYjrPr9gvA@mail.gmail.com>`.
  - Directive: external senders do not receive Avignon/Frank internal control-surface confirmations or board/session/task status; external replies are normal business responses only; no external auto-send exists unless a named sender class/template is separately approved. Docs/state only; no Avignon mailbox/runtime/auth/credential/production/deploy/git change.

- 2026-04-20: Completed Robert/Frank-routed check of Sonat CRM target-link status.
  - Source Message-ID `<CAAtX44YhuBQTJ=6xx6RBioG4WY==B994tZPjbW3bdBtNMbS5ew@mail.gmail.com>`; continuation source `<CAAtX44Zhz0i41owpAdyPBoWWNWLz_9=E=RVqu4KSKodeunf_iQ@mail.gmail.com>`; session `Avignon CRM target-link verification`; dedupe key `avignon-robert-frank-crm-target-link-check-2026-04-20`.
  - Checked Avignon TODO/HANDOFF/decision ledger, non-private CRM action-plan review, draft filenames, narrow Avignon sent/automation-log metadata, then minimum necessary Avignon Gmail records across `Handled`, `INBOX`, `[Gmail]/All Mail`, and `[Gmail]/Sent Mail`.
  - Result: partially resolved. Sonat reply `<CALbLtzyj0A=Vs8z5ftYRYeP+V2c_Bup_iRBR=DCck=-LzbO_WA@mail.gmail.com>` answers source `1` as Alexis Harris under `Sophy Hotel - Hyde Park` and answers source `7` status closeout as complete/yes.
  - Source `10` partial answer: Stephen Beck is already in the system and should not be added again. If a target link/update is still required, the needed answer is whether to leave Stephen Beck as-is/no link update or link/update the existing contact under a specific named CRM account/distributor.
  - No CRM/Portal/OPS/mailbox/email/runtime/auth/deploy/git/production mutation occurred; Task Manager/Frank should report this partial resolution back to Robert.

- 2026-04-20: Sent missing Monday morning summary catch-up to Sonat.
  - Source Message-ID `<CAAtX44bvRKy+y9-pc6q2YtRNxagu-v=efSToCHVZvfXTz70HDg@mail.gmail.com>`; visible session `f60904c1` / `Avignon Monday morning summary catch-up`.
  - Non-secret sent-log and morning-overview logs showed no prior Monday 2026-04-20 morning-summary send; duplicate key `avignon-morning-summary-2026-04-20` was clear before send.
  - Sent Sonat-only subject `Morning Summary: Monday, April 20`, task id `avignon-morning-summary-2026-04-20`, Message-ID `<177668518217.34199.10102899633008497659@kovaldistillery.com>`; draft/log path `/Users/admin/.avignon-launch/state/drafts/morning-summary-2026-04-20.txt`.
  - Follow-up remediation session `019dab8f-d773-7251-a525-3fc5ab0f8315` / `Frank/Avignon scheduled reports runtime remediation`: installed `com.koval.avignon-morning-overview` now has both 06:00 and 18:00 schedule entries and Avignon-specific runtime/log paths; Avignon EOD dry-run completed without sending.
  - Remaining blocker: scheduled `com.koval.avignon-morning-overview` is enabled but still not loaded in the current logged-out/non-Aqua launchd context; loading requires an active Aqua/gui user session or separately approved privileged launchd action.

- 2026-04-19: Sent Sonat the Avignon email delivery/runtime status report requested by Robert.
  - Source Message-ID `<CAAtX44a0j6bXPbJNh=Q7Cmm34H91KfFZ6c2iEtLb-as8+ittxA@mail.gmail.com>`; task id `avignon-sonat-email-delivery-status-2026-04-19`.
  - Sent subject `Avignon email delivery status` to Sonat with Robert copied; Message-ID `<177665295551.68733.4913818806070436873@kovaldistillery.com>`; draft `drafts/sonat-avignon-email-delivery-status-2026-04-19.txt`.
  - Report stated that recent Avignon Sonat-facing task emails are present in the sent log, the bounded runtime review did not reproduce the suspected Python 3.9 issue, current polling output is cycling successfully, CRM target/link decisions remain open, and Gmail push/OAuth/PubSub remains parked pending the Monday polling-health check.
  - No credential/OAuth/Google Cloud/PubSub, LaunchAgent restart/cadence, mailbox-body read, deploy, push, commit, reset, clean, CRM/Portal mutation, or external-sensitive send was performed.

- 2026-04-19: Completed approved Avignon Python 3.9 runtime compatibility hotfix check.
  - Approval source: Robert Message-ID `<CAAtX44ZbSRL-xm9os0OeuBABU82PnkjAQJ16VQnqWiupkqXfmw@mail.gmail.com>`.
  - Checked approved installed runtime files and direct Avignon import chain; `/usr/bin/python3` and `python3` are Python 3.9.6, and `python3.9` is not installed as a separate command.
  - Result: no current Python 3.9 compile/import failure reproduced. Existing `str | None` / `Path | None` annotations are paired with `from __future__ import annotations`; `list[...]`/`dict[...]` usage is compatible with Python 3.9. No runtime file edit or backup was needed.
  - Verification: `/usr/bin/python3 -m py_compile` on the approved scripts passed; `PYTHONPATH=/Users/admin/.avignon-launch/runtime/scripts /usr/bin/python3` imports for `send_frank_email`, `avignon_inbox_cycle`, `frank_paths`, `assistant_decision_email`, and `avignon_morning_overview` passed; `send_frank_email.py --help` passed without credential access.
  - No email was sent; no mailbox body/state, credential/OAuth/secret, LaunchAgent, cadence, deploy, commit, push, reset, clean, or session state was touched.

- 2026-04-19: Audited Avignon completion-confirmation flow for Robert escalation.
  - Checked Avignon TODO/HANDOFF/decision ledger and available non-secret sent/automation metadata; no safe missing Sonat completion report was identified for the last few completed Sonat-owned tasks.
  - Immediate safe fix was docs/state only: recorded runtime reliability blocker and current confirmation status. No email was sent, no mailbox body/secret was printed, and no runtime/code/auth/LaunchAgent/mailbox mutation was performed.

- 2026-04-19: Mirrored Avignon side of the email context/signature formatting fix.
  - Source Message-ID `<CAAtX44b2TeGjyqiz9Eu8hSt7HjyUDioP7eoVO7SQ1z4m_EKmgw@mail.gmail.com>`; dedupe key `frank-avignon-email-context-signature-fix-CAAtX44b2TeGjyqiz9Eu8hSt7HjyUDioP7eoVO7SQ1z4m_EKmgw`; visible Frank worker/session `0636ae32`.
  - Updated installed Avignon send-helper signature and Avignon morning-summary signature behavior under the existing local approved send configuration. Verification used dry-runs only; no Avignon email was sent and no mailbox/CRM/runtime cadence/credential/auth state changed.

- 2026-04-19: Sent plain-English CRM remaining-decision correction to Sonat with Robert copied.
  - Sent subject `CRM cleanup: plain-English remaining decisions`, task id `avignon-sonat-crm-clear-missing-decisions-2026-04-19`, Message-ID `<177661436956.52315.8467458566500911223@kovaldistillery.com>`, draft `drafts/sonat-crm-clear-missing-decisions-2026-04-19.txt`.
  - Corrected internal source-number wording into answerable names/companies: Alexis Harris / SOPHY Hyde Park / Mesler Kitchen Bar Lounge, Stephen Beck / Lanterna Distributors, and Sonat's list/status request.
  - No CRM/Portal mutation, phpList action, credential exposure, OAuth/auth work, service restart, deploy, live pull, external customer send, or private body disclosure in chat occurred.

- 2026-04-19: Answered Sonat's new CRM accounts/contacts request and restored Avignon inbox-zero.
  - Sent Sonat-only subject `New CRM accounts and contacts entered`, task id `avignon-sonat-new-crm-accounts-contacts-2026-04-19`, Message-ID `<177661321931.37680.11405389492595920280@kovaldistillery.com>`, draft `drafts/sonat-new-crm-accounts-contacts-2026-04-19.txt`.
  - Filed the source thread and remaining Avignon inbox residue to `Handled`. Final verification: Avignon INBOX `0`, unread `0`.
  - No CRM/Portal mutation, phpList action, credential exposure, OAuth/auth work, deploy, live pull, service restart, external customer send, or private body disclosure in chat occurred.

- 2026-04-19: Recorded Avignon inbox-zero directive.
  - Avignon must keep mailbox state at `0` open / `0` unread as the standing target by filing handled/no-action/already-routed/duplicate/completed mail to `Handled` after source-id logging and surfacing only one real Sonat/Robert decision/blocker at a time.
  - This does not authorize credential exposure, auth/OAuth work, external-sensitive sends, finance/legal/security decisions, destructive/bulk action, production-impacting changes, suspicious-mail bypass, or private-content disclosure.

- 2026-04-19: Sent Sonat the pricing unification / Portal pricing scope note.
  - Task id `ops-pricing-unification-portal-2026-04-19`; subject `Pricing unification and Portal pricing scope`; Message-ID `<177661177342.12519.5475020165538054926@kovaldistillery.com>`. No production pricing data or Portal behavior changed.

- 2026-04-19: Completed Avignon CRM recovery action-plan review.
  - Review artifact: `drafts/avignon-crm-recovery-action-plan-review-2026-04-19.md`.
  - Outcome: no safe further CRM mutation without exact human answers for source `1`, source `10`, and source `7`; item moved out of active In Progress into Waiting Next Step. No private bodies/contact fields were printed; no email was sent; no CRM/Portal/phpList/mailbox/credential/runtime mutation was performed.

- 2026-04-18: Parked Gmail API push/OAuth/PubSub slice until Monday health check.
  - Recorded Robert's pause directive: stay on current 15-second polling until Monday, 2026-04-20; verify polling health first; resume Gmail API push/OAuth/PubSub only from the M4 ERTC Google auth context if still needed. Docs-only; no Google auth, mailbox read, runtime cadence change, Cloud/PubSub/IAM mutation, deploy, push, live pull, credential, OPS, or external-system state changed.

- 2026-04-18: Installed Avignon Gmail fast-poll runtime improvement.
  - `com.koval.avignon-auto` now polls every 15 seconds instead of 60 seconds, using the existing duplicate-protected inbox cycle. True Gmail push is still blocked on Google Cloud/PubSub/IAM plus Avignon Gmail API OAuth setup.

- 2026-04-18: Cleaned active Avignon TODO.
  - Collapsed verbose history into the current CRM recovery item plus exact waiting gates. Older Done history remains in `HANDOFF.md` and `TODO-done-archive-2026-04-18.md`. No mailbox/runtime/CRM/Portal/phpList mutation was performed.
- 2026-04-18: Mandatory Avignon completion-report correction recorded.
  - Avignon task-completion report email is required by default unless explicitly suppressed. Reports go to Sonat by default and include Robert only when task context or approval path requires it.
- 2026-04-18: Authorized Avignon chief-of-staff inbox cleanup sweep completed.
  - Final verified Avignon INBOX/unread was `0` / `0`. No follow-up email, worker routing, credential output, runtime change, CRM/Portal write, or external-system action was performed.
- 2026-04-18: Chief-of-staff email-worker directive recorded.
  - Avignon routes clear low-risk internal email tasks to visible workers, verifies start/completion, updates durable state, sends required completion reports, suppresses duplicate surfacing, files FYI/CC/no-action items, and follows 24-hour decision follow-up rules.
- 2026-04-17 and earlier: Older Avignon setup, runtime, inbox, decision-loop, CRM recovery, Google Ads routing, and historical completion entries archived out of the active TODO.
  - See `TODO-done-archive-2026-04-18.md` and `HANDOFF.md`.

## Backlog

No open items.
