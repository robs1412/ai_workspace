# HANDOFF - asher

## 2026-06-07 Sonat BCC Directive Recorded

Directive recorded at 2026-06-07 14:24 CDT: Asher outbound emails must include Sonat Birnecker Hart at `sonat@kovaldistillery.com` as Bcc unless Sonat is already an explicit To/Cc/Bcc recipient on the same message.

- AI Manager input: row `2863`, UUID `ai-manager-chat-20260607192442-b0e0b4c8eaee`.
- Papers durability path: `ai-manager/durability/2026-06-07-decision-directive-venetia-and-asher-outbound-emails-must-always-bcc-sonat.md`.
- Enforcement: approved-send helper `scripts/email_worker_header_poll.py` now applies the default Bcc rule for worker `asher`; runtime copy synced to `/Users/admin/.asher-launch/runtime/scripts/email_worker_header_poll.py`.

## 2026-04-27 Setup Scaffold

Asher workspace created for `asher@thecultivater.com`.

Private credential file: `.private/email-workers/asher/credentials.txt`

Verification: IMAP SSL, IMAP STARTTLS, SMTP SSL, and SMTP STARTTLS authentication succeeded against the supplied mail server. No mailbox messages were listed, read, moved, filed, or sent.

Current blocker: explicit action-policy approval before filing, deletes, or routine authority beyond approved task-specific sends. Body reads, owner-question drafting, and approved send automation are enabled. Avignon is the managing assistant by default.

## 2026-04-27 Sonat Introduction Sent

Asher sent Sonat the setup introduction and directive-request email.

- To: `sonat@kovaldistillery.com`
- Subject: `Introduction: Asher email worker`
- Message-ID: `<177729951721.95902.8196008921447369271@thecultivater.com>`
- Local body: `asher/drafts/sonat-introduction-2026-04-27.txt`
- Local sent log: `asher/sent-log.jsonl`

No credentials or private mailbox content were included.

## 2026-04-27 Body-Read Polling Activated

`system/com.koval.asher-auto` is installed as a system LaunchDaemon under `/Library/LaunchDaemons/`, runs as `admin`, and is configured for a 60-second interval.

Read-only launchd verification showed repeated runs with last exit code `0`. Runtime output now includes body reads, owner-question drafting, and approved send automation for new messages, and no mailbox bodies were filed or deleted.

## 2026-04-27 Sonat Persona Packet Incorporated

Sonat's Cultivater editor attachment was retrieved from Avignon's handled mailbox source and stored privately under `.private/email-workers/asher-venetia/`. The reusable Asher Wilde persona/directive is now incorporated in `PERSONA.md`.

Asher is the Editor-in-Chief / Philosophical Preservationist for The Cultivater. He owns heritage, organic farming, food and drink, slow travel, provenance, stewardship, and craft-lineage editorial angles. His voice is warm, authoritative, tactile, literary, slow, and quality-focused. Filing, deletes, external sends, and routine authority remain gated pending a separate action-policy approval.

Sonat's source also included an Asher internal memo request. The draft is saved at `asher/drafts/internal-memo-cultivater-editorial-direction-2026.md`.

Sent on 2026-04-27:

- Persona packet to Sonat, Robert copied. Subject `Asher Wilde persona packet incorporated`; Message-ID `<177732440298.88011.4507330355917329364@thecultivater.com>`.
- Internal memo to Sonat, Robert copied. Subject `The Cultivater: internal memo from Asher`; Message-ID `<177732440451.88011.13318200542973770515@thecultivater.com>`.

Broader mailbox filing, deletes, and routine authority remain gated pending the separate action-policy approval.

## 2026-05-17 Cultivater Outreach Approval Request Sent

Asher sent Sonat the approval request for the current Cultivater outreach draft set.

- To: `sonat@kovaldistillery.com`
- Subject: `Cultivater draft emails for approval`
- Message-ID: `<177906017569.47621.51219568993032508@thecultivater.com>`
- Local body: `asher/drafts/cultivater-sonat-approval-request-2026-05-17.md`
- Local sent log: `asher/sent-log.jsonl`
- Task Flow key: `taskflow-cultivater-asher-sonat-approval-2026-05-17`
- Workspaceboard work-state session: `asher-cultivater-approval-2026-05-17`

The external business outreach subject line remains `The Cultivater Feature Inquiry` and no business send will happen until Sonat approves.

## 2026-05-18 Direct Route Confirmed

Sonat confirmed the direct Asher route for Cultivater outreach work. Use `asher@thecultivater.com` as the primary route for Asher's own draft/send workflow, while keeping the existing action-policy gate in place for any external send.

## 2026-05-22 Cultivater Exact-Text Review Request Already Satisfied

Reviewed the visible worker packet `taskflow-9a832f3b9b2cccd2` against the live Asher proof surfaces after National Outreach prompted `Cultivater: please send Sonat the exact message text for review`.

- The earlier summary mail to Sonat was sent on 2026-05-17 with subject `Cultivater draft emails for approval`, Message-ID `<177906017569.47621.51219568993032508@thecultivater.com>`, local draft `asher/drafts/cultivater-sonat-approval-request-2026-05-17.md`.
- The exact full-text draft set for the Asher lane was also sent to Sonat on 2026-05-17 from `asher@thecultivater.com` with the same subject. Sent-log proof shows Message-IDs `<177906092050.55241.18422117979413402264@thecultivater.com>`, `<177906111421.57747.4798276751179909865@thecultivater.com>`, and the latest revised full-text send `<177906158668.61070.415055155373296713@thecultivater.com>`.
- The revised full-text send satisfies the request to give Sonat the exact message text for review before any outbound business email.

Outcome: no new mailbox action was needed from this packet. The truthful closeout is complete with proof from `asher/sent-log.jsonl` plus the local draft source.

## 2026-05-22 Cultivater Approval Reply Classified

Workspaceboard packet `taskflow-125eef164a018e83` (`Re: Cultivater draft emails for approval`) is no longer an open approval decision.

- Source poll capture: `header-poll-log.jsonl` logged Sonat's May 18, 2026 reply to Asher's revised approval-request thread as body-captured, unprocessed residue under the same subject.
- Original approval request proof: `sent-log.jsonl` contains Asher's approval request chain, including revised full-text approval Message-ID `<177906158668.61070.415055155373296713@thecultivater.com>`.
- Superseding outcome proof: `../daily-inputs/2026-05-21.md` records that a later Sonat approval email titled `Emails` instructed both Cultivater sends and that the stale Asher approval wait was closed on 2026-05-21.

Result: classify this May 18 reply packet as completed/no-action residue rather than an active owner question. No mailbox mutation was performed here; filing and external-send actions remain gated outside the scope of this review.

## 2026-05-22 Packet `taskflow-c9fded0aa59bb3a3` Blocked On Body Access Boundary

Reviewed the repo-local Asher proof surfaces for Sonat's captured message with subject `Emails`, Message-ID `<CALbLtzwCoCRLSE2ptGO8Yu3iK46ugOM_gHmNDZ5HGy5u9OncjQ@mail.gmail.com>`, logged at `2026-05-18 15:57:55 -0500`.

- Repo-local proof exists in `header-poll-log.jsonl` with Task Flow key `taskflow-c9fded0aa59bb3a3`.
- The captured full body path recorded there is `/Users/admin/.asher-launch/state/bodies/calbltzwcocrlse2ptgo8yu3ik46ugom_ghmndz5hgy5u9oncjq-mail.gmail.com.txt`.
- This session is operating under the `ai_workspace` boundary that disallows work outside `/Users/werkstatt` without explicit approval, so the body cannot be reviewed from the current allowed surfaces.

Truthful outcome: blocked pending either a repo-local mirror of the captured body into `/Users/werkstatt` or explicit approval to inspect the existing `/Users/admin/.asher-launch/...` body file. No mailbox mutation, filing, or reply was performed.
