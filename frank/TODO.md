# TODO — frank

Updated: 2026-04-20 12:01 CDT (Machine: Macmini.lan)

## In Progress

_No active Frank implementation/routing items._

## Blocked / Parked

- [ ] `frank-avignon-scheduled-reports-launchd-blocker-2026-04-20`: Scheduled-report runtime remediation partially fixed Avignon schedule, but Frank/Avignon scheduled-report LaunchAgents remain blocked at the user launchd loading boundary.
  - Source Message-IDs: `<CAAtX44YHbyyXDVws5=DRs+77N3O63WEf_+TBnD1yUaBvDTVaoQ@mail.gmail.com>` (`Re: Daily updates incident final report`, Tue, 21 Apr 2026 00:42:55 +0900) and `<CAAtX44bzZ3kojULqhSxsNdOFRKXqzxg0uwsZDkR1F4sb3JNK3w@mail.gmail.com>` (`Re: Daily update send status check`, Mon, 20 Apr 2026 10:43:14 -0500).
  - Source worker: `f704aa61` / `Frank Avignon scheduled reports remediation approved`.
  - Robert-only completion/blocker report sent, subject `Frank/Avignon scheduled reports: partial fix and launchd blocker`, task id `frank-avignon-scheduled-reports-launchd-blocker-2026-04-20`, Message-ID `<177670038813.68233.3384470854535767002@kovaldistillery.com>`, draft `drafts/frank-avignon-scheduled-reports-launchd-blocker-robert-2026-04-20.txt`.
  - Result reported: Frank installed plist already had 06:00 and 18:00 entries; Avignon installed plist now has 06:00 and 18:00 entries with Avignon runtime/log paths; both plists lint; both helpers completed EOD `--dry-run`; both labels are enabled.
  - Blocker: both labels remain enabled but not loaded as services in `user/501`; `bootstrap user/501` failed error 5, `bootstrap gui/501` failed error 125, legacy `load -w` exited 134, and `sudo -n bootstrap` was unavailable because sudo requires a password. No password prompt or handling occurred.
  - Needed: active Aqua/gui user-session launch/load verification or separately approved privileged/hard-server-mode launchd remediation.
  - Duplicate/handled status: both source Message-IDs are logged here, in `completion-confirmation-log.jsonl`, and in the Frank automation log as handled/blocked for duplicate suppression; IMAP archive-by-Message-ID found no matching current INBOX items to move, so no mailbox bodies were read.
  - Boundaries observed: no secrets, passwords, tokens, private keys, credential contents, mailbox bodies, OAuth, Gmail push, Pub/Sub, IAM, Google Cloud, DNS, TLS, router, `.205`, Workspaceboard runtime, production deploy, code commit/push, polling cadence, `com.koval.frank-auto`, `com.koval.avignon-auto`, privileged launchd work, or password handling was changed or accessed by this report session.

- [ ] `frank-avignon-oauth-token-storage-blocked-2026-04-20`: Frank/Avignon Gmail push OAuth continuation blocked before OAuth because the approved token storage path/scope/client are not documented.
  - Source Message-ID: `<CAAtX44bSqrWb2twfLvj_45oOkFLKcSDtjGQ6fqwRbm16xBSprA@mail.gmail.com>`; classification `tracked-primary-instruction`; subject `Re: Monday polling health verification complete`; from Robert Birnecker `<robert@kovaldistillery.com>` on Tue, 21 Apr 2026 00:38:04 +0900 / Mon, 20 Apr 2026 10:38:04 CDT.
  - Source OAuth worker: `05445182` / `Frank Avignon OAuth next step approved`; Frank report worker: `e2af4017`; report draft `drafts/frank-avignon-oauth-token-storage-blocked-robert-2026-04-20.txt`.
  - Robert blocker report sent to `robert@kovaldistillery.com` only, subject `Frank/Avignon OAuth blocked: token storage approval needed`, task id `frank-avignon-oauth-token-storage-blocked-2026-04-20`, Message-ID `<177669997157.65386.7555298061424976297@kovaldistillery.com>`.
  - State: blocked before OAuth. The source worker performed no OAuth/browser login, token creation/write/refresh/validation, mailbox read/search/export, Pub/Sub/IAM/Google Cloud project/subscriber/webhook work, LaunchAgent/cadence/runtime/production/deploy/push/live-pull changes, or external-sensitive email.
  - Backup polling remains in place: plist metadata still shows `StartInterval 15` for both Frank and Avignon.
  - Needed before OAuth can continue: Robert approval for the named Frank/Avignon OAuth token storage path and storage class; minimum Gmail API scope; OAuth client/source replacing the deleted Gmailconnector client; and explicit approval for any setup/token path outside `/Users/werkstatt/ai_workspace`, including whether metadata-only checks or actual token writes are allowed.
  - Duplicate/handled status: source Message-ID is logged here and in the completion-confirmation log as handled/blocked for duplicate suppression; do not resurface it as a fresh decision unless Robert replies with the missing approvals.
  - Boundaries observed by this report session: no OAuth/browser login, token write/refresh/validation, mailbox read/search/export, Pub/Sub/IAM/Google Cloud mutation, LaunchAgent/runtime/cadence change, deploy/push/live pull, or credential/token material was inspected or printed.

- [ ] `frank-claude-drive-credential-setup-blocked-2026-04-20`: Claude Drive credential/OAuth setup blocked as credential/auth-sensitive.
  - Source Message-ID: `<CAAtX44YV+ufv=AVs9+S7DyAt7XTJ0pVfzg-c9oYfM=HphmgKaw@mail.gmail.com>`; classification `tracked-primary-instruction`; subject `Re: Fwd: Password for claude@kovaldistillery.com needed for Drive API setup`; from Robert on 2026-04-20 10:35:37 -0500.
  - Work session: `5e6261fa` / Frank email-specific work session; Security review session `026a8ee8` / `Security review Claude Drive password request`.
  - Robert blocker report sent to `robert@kovaldistillery.com` only, subject `Claude Drive credential setup: safe next step needed`, task id `frank-claude-drive-credential-setup-blocked-2026-04-20`, Message-ID `<177669959173.63330.7018280144492669297@kovaldistillery.com>`, draft `drafts/claude-drive-credential-setup-safe-next-step-robert-2026-04-20.txt`.
  - State: blocked pending human physical credential entry by Robert/Dmytro or an approved secure secret-manager/keychain workflow where agents receive only a non-secret reference, plus non-secret confirmation of account, Drive API/OAuth project/app, minimum scopes, allowed token storage location, and whether Google Cloud/IAM/Drive API changes are approved or only human credential entry is approved.
  - Duplicate/handled status: runtime automation log already recorded the source and filed it to `Handled`; keep this TODO row as the active blocker record so the source does not resurface as a fresh decision.
  - Boundaries observed: no Claude password/app password, regular login, token, credential-file contents, server credential file, Google/OAuth/Drive/IAM mutation, production/runtime change, mailbox body dump, or secret material was accessed or printed by this session.

- [ ] `frank-one-by-one-blockers-2-through-7-2026-04-19`: Waiting on Robert replies to blockers 2-7, except Blocker 6 is answered/parked until April 27.
  - Source: follow-up chat instruction routed by Task Manager, `Email the other blockers too`.
  - Work session: `4a3d38b5` / `Frank one by one blocker emails`.
  - Blocker 2 sent to `robert@kovaldistillery.com` only, subject `Blocker 2: CRM target/link`, Message-ID `<177665505693.77020.10794824217811744970@kovaldistillery.com>`, draft `drafts/blocker-2-crm-target-link-robert-2026-04-19.txt`; asked which exact CRM target/link Avignon should use.
  - Blocker 3 sent to `robert@kovaldistillery.com` only, subject `Blocker 3: Gmail push/OAuth/Pub/Sub`, Message-ID `<177665505946.77053.17205547597713858551@kovaldistillery.com>`, draft `drafts/blocker-3-gmail-push-oauth-pubsub-robert-2026-04-19.txt`; asked whether to keep Gmail push/OAuth/Pub/Sub parked and continue current polling.
  - Blocker 4 sent to `robert@kovaldistillery.com` only, subject `Blocker 4: Claude and AI Bridge context`, Message-ID `<177665506271.77054.901458924896341917@kovaldistillery.com>`, draft `drafts/blocker-4-claude-ai-bridge-context-robert-2026-04-19.txt`; stated the external wait on Claude/AI Bridge backup context and next-step status.
  - Blocker 4 approval follow-up received: Source Message-ID `<CAAtX44ZYxUpzOLz1UXNUT-C8CnQSXxGy0hge3ojxW+f3PwBHWw@mail.gmail.com>`; Robert wrote, "Great. Let's add to plan and implement." Current state: attached to existing AI-Bridge plan/status task; AI-Bridge completed the safe local docs/source-map implementation and left Workspaceboard code/runtime work routed to Code/Git Manager. Frank should send the task-specific completion report from the AI-Bridge closeout and not create a duplicate blocker item.
  - Blocker 5 sent to `robert@kovaldistillery.com` only, subject `Blocker 5: Login/Codex password reset`, Message-ID `<177665506428.77055.11055407524342367711@kovaldistillery.com>`, draft `drafts/blocker-5-login-codex-password-reset-robert-2026-04-19.txt`; asked whether to handle the Login/Codex reset through the approved reset path.
  - Blocker 6 sent to `robert@kovaldistillery.com` only, subject `Blocker 6: OPS Connecteam packet`, Message-ID `<177665506583.77095.13636226877758366898@kovaldistillery.com>`, draft `drafts/blocker-6-ops-connecteam-packet-robert-2026-04-19.txt`; asked whether the Connecteam packet should wait for a fresh approved export/read-only export path. Robert replied in source Message-ID `<CAAtX44YOhLG9thNhpXnT4g=sAG468rEcf1nGteTjgEWjvwNMww@mail.gmail.com>` on 2026-04-20: `No new export info. We will have more April 27 - remind me at 11am.` Current state: answered/parked, no fresh export now, remind/follow up on Monday 2026-04-27 at 11:00 AM local time; do not create a duplicate work item or re-ask before then.
  - Blocker 7 sent to `robert@kovaldistillery.com` only, subject `Blocker 7: Workspaceboard phone send closeout`, Message-ID `<177665506931.77019.8985011316480857370@kovaldistillery.com>`, draft `drafts/blocker-7-workspaceboard-phone-send-closeout-robert-2026-04-19.txt`; asked whether Code/Git may stage, commit, and push only the narrow reviewed phone-send slice.
  - State: all listed one-by-one blocker emails are sent; waiting on Robert replies/decisions except Blocker 6, which is answered/parked until the dated 2026-04-27 11:00 AM local follow-up. No skipped blockers.
  - Boundaries observed: no external email, no mailbox state mutation beyond these approved Robert emails and local tracking, no runtime/auth/OAuth/credential/LaunchAgent/deploy/git/production changes.

- [ ] `frank-claude-backup-context-request-2026-04-19`: Waiting on Claude backup context for Workspaceboard / AI work product protection.
  - Source Message-ID: `<CAAtX44aGWoh4r0=GAM242S4H8LtoreV3tQaCuKdsiQh7Jv+5cA@mail.gmail.com>`; source subject `Backup`; classification `primary-input`; from Robert on 2026-04-19 20:20:46 CDT.
  - Sent to `claude@koval-distillery.com`, Cc `robert@kovaldistillery.com`, subject `Backup context for Workspaceboard and AI work product`, Message-ID `<177664819744.56612.7942568387030999886@kovaldistillery.com>`, draft `drafts/claude-backup-context-request-2026-04-19.txt`.
  - Robert status/approval report sent to `robert@kovaldistillery.com`, subject `Workspaceboard / AI backup status and next approvals`, Message-ID `<177664836625.57241.7623712127106052806@kovaldistillery.com>`, draft `drafts/workspaceboard-ai-backup-status-next-approvals-robert-2026-04-19.txt`; upstream sessions: AI backup planning `b6a73652`, Frank Claude request `0069937b`.
  - Status: waiting on Claude for non-secret answers about current Claude/Papers/AI workspace backup process, included/excluded categories, cadence, encryption/versioning/offsite state, restore/test-restore path, and recommended additions for Workspaceboard/Frank/Avignon/Codex. Remaining approvals before implementation: backup destination model, whether `.200` external drive is in scope, encrypted handling for sensitive machine-local state, and any restore test touching runtime or external media.
  - Boundaries observed: no `.200`/`.205` access, drive mounting, backup start, folder creation/change, Google Drive permission change, OAuth mutation, commit, push, deploy, restart, production change, credential exposure, mailbox body exposure, or sensitive-path disclosure.

- [ ] `frank-2026-salesreport-audit-summary-monday-gaps-2026-04-19`: Create Monday OPS task after OPS auth/password-reset blocker is repaired.
  - Source Message-ID: `<CAAtX44aFMW1gypQ7GGOnBKe4j2uzDm=MvwpBaqGxBzvF6A20xw@mail.gmail.com>`; dedupe key `frank-salesreport-audit-monday-gaps-CAAtX44aFMW1gypQ7GGOnBKe4j2uzDm-MvwpBaqGxBzvF6A20xw`.
  - Routed visible Frank worker/session: `58df8905`; related infrastructure/bad-gateway work is separate Workspaceboard session `f9f2b030`.
  - Email report sent to Robert: subject `Salesreport audit gaps and Monday follow-up`, Message-ID `<177663298539.20068.1942596357120237443@kovaldistillery.com>`, draft `drafts/salesreport-audit-summary-robert-2026-04-19.txt`.
  - Intended OPS task: `Fill Salesreport audit gaps from Frank summary`, due `2026-04-20`, creator `1`, owner/assignee Codex `1332`, notifications suppressed.
  - Blocker: approved helper `/Users/werkstatt/ops/scripts/create_codex_task.php` failed with `Portal access requires the mandatory security password reset`; no OPS task ID was created, and no raw DB/API bypass was performed.

- [ ] `frank-2026-04-19-outreach-macee-inbox-oauth-template-security-review`: Future/security-reviewed Macee inbox OAuth/template task for Outreach Communicator.
  - Source/date: Robert input in active Codex Integration Manager chat on 2026-04-19.
  - Owner/session: Outreach Communicator; source coordination from Frank worker `2e9c321b` and Codex Integration Manager session `b66fdade`.
  - Status: Blocked / approval-gated; no OAuth, mailbox-content read, credential access, email send, mailbox filing, Portal/CRM mutation, deploy/live pull, service restart, or runtime change is approved from this record.
  - Due date: TBD / future only after explicit Robert approval and Security Guard review; do not infer approval from the existence of this task.
  - Next step: after explicit approval, route to Security Guard first to define permitted OAuth scope, template access path, token storage class, duplicate protection, and implementation owner before Outreach Communicator or any workspace worker touches OAuth/template surfaces.
  - Approval gates: Robert explicit approval, Security Guard review, named credential/token storage path outside synced docs/git/chat, and a concrete mailbox/template action brief.

- [ ] 2026-04-20 Monday follow-up: include Mac mini hard-server-mode sequence in the Monday morning update.
  - Add alongside the Gmail polling/OAuth health follow-up.
  - Checklist for Monday discussion: wire Mac mini; turn Mac mini into hard server mode; migrate/verify critical Workspaceboard/Frank/Avignon services so logout of the Aqua/GUI session is safe; only then consider logging out the old workstation GUI session.
  - Boundary from Robert's 2026-04-19 note: record/follow up only. Do not perform service migration, logout, LaunchDaemon changes, service restarts, LaunchAgent/runtime changes, deploy/live pull, OAuth work, mailbox reads, credential access, Workspaceboard mutation, or hard-server-mode implementation from this note.

- [ ] `frank-task-manager-phone-send-five-continuations-2026-04-19`: Await Robert decisions from Task Manager update email.
  - Sent to `robert@kovaldistillery.com`, subject `Task Manager update: phone send live, five continuations routed`, Message-ID `<177664395287.47269.7385047652972662553@kovaldistillery.com>`, draft `drafts/task-manager-phone-send-five-continuations-robert-2026-04-19.txt`.
  - Complete/no further approval needed from this email: Workspaceboard phone-send rollout live; Frank/Avignon 15-second polling health check healthy.
  - Approval/decision items now waiting on Robert or Robert/Sonat: Login/Auth non-secret live config/header check; fresh Connecteam export or read-only export path; Portal docs-only commit/preserve plus later live lookup rules; Salesreport New York issue classification and optional read-only production rerun/export; AI-Bridge no-write artifact Code/Git closeout/commit-push.
  - Do not perform implementation, commits, deploys, restarts, mailbox reads, OAuth, live system changes, credential access, or mailbox mutations from this follow-up without the separate narrow approval required for that item.

## Backlog

- [ ] `frank-kive-codex-capability-comparison-later-2026-04-20`: Later / non-urgent: investigate Kive and compare it to Codex capabilities.
  - Source Message-ID: `<CAAtX44aHsgMTWqCOWBSfCSORgmps39srq=eeN=An5DBY-RHAng@mail.gmail.com>`; dedupe key `frank-kive-codex-capability-comparison-later-CAAtX44aHsgMTWqCOWBSfCSORgmps39srq-eeN-An5DBY-RHAng`.
  - Classification: `primary-forward`; source subject `Fwd: Done`; from Robert on 2026-04-20 10:38:42 CDT.
  - Work session: `019dab8c-081f-7a33-b56c-1a2ac5a2f624` / `Frank email-specific Kive TODO capture`.
  - Robert completion report sent: subject `Kive/Codex comparison TODO recorded`, Message-ID `<177669966723.64032.5543135622828542053@kovaldistillery.com>`, draft `drafts/kive-codex-comparison-todo-recorded-robert-2026-04-20.txt`.
  - Scope: record for later only; do not research Kive now. Future pass should define a concise comparison scope before starting research.
  - State: backlog / later; not urgent.

Live Papers lookup/projection remains approval-gated and is represented by AI Workspace/Papers project notes plus the Claude guidance request, not by an open Frank implementation row.

## Done

- 2026-04-20: Recorded Robert's approval for the AI Improvement Manager EOD review workflow.
  - Approval source Message-ID `<CAAtX44a_fFqVJX8Er+eRC8t_uZ0+_zzneSCVYc5EepNmtB=gTQ@mail.gmail.com>` attaches to the prior EOD follow-up source `<CAAtX44ZFzwjpws1QUxnxm8recMTXURppJL7c-VCV5Qft_Z1wjw@mail.gmail.com>`.
  - Source worker `6bf7df84` / `AI Improvement Manager EOD workflow approval activation`.
  - Approved workflow: Task Manager creates or prompts the visible `AI Improvement Manager end-of-day review` session in `ws ai`; AI Improvement Manager reads approved non-secret Markdown state and board-provided summaries at EOD and returns process-improvement recommendations for Task Manager/Frank routing.
  - Board check: no separate healthy session titled exactly `AI Improvement Manager end-of-day review` was found. No email/send/mailbox/runtime/scheduler/code/commit/push/deploy/production change was performed by this worker.

- 2026-04-20: Recorded Robert's approval of the Frank/Avignon external-sender handling directive.
  - Original plan source Message-ID `<CAAtX44YqrppVfTaoFxJqVRpNZgYy2XLWDvSeoBiwjiCyg-=eKQ@mail.gmail.com>`; blocker email Message-ID `<177665435606.75142.13942827033074478850@kovaldistillery.com>`; approval source Message-ID `<CAAtX44ZtTzCMqg-eZgO2X5rfkf+hhF2CzOzv+uyHe=T0GN7QRw@mail.gmail.com>`; confirmation source Message-ID `<CAAtX44YfMtfrf_dA69mw7uLZvuBO=j-kZraJYskdLYjrPr9gvA@mail.gmail.com>`.
  - Directive: external senders do not receive captured/routed/worker-started/completion/blocker confirmations, board/session/task status, source Message-IDs, TODO/HANDOFF details, or approval-gate language. External replies are normal business responses only; external auto-send remains disabled unless separately approved by named sender class/template.
  - Dedupe state: blocker 1 is approved/closed and should not resurface as a fresh decision unless Robert changes the directive. Docs/state only; no external email, mailbox settings, runtime/auth/credential/production/deploy/git change, or secret/private body exposure occurred.

- 2026-04-20: Sent Robert the AI Improvement Manager EOD review workflow follow-up report.
  - Source Message-ID `<CAAtX44ZFzwjpws1QUxnxm8recMTXURppJL7c-VCV5Qft_Z1wjw@mail.gmail.com>`; subject `Re: AI Improvement Manager role setup complete`; classification `tracked-primary-instruction`.
  - Source worker `590e41e5` / `AI Improvement Manager EOD review workflow`.
  - Report sent to `robert@kovaldistillery.com` only, subject `AI Improvement Manager EOD review workflow recorded`, task id `frank-ai-improvement-manager-eod-review-follow-up-2026-04-20`, Message-ID `<177670035086.68160.505116903068389250@kovaldistillery.com>`, draft `drafts/ai-improvement-manager-eod-review-follow-up-robert-2026-04-20.txt`.
  - Reported recommendation: end-of-day Markdown-file review plus board-provided summaries as the safe source model; standing visible Workspaceboard session only as a Task Manager-created/prompted review surface, not daemon/scheduler/mailbox monitor/runtime automation.
  - Exact standing session title: `AI Improvement Manager end-of-day review`.
  - Duplicate/handled status: source Message-ID is logged and the runtime automation log records it archived to `Handled`; do not resurface it as a fresh task unless Robert replies with new instructions.
  - Boundaries observed by this report session: no secrets, credentials, OAuth, mailbox content, runtime daemon, schedule, LaunchAgent, cadence, production, deploy, push, live pull, external system, or Workspaceboard runtime/organigram source change was touched.

- 2026-04-20: Sent Robert the task-specific Monday polling health verification completion report.
  - Source Message-ID `<CAAtX44ay8Bar_6e7Q50SD7hAhu4mW0_eNfhO7A1aOGYFtW-XxA@mail.gmail.com>`; subject `Re: Frank/Avignon Gmail push: OAuth and Pub/Sub setup needed`; classification `tracked-primary-instruction`.
  - Work session `b8f42d66` / `Frank Avignon Monday polling health verify`.
  - Report sent to `robert@kovaldistillery.com`, subject `Monday polling health verification complete`, task id `frank-avignon-monday-polling-health-complete-2026-04-20`, Message-ID `<177669724214.57473.7159050502453305607@kovaldistillery.com>`, draft `drafts/frank-avignon-monday-polling-health-complete-robert-2026-04-20.txt`.
  - Reported health result: `com.koval.frank-auto` and `com.koval.avignon-auto` are clean enough to proceed to a separate OAuth/PubSub planning and approval step only; implementation remains closed.
  - Remaining blocker/approval: Robert approval is needed for the M4 ERTC Google auth-context planning/design slice covering Gmail API push architecture, Google Cloud project/topic/subscription/IAM decisions, `users.watch` scope, machine-local historyId/token storage proposal, fallback polling behavior, and Security Guard review. No OAuth, Pub/Sub/IAM mutation, `users.watch`, subscriber setup, token/history work, LaunchAgent/runtime changes, mailbox-content reads, deploy, commit, push, production mutation, secrets, or mailbox bodies were touched.

- 2026-04-20: Completed Frank daily updates missing status check.
  - Source Message-ID `<CAAtX44bvRKy+y9-pc6q2YtRNxagu-v=efSToCHVZvfXTz70HDg@mail.gmail.com>`; subject `Daily morning / evening updates`; classification `primary-input`.
  - Work session `df1aa895` / `Frank daily updates missing status check`.
  - Frank catch-up reports sent to `robert@kovaldistillery.com`: Sunday EOD Message-ID `<177668493968.32295.4155531079385169941@kovaldistillery.com>` and Monday morning overview Message-ID `<177668494056.32305.7274393911093652375@kovaldistillery.com>`.
  - Robert status report sent as `Daily update send status check`, task id `frank-daily-updates-missing-status-check-2026-04-20`, Message-ID `<177668505055.32507.4537808479208625078@kovaldistillery.com>`, draft `drafts/frank-daily-updates-missing-status-check-robert-2026-04-20.txt`.
  - Evidence: local Frank/Avignon sent logs, automation logs, launch stdout/stderr timestamps, scheduled-report plist metadata, and local TODO/HANDOFF only. Avignon evidence found Sunday morning summary to Sonat Message-ID `<177659640379.52425.4125343581149672153@kovaldistillery.com>` and approved Sunday 21:42 Sonat status email Message-ID `<177665295551.68733.4913818806070436873@kovaldistillery.com>`; no Avignon Monday morning or scheduled EOD sent-log entry found.
  - Avignon catch-up session `f60904c1` / `Avignon Monday morning summary catch-up` verified Monday summary had not already sent and sent Sonat-only catch-up `Morning Summary: Monday, April 20`, task id `avignon-morning-summary-2026-04-20`, Message-ID `<177668518217.34199.10102899633008497659@kovaldistillery.com>`, no Cc/Bcc.
  - Runtime-health session `0820318c` / `Frank Avignon scheduled report runtime health` found installed plists exist and lint but jobs are enabled/not loaded as services after Mac mini reboot/logged-out state; likely primary cause is user LaunchAgents did not load after reboot/logged-out state. Secondary cause: Avignon installed plist has only 06:00 while runtime template has 06:00 and 18:00.
  - Follow-up remediation session `019dab8f-d773-7251-a525-3fc5ab0f8315` / `Frank/Avignon scheduled reports runtime remediation`: Avignon installed plist was updated to 06:00 and 18:00; Frank already had both intervals; both report helpers dry-ran without sending; labels remain enabled but not loaded because bootstrap/load requires an active Aqua/gui user session or separately approved privileged launchd action.
  - Final Robert completion report sent as `Daily updates incident final report`, task id `frank-daily-updates-incident-final-report-2026-04-20`, Message-ID `<177668560100.35356.6242739637421787200@kovaldistillery.com>`, draft `drafts/frank-daily-updates-incident-final-report-robert-2026-04-20.txt`.
  - Remaining blocker/approval: active Aqua/gui user-session reload or separately approved privileged launchd/hard-server-mode remediation is needed before the scheduled-report LaunchAgents can be confirmed loaded after logged-out reboot. No polling cadence, auth/OAuth, credential, production, deploy, git, mailbox-body, or inbox-polling-daemon mutation was performed.

- 2026-04-20: Sent Robert the AI Improvement Manager role setup completion report.
  - Source Message-ID `<CAAtX44a_J500uEU+8hpFcOHH25fmb8EHRJJAY6rjORy00=mgQQ@mail.gmail.com>`; subject `New role`; classification `primary-input`.
  - Work session `e13f147b` / `AI Improvement Manager role setup`; Code/Git closeout session `255859e8` / `Code Git closeout AI Improvement Manager role`.
  - Report sent to `robert@kovaldistillery.com`, subject `AI Improvement Manager role setup complete`, task id `frank-ai-improvement-manager-role-setup-complete-2026-04-20`, Message-ID `<177666248466.92070.288355396088470470@kovaldistillery.com>`, draft `drafts/ai-improvement-manager-role-setup-complete-robert-2026-04-20.txt`.
  - Reported docs-only role setup, ai_workspace docs changed, verification, dirty-worktree no-commit recommendation, live organigram caveat, and remaining decisions/gates. No external recipient, live automation/runtime/mail/deploy/credentials/production changes, standing session, schedule, OAuth, credential, LaunchAgent, deploy, live pull, production mutation, commit, push, or mailbox-content access was performed.
  - 2026-04-20 12:01 CDT: follow-up Code/Git closeout instruction for source session `e13f147b` confirmed no blocking findings and asked Frank to send/report completion; covered by the already-sent 00:21 Robert report above, so no duplicate email was sent.

- 2026-04-19: Drafted Frank/Avignon external-sender email handling plan for Robert review.
  - Source Message-ID `<CAAtX44YqrppVfTaoFxJqVRpNZgYy2XLWDvSeoBiwjiCyg-=eKQ@mail.gmail.com>`; subject `External`; classification `primary-input`; from Robert on 2026-04-19 22:00:37 CDT.
  - Follow-up Message-ID `<CAAtX44bJw8EtdsenzQQkrhZnNyHkxvhPKUwo_JV88sPVpmk1gQ@mail.gmail.com>`; classification `tracked-primary-instruction`; Robert instructed Frank/Avignon to wait for the visible work session before owner-facing routed/status/completion responses and include work session ID/title in those emails.
  - Work session `efea2fde` / `Frank external sender email policy plan`.
  - Existing docs already covered internal primary-owner handling and broad external-sensitive approval gates, but did not contain a category-level external-sender plan.
  - Created `external-sender-email-handling-plan.md` as a Frank-local policy draft for Frank/Avignon: external senders must not receive internal captured/routed/completion confirmations; default external handling is log/file, draft-only, visible routing, or human-approved send depending on category; no external auto-send is active without separately approved named templates; owner-facing routed-work emails must include visible session ID/title after the prompt has landed.
  - Robert completion/status report sent as `External sender handling plan drafted`, Message-ID `<177665431346.74949.5721043396667872280@kovaldistillery.com>`, draft `drafts/external-sender-handling-plan-robert-2026-04-19.txt`.
  - Boundaries: no external emails, mailbox body reads beyond supplied source context, mailbox filing/state mutation, runtime/OAuth/credential/LaunchAgent/production/deploy/git mutation, central AI Workspace policy edit, commit, push, reset, clean, or session closure.

- 2026-04-19: Confirmed Avignon sent Sonat the approved email delivery/status report and closed Robert's request.
  - Source Message-ID `<CAAtX44a0j6bXPbJNh=Q7Cmm34H91KfFZ6c2iEtLb-as8+ittxA@mail.gmail.com>`; subject `Re: Avignon runtime review complete`; Robert instruction: `we need to get sonat the emails~ approve what is necessary for that`.
  - Avignon delivery session `ceca06e7`; Avignon Code/Git closeout session `daa8d16f`.
  - Avignon sent to `sonat@kovaldistillery.com`, Cc `robert@kovaldistillery.com`, subject `Avignon email delivery status`, task id `avignon-sonat-email-delivery-status-2026-04-19`, Message-ID `<177665295551.68733.4913818806070436873@kovaldistillery.com>`.
  - Frank completion report sent to `robert@kovaldistillery.com`, subject `Avignon Sonat email delivery complete`, Message-ID `<177665316470.69726.2158923544660869612@kovaldistillery.com>`, draft `drafts/avignon-sonat-email-delivery-complete-robert-2026-04-19.txt`.
  - Remaining blockers reported exactly: CRM target/link decisions remain open; Gmail push/OAuth/Pub/Sub remains parked pending the Monday polling-health check.
  - Boundaries: no private email body content duplicated; no secrets, credentials, OAuth/token material, mailbox bodies, Avignon runtime/mailbox/auth mutation, LaunchAgent restart/cadence change, deploy, push, commit, reset, clean, session closure, Google Cloud/Pub/Sub/IAM, CRM/Portal mutation, customer/vendor external-sensitive send, or mailbox archive/state mutation by Frank.

- 2026-04-19: Completed the Avignon runtime confirmation hotfix approval thread and sent Robert the completion report.
  - Approval source Message-ID `<CAAtX44ZbSRL-xm9os0OeuBABU82PnkjAQJ16VQnqWiupkqXfmw@mail.gmail.com>`; covered follow-up `any update?` source Message-ID `<CAAtX44Zx5Q=L_A9ie7_tdwK5Ftat7=2zYcrCj5D=H5XCw7svmg@mail.gmail.com>`; original source Message-ID `<CAAtX44aTafv2TwV47RdxaH-pG-HHx-Em4CBKC0T0f69sy_6HcQ@mail.gmail.com>`.
  - Sessions: Frank `f6f9dd35`; Avignon runtime worker `880138a3`; prior Avignon audit `774c8dfb`; Code/Git Manager `f92b4b8c`; Security review `cee4abaa`.
  - Sent to `robert@kovaldistillery.com`, subject `Avignon runtime review complete`, Message-ID `<177665253964.67115.5242328108444952799@kovaldistillery.com>`, draft `drafts/avignon-runtime-confirmation-hotfix-complete-robert-2026-04-19.txt`.
  - Result reported: suspected Python 3.9 issue was not reproducible; approved scripts compiled/imported cleanly under Python 3.9.6; no installed runtime Python files changed and no backups were needed.
  - Boundaries: no Avignon email, mailbox body/state inspection or mutation, credentials/OAuth/tokens/secrets, deploy, commit, push, restart, reset, clean, session closure, or LaunchAgent cadence/restart change. Any forced live-cycle health check, restart, cadence change, or mailbox-state test remains a separate approval-gated next step.
  - No duplicate email sent for the `any update?` follow-up because this completion report was already sent just after it and answered the status question.

- 2026-04-19: Sent Robert the secure document-intake recommendation for the direct `Info / files` request.
  - Source Message-ID `<CAAtX44bQEg-xPKiLTq=t2UADFegQ1G35KG7vHcWeu-kB5YFgAg@mail.gmail.com>`; AI-Bridge design session `64ea6f84`; task id `frank-info-files-document-intake-recommendation-2026-04-19`.
  - Sent to `robert@kovaldistillery.com`, subject `Re: Info / files`, Message-ID `<177664788020.55540.7563835369641737839@kovaldistillery.com>`, draft `drafts/info-files-document-intake-recommendation-robert-2026-04-19.txt`.
  - Recommendation reported: restricted Robert-owned Google Drive intake for raw documents, paired with git-backed AI Workspace / AI-Bridge metadata for routing, source IDs, sensitivity tier, approvals, and summaries. Papers/MI remains a later approved projection/index target.
  - Approval needed: whether to set up the restricted intake folder and who initially has access: Robert only, Robert + Frank, Robert + Frank + Avignon, or broader internal group. No folders, permissions, Docs/Drive reads/downloads, mailbox content reads, OAuth changes, commits, deploys, restarts, `.205` access, production changes, secret exposure, or raw document handling was performed.

- 2026-04-19: Sent Robert the AI bridge status report for the direct `Update on AI bridge` request.
  - Source Message-ID `<CAAtX44a43fDLt5MWnN0=RFYouL9tYX6-v_0JjoaBSgJUMwm7PA@mail.gmail.com>`; AI-Bridge analysis/status session `10b2d79e`; task id `frank-ai-bridge-status-claude-integration-next-steps-2026-04-19`.
  - Sent to `robert@kovaldistillery.com`, subject `AI bridge status: Claude, integration state, next 5 steps`, Message-ID `<177664767711.54765.1039444888411215614@kovaldistillery.com>`, draft `drafts/ai-bridge-status-claude-integration-next-steps-robert-2026-04-19.txt`.
  - Status reported: Claude replied on the earlier Papers/email-text thread, but no Claude reply is locally recorded yet for the newer bridge/task-record note. Integration is design/local-record ready, not live.
  - Remaining blockers/approval gates: Claude bridge-note reply, Workspaceboard exporter ownership/Code-Git coordination, Robert/Security Guard approval for Papers read-only wrapper, and separate approval for live read-only registration. No implementation, commit, deploy, restart, mailbox read, OAuth, MCP config change, Papers/MI/.205 access, protected body read, live-system mutation, or secret exposure was performed.

- 2026-04-19: Sent Robert one Task Manager update covering Workspaceboard phone-send live rollout and five additional continuations.
  - Sent to `robert@kovaldistillery.com`, subject `Task Manager update: phone send live, five continuations routed`, task id `frank-task-manager-phone-send-five-continuations-2026-04-19`, Message-ID `<177664395287.47269.7385047652972662553@kovaldistillery.com>`, draft `drafts/task-manager-phone-send-five-continuations-robert-2026-04-19.txt`.
  - Statuses recorded: phone-send rollout complete/live under approval emails; Login/Auth classified with non-secret live config/header approval needed; OPS Connecteam read-only packet complete with fresh export/read-only export still blocked; Portal docs closeout ready with commit/live lookup approval gates; Salesreport NY audit complete with Robert/Sonat classification needed; Frank/Avignon polling health complete/healthy and Gmail push not urgent; AI-Bridge no-write package complete with Code/Git closeout/publish gates. No implementation, commit, deploy, restart, mailbox read, OAuth, live mutation, secret exposure, or credential change was performed by Frank for this report.

- 2026-04-19: Resent missed Frank completion reports in one bundled email after Robert confirmed both diagnostics were received.
  - Sent to Robert subject `Frank completion report resend bundle - 2026-04-19`, task id `frank-completion-report-resend-bundle-2026-04-19`, Message-ID `<177664151261.32260.18106833226129375414@kovaldistillery.com>`, draft `drafts/frank-completion-report-resend-bundle-robert-2026-04-19.txt`.
  - Covered Salesreport audit gaps, Claude Papers email-text follow-up, Frank/Avignon formatting, signature linked-text correction, routed task ID recording, and Python 3.9 send-helper/diagnostic status. Skipped Dmytro because Robert's acknowledgement was already logged; did not resend Sonat-only Avignon reports. No remaining blocker.

- 2026-04-19: Normalized Frank/Avignon completion-report default send path after diagnostic session `39727394`; installed `frank_paths.py` defaults now resolve to the working machine-local private credential paths and state sent-log paths for both assistants. Verified Python compile and no-send Frank/Avignon dry-runs without explicit credential/log overrides. No email, credential change/print, mailbox body read, LaunchAgent/cadence/service change, deploy, commit, or push.

- 2026-04-19: Verified Frank/Avignon Python 3.9 send-helper import repair after completion-report outage.
  - Incident: Task Manager reported Frank/Avignon send automation import crashes from `html_body: str | None = None` in installed send helpers under Python 3.9.
  - Active installed helpers inspected at `/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py` and `/Users/admin/.avignon-launch/runtime/scripts/send_frank_email.py`; both already used the Python 3.9-safe `html_body=None`, and `rg` found no remaining `| None` annotations in either file.
  - Backups preserved before verification: `/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py.bak-20260419-173920-py39-import-repair` and `/Users/admin/.avignon-launch/runtime/scripts/send_frank_email.py.bak-20260419-173920-py39-import-repair`.
  - Verification: `python3` is 3.9.6; `py_compile` passed for both helpers; script-directory import checks passed for both helpers; both helpers loaded `--help`; fresh launchd stdout advanced normally after the old 16:32 CDT error-log entries. No credentials were read/printed, no email was sent, no mailbox state changed, and no service/LaunchAgent restart was performed.
  - Send-log evidence showed the cited Frank and Avignon completion reports were already logged as sent; no resend was performed. Remaining delivery question, if Robert still did not receive them, is downstream delivery/mailbox placement rather than current helper import failure.

- 2026-04-19: Completed Frank routed task ID recording workflow.
  - Source Message-ID `<CAAtX44asa5JXGUhiF7KXuNzCC4dnfFvjGhyAXjFON62Qq=DnbA@mail.gmail.com>`; dedupe key `frank-routed-task-id-recording-CAAtX44asa5JXGUhiF7KXuNzCC4dnfFvjGhyAXjFON62Qq-DnbA`; local task id `frank-2026-04-19-routed-task-id-recording-workflow`; visible board/Codex session `bff2d116`.
  - Chosen convention: record real IDs only in a compact ID block: source Message-ID, dedupe key, local task ID, board/Codex session ID, Claude/bridge task ID when supplied, OPS/Portal task ID when created, outbound Message-ID when sent, and current status.
  - Changed files/templates: `routed-task-id-recording.md`, `scripts/frank_completion_confirmation.py`, `drafts/frank-routed-task-id-recording-complete-robert-2026-04-19.txt`, `TODO.md`, and `HANDOFF.md`.
  - Robert completion report sent as `Frank routed task ID recording workflow complete`, Message-ID `<177663408472.52512.7962573480166008562@kovaldistillery.com>`; direct source capture ack already logged as Message-ID `<177663384714.39356.12843538403633616685@kovaldistillery.com>`.
  - Claude/bridge task ID: not available in local non-secret metadata for this source; OPS/Portal task ID: none created. No OAuth/auth, mailbox private-body read, runtime cadence change, LaunchAgent mutation, deploy, push, production mutation, or invented external ID.

- 2026-04-19: Completed Frank/Avignon signature social linked-text correction.
  - Original source Message-ID `<CAAtX44Zdop6K5a=5tzQ+3u2-bFBVLs9jdfxZEsPis-LvnX5a6Q@mail.gmail.com>`; follow-up source Message-IDs `<CAAtX44a5j6hMjsF37=PBAg1aXFNPYsoKKFMq9SzPMGZ44g64LQ@mail.gmail.com>` and `<CAAtX44YU18iCXW95rzx2hzqN92UhKTZGTU+1W9k3PP_=hoxgiQ@mail.gmail.com>`; dedupe key `frank-signature-social-links-fix-CAAtX44Zdop6K5a-5tzQ-3u2-bFBVLs9jdfxZEsPis-LvnX5a6Q`; visible worker/session `9f7823b5`.
  - Amended the earlier raw-visible-URL correction: the installed helper now sends multipart text/html and the rendered HTML signature shows linked text `<a href="http://www.x.com/kovaldistillery">X</a>` for both Frank and Avignon. Avignon-specific role/contact identity remains intact.
  - Changed surfaces: `/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py`, `/Users/admin/.avignon-launch/runtime/scripts/send_frank_email.py`, and `scripts/frank_completion_confirmation.py` preview note.
  - Verification: Python compile passed; Frank and Avignon dry-run HTML alternatives both contained the X anchor and a rendered-text check confirmed the raw X URL was not visible text. No second completion report was sent after the follow-up corrections.
  - Earlier Robert completion report `Frank signature social links fixed`, Message-ID `<177663402412.48555.7577548409194901162@kovaldistillery.com>`, is superseded by this linked-text correction record. Backups: `.bak-20260419-signature-social-links` and `.bak-20260419-signature-linked-text` copies under both installed runtime script directories. No OAuth/auth, polling cadence, mailbox filing, production mutation, deploy, push, or external test email was performed.

- 2026-04-19: Completed Frank and Avignon email context/signature formatting fix.
  - Source Message-ID `<CAAtX44b2TeGjyqiz9Eu8hSt7HjyUDioP7eoVO7SQ1z4m_EKmgw@mail.gmail.com>`; dedupe key `frank-avignon-email-context-signature-fix-CAAtX44b2TeGjyqiz9Eu8hSt7HjyUDioP7eoVO7SQ1z4m_EKmgw`; visible worker/session `0636ae32`.
  - Updated installed Frank/Avignon send-helper signatures, Frank capture/decision helper body formatting, Avignon morning-summary signature behavior, and Frank dry-run completion-confirmation preview text.
  - Robert completion report sent as `Frank and Avignon email formatting fixed`, Message-ID `<177663349322.36871.5513170878204110685@kovaldistillery.com>`, draft `drafts/frank-avignon-email-context-signature-fix-complete-robert-2026-04-19.txt`.
  - Verification: Python compile passed; Frank send-helper dry-run, Avignon send-helper dry-run, Avignon morning-summary dry-run, Frank direct-capture ack preview, and Frank completion-confirmation preview all rendered 1-2 useful context paragraphs plus restored assistant signatures. No OAuth/auth, polling cadence, mailbox filing, credential change, production mutation, deploy, push, or external test email was performed.

- 2026-04-19: Completed Claude Papers access email-text follow-up.
  - Source Message-ID `<CAAtX44YrM-iyMkG220Dai+jzW2afC_S+yjaQwGXA+vaL3N-QUQ@mail.gmail.com>`; dedupe key `frank-2026-claude-ai-workspace-setup-review|CAAtX44YrM-iyMkG220Dai+jzW2afC_S+yjaQwGXA+vaL3N-QUQ`.
  - Attached to existing route/task `frank-2026-claude-ai-workspace-setup-review`, subject `Re: Thoughts on our AI workspace setup`, visible routed session `ba40b59d`.
  - Existing local route record showed Claude later resent the Papers assessment as email text on the tracked thread, source Message-ID `<666e4b258f67e6cf755422bd3a381480.claude@koval-distillery.com>`, so this worker did not send a duplicate Claude nudge.
  - Robert completion report sent as `Claude Papers email-text follow-up complete`, Message-ID `<177663320427.29902.13714328536849715424@kovaldistillery.com>`, draft source `drafts/frank-claude-papers-email-text-follow-up-complete-2026-04-19.txt`. No Papers access/read/write, auth/credential work, runtime cadence change, deploy, commit/push, or destructive action was performed.

- 2026-04-19: Sent Robert the Salesreport audit gap summary for the `Failed input` source email.
  - Task id `frank-2026-salesreport-audit-summary-monday-gaps-2026-04-19`; source Message-ID `<CAAtX44aFMW1gypQ7GGOnBKe4j2uzDm=MvwpBaqGxBzvF6A20xw@mail.gmail.com>`; routed session `58df8905`.
  - Email subject `Salesreport audit gaps and Monday follow-up`; Message-ID `<177663298539.20068.1942596357120237443@kovaldistillery.com>`; draft `drafts/salesreport-audit-summary-robert-2026-04-19.txt`.
  - OPS task creation is still blocked by the Portal auth/password-reset gate above, so no OPS task ID exists yet. No secrets, production data mutation, deploy/live pull, commit/push, runtime change, or `.205`/wb infrastructure handling was performed.

- 2026-04-19: Created Robert / Dmytro Wednesday morning calendar meeting.
  - Local task id `frank-2026-04-19-calendar-dmytro-wednesday-morning`; source Message-ID `<CAAtX44bA3wKS1KtB53ejqb9JDsfMjABCupACYOXCuqjpm3vU1A@mail.gmail.com>`; dedupe key `frank-calendar-dmytro-20260422-source-CAAtX44bA3wKS1KtB53ejqb9JDsfMjABCupACYOXCuqjpm3vU1A`; board session `da0aa3b4`.
  - Checked Robert's `robert@kovaldistillery.com` calendar free/busy for Wednesday, 2026-04-22, 09:00-12:00 America/Chicago; no busy blocks and no duplicate Dmytro event were found in that window.
  - Created `Meeting with Dmytro` for Wednesday, 2026-04-22, 09:00-09:30 America/Chicago on `robert@kovaldistillery.com`, invitee `dmytro.klymentiev@kovaldistillery.com`, event id `460utm9sh8n4qc093ao51oo2hs`, with Google attendee updates requested.
  - Completion report sent to Robert as `Dmytro calendar meeting added`, Message-ID `<177663294486.17936.11663904666152187963@kovaldistillery.com>`, draft `drafts/frank-calendar-dmytro-meeting-complete-robert-2026-04-19.txt`. No OAuth/auth setup, credential output, runtime/polling change, mailbox rule change, deploy, production mutation, or extra event details were performed.
  - Follow-up acknowledgement attached as handled/no-action: source Message-ID `<CAAtX44ZTi4=tDc8g7ji++diN3Y+REwNpn78UoPyq0dhduP5g=g@mail.gmail.com>`, subject `Re: Dmytro calendar meeting added`, Robert wrote thanks/positive acknowledgement. Do not create a new task or send another reply from this follow-up; preserve duplicate key `frank-calendar-dmytro-20260422-source-CAAtX44bA3wKS1KtB53ejqb9JDsfMjABCupACYOXCuqjpm3vU1A`.

- 2026-04-19: Sent Claude bridge nudge with Robert copied.
  - Task id `frank-2026-claude-codex-organigram-work-record-bridge-nudge`; subject `Re: Codex / Claude organigram and task-record bridge`; To `claude@koval-distillery.com`; Cc `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`; Message-ID `<177661959602.5921.17895643980954120746@kovaldistillery.com>`.
  - Target thread/source: active Claude bridge reply subject following Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`; draft source `drafts/claude-codex-organigram-work-record-bridge-nudge-2026-04-19.txt`; source Codex session `019da6be-1b3f-7df1-b11e-df7f4d23ea07`.
  - Robert was copied directly because the approved Claude bridge requirement requires Robert on Claude bridge emails; no separate Robert-only copy was needed. No Bcc, private mailbox body/secret output, .205/OAuth/Papers/MI/Portal/CRM/MCP mutation, deploy/live pull, service restart, or mailbox runtime config change was performed.

- 2026-04-19: Completed Frank inbox-zero cleanup.
  - Starting verified Frank INBOX count was `19`; final verification is `0` INBOX / `0` unread.
  - Filed old routed/handled/decision-thread residue to `Handled` with non-body closure rows in the machine-local automation log. No private body/header content, credentials, tokens, outgoing email, OAuth/auth work, service restart, deploy, live pull, Portal/CRM/Papers/MI mutation, or runtime cadence change was performed.

- 2026-04-19: Recorded Frank inbox-zero directive.
  - Frank must keep mailbox state at `0` open / `0` unread as the standing target by filing handled/no-action/already-routed/duplicate/completed mail to `Handled` after source-id logging and surfacing only one real Robert decision/blocker at a time.
  - This does not authorize credential exposure, auth/OAuth work, external-sensitive sends, finance/legal/security decisions, destructive/bulk action, production-impacting changes, suspicious-mail bypass, or private-content disclosure.

- 2026-04-19: Sent Claude bridge CC correction with Robert and Dmytro copied.
  - Sent through the approved Frank helper after explicit dry-run using the approved private credential path without printing credential material.
  - Task id `frank-2026-claude-codex-organigram-work-record-bridge-cc-follow-up`; subject `Re: Codex / Claude organigram and task-record bridge`; To `claude@koval-distillery.com`; Cc `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`; Message-ID `<177661269639.29604.14362403569930801531@kovaldistillery.com>`.
  - Draft source: `drafts/claude-codex-organigram-work-record-bridge-cc-follow-up-2026-04-19.txt`.
  - This corrected the active recipient trail after the original 09:03 Claude-only send and the 09:24 Robert-only copy. No Bcc, mailbox content read, credential exposure, OAuth/PubSub work, Portal/CRM/Papers/MI mutation, service restart, deploy, live pull, or runtime cadence change was performed.

- 2026-04-19: Finished the April 27 national outreach / Macee leave no-send checklist brief.
  - Durable checklist: `drafts/national-outreach-macee-leave-2026-04-27-checklist.txt`.
  - Scope: local draft/checklist only. No email was sent; no mailbox content was read; no mailbox filing, Portal/CRM mutation, credential access, OAuth, deploy/live pull, service restart, runtime change, or template access was performed.
  - Remaining blockers for any actual outreach: recipient/list source, content/subject, sender/persona, timing, and send authority must be explicitly approved; Security Guard review is required if the task expands into credentials, OAuth, mailbox/template access, external-sensitive outreach, or bulk sending.

- 2026-04-19: Routed Robert's Claude/Avignon CRM recovery context to visible Avignon worker.
  - Frank inbox metadata check found the relevant Robert-forwarded CRM target/link decision email, the related Frank/Workspaceboard recovery reply, and Claude-related context; private bodies were not exposed.
  - Routed non-secret context through Workspaceboard/Task Manager to Avignon worker `b583edb6`.
  - Sent Robert acknowledgment `Avignon CRM recovery Claude context routed`, task id `frank-2026-avignon-crm-claude-context-route-2026-04-19`, Message-ID `<177661099509.95877.3244850234872230469@kovaldistillery.com>`.
  - Avignon blocker review later completed and recorded that safe resolution still needs exact human CRM target answers; Frank routing is closed. No private body/secret disclosure, .205/OAuth/Papers/MI/Portal/CRM/MCP/deploy/live-pull/service/runtime mutation was performed.

- 2026-04-19: Added CC/BCC support to the installed Frank send helper and resolved the Claude bridge Robert-copy blocker.
  - Patched `/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py` and the Avignon parity copy at `/Users/admin/.avignon-launch/runtime/scripts/send_frank_email.py`.
  - New recipient behavior: `--to`, `--cc`, and `--bcc` accept repeated or comma-separated addresses; all recipients are validated against the existing primary-audience guard unless `--allow-non-primary` is explicitly used.
  - Sent-log behavior records To/Cc plus Cc/Bcc presence/count; Bcc addresses are not logged.
  - Verification: Python compile, helper `--help`, Frank guardrail rejection without `--allow-non-primary`, Frank CC/BCC dry-run with explicit approved credential path, and Avignon CC/BCC dry-run with explicit approved credential path.
  - Robert-copy resolution: original Claude-only Message-ID `<177660739756.67470.17168217427046240939@kovaldistillery.com>` cannot be retroactively CC'd, so Frank sent Robert-only post-send copy `Copy: Codex / Claude organigram and task-record bridge`, task id `frank-2026-claude-codex-organigram-work-record-bridge-robert-copy`, Message-ID `<177660868352.77456.17905572612484589347@kovaldistillery.com>`, draft source `drafts/claude-codex-organigram-work-record-bridge-robert-copy-2026-04-19.txt`, To `robert@kovaldistillery.com`, Cc none, Bcc none.
  - No unrelated mailbox polling/cadence change, Google/OAuth/PubSub work, service restart, .205/Papers/MI/Portal/CRM mutation, credential exposure, or duplicate Claude resend was performed.

- 2026-04-19: Sent Claude the Codex / Claude organigram and task-record bridge note.
  - Sent to Claude only through the approved Frank send helper before Robert's correction requiring Robert-copy/CC arrived in this session.
  - Sent-log task id: `frank-2026-claude-codex-organigram-work-record-bridge`.
  - Message-ID: `<177660739756.67470.17168217427046240939@kovaldistillery.com>`.
  - Draft source: `drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt`.
  - No credentials, private mailbox bodies, .205/OAuth/Papers/MI writes, Portal/CRM mutation, MCP exposure, deploy/live pull, service restart, mailbox/runtime config change, or Code/Git action was performed. Robert-copy/CC was later resolved by the CC/BCC helper support and Robert-only post-send copy recorded above.

- 2026-04-18: Tightened Frank copied/CC no-decision directive.
  - Robert corrected that Claude-managed/status copies where Robert is already CC'd are for Frank's awareness only, not a reason for Frank to send Robert a separate decision email.
  - Updated the Frank directive and patched installed `frank_auto_runner.py` so copied-only/no-explicit-Frank-action messages are handled before credential/auth suspicious-keyword escalation.
  - Direct requests to Frank and genuine safety/action blockers still route/escalate under existing gates. No outbound email, credential read, Google auth/OAuth/PubSub work, mailbox body print, or external-system mutation was performed.

- 2026-04-18: Parked Gmail API push/OAuth/PubSub slice until Monday health check.
  - Recorded Robert's pause directive: stay on current 15-second polling until Monday, 2026-04-20; verify polling health first; resume Gmail API push/OAuth/PubSub only from the M4 ERTC Google auth context if still needed. Docs-only; no Google auth, mailbox read, runtime cadence change, Cloud/PubSub/IAM mutation, deploy, push, live pull, credential, OPS, or external-system state changed.

- 2026-04-18: Recovered Frank monitor direct-email response behavior.
  - Patched installed machine-local `frank_auto_runner.py` so future direct Robert emails route to Workspaceboard Task Manager and send Robert-only captured/routed acknowledgements instead of silently logging.
  - Manually routed the already-logged phone issue and Gmail push/OAuth approval messages to Task Manager.
  - Sent Robert-only recovery email `Frank and Workspaceboard recovery`, task id `frank-2026-runtime-wb-recovery-2026-04-18`.
  - Verified Python compile, dry-run inbox cycle, sent-log entry, and stale stderr timestamp; no credentials were printed and no Google OAuth/Cloud mutation was performed.

- 2026-04-18: Installed Frank Gmail fast-poll runtime improvement.
  - `com.koval.frank-auto` now polls every 15 seconds instead of 60 seconds, using the existing duplicate-protected inbox cycle. True Gmail push is still blocked on Google Cloud/PubSub/IAM plus Frank Gmail API OAuth setup.
  - Follow-up auth retry at 13:20 CDT: the old local Gmailconnector OAuth client returned Google `401 deleted_client` before password or 2FA/app approval, so it cannot supply the missing Frank Gmail API token. No OAuth token, Gmail content, Google Cloud/PubSub/IAM state, credential output, or runtime change resulted from the retry.

- 2026-04-18: Sent Robert the Frank/Avignon Gmail push approval-packet decision email.
  - Local Frank task id: `frank-2026-gmail-push-approval-packet-2026-04-18`.
  - Sent Robert-only subject `Frank/Avignon Gmail push: concrete approvals needed` with Message-ID `<177652840568.70175.10644898545170796700@kovaldistillery.com>`.
  - Draft source: `drafts/gmail-push-approval-packet-robert-2026-04-18.txt`; sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`.
  - Asked Robert for concrete decisions on Google Cloud project/new project, Pub/Sub owner, Gmail API watch approval, Mac mini machine-local token/historyId storage approval, pull-subscriber/LaunchAgent/fallback sync slice approval, and MacBook setup-only vs supplemental-worker role. No Gmail push/OAuth implementation credentials, mailbox bodies, Google Cloud state, Pub/Sub/IAM, OAuth clients, LaunchAgents, runtime installs, code commits, deploys, live pulls, or mailbox filing were changed.

- 2026-04-18: Prepared BID payroll/Portal reimbursement owner-validation draft for Robert.
  - Draft source: `drafts/bid-payroll-portal-reimbursement-owner-validation-2026-04-18.txt`.
  - Created because BID local docs do not identify the payroll/reimbursement owner. The draft asks Robert to name the owner and answer the validation fields before live BID payroll/Portal validation. Draft only; no email was sent, no mailbox state changed, and no live Portal/payroll access was used.
- 2026-04-18: Recorded mandatory Frank completion-report correction.
  - Frank task-completion report email is required by default unless a task explicitly suppresses email. It must include what was done, what changed, links/session IDs/task IDs, what was not done, and remaining decisions. Frank reports to Robert by default. Docs-only; no mailbox/runtime/send/cadence/code change.
- 2026-04-18: Completed authorized Frank chief-of-staff inbox cleanup sweep.
  - Starting verified Frank INBOX/unread was `6` / `6`; filed all `6` remaining Google Ads and social media pipeline residue messages to `Handled`; final verified Frank INBOX/unread is `0` / `0`.
  - Rationale: Google Ads owner path was already closed/routed, and the social media pipeline thread was copied/FYI without a fresh Frank action request. No follow-up email, worker routing, credential output, runtime change, OPS write, or external-system action was performed.
- 2026-04-18: Recorded Frank chief-of-staff email-worker directive.
  - Frank should identify clear low-risk internal email tasks, route them to visible board-managed workers with full briefs, verify start, monitor completion, update TODO/project/handled-mail state, and send the required Robert/relevant-owner completion report. Added duplicate protection, FYI/CC filing, and 24-hour decision follow-up rules. Docs-only; no mailbox/runtime/send/cadence/code change.
- 2026-04-18: Sent Robert the live Sonat market events cost/sales report link.
  - Local Frank task id: `frank-2026-salesreport-sonat-market-events-link-2026-04-18`.
  - Sent Robert-only subject `Sonat market events report live` with Message-ID `<177651881735.71634.16718420527833151961@kovaldistillery.com>`.
  - Draft source: `drafts/sonat-market-events-report-robert-2026-04-18.txt`; sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`.
  - Included exact live link `https://koval-distillery.com/salesreport/sonat-market-events-report-2026-04-18.html` and noted source data caveats/data issues are captured in the report. No private receipt details, Salesreport files, runtime, mailbox filing, OPS, credentials, commit, push, deploy, or external recipients were touched.
- 2026-04-17: Added Frank copied/FYI no-action handling.
  - Runtime now classifies CC-only messages without an explicit Frank action request as `cc-fyi-no-action`, logs/files them as no-action, and does not send Robert a decision email for them. Updated Frank directive docs with the same rule. The current Claude social media pipeline example was filed to `Handled` without external email.
- 2026-04-17: Closed Frank's local live Papers lookup/projection row from open TODO counting.
  - Durable reason: Frank already sent Claude the guidance request `frank-2026-claude-papers-completion-reporting`, AI Workspace/project-hub records hold the live Papers approval gates, and Frank can only format supplied approved Papers URLs until a separate approved implementation slice exists. No Papers read/write, live lookup, runtime change, mailbox action, credential access, email send, commit, push, deploy, or external-system mutation was performed.
- 2026-04-17: Moved the standing Frank communication monitor out of open TODO counting.
  - The standing monitor remains live as board session `1794c370` and is governed by Frank docs/HANDOFF, but it is not a closable one-shot TODO. Receipt duplicate protection and merchant-category heuristics remain folded into the standing receipt workflow notes rather than counted as separate open tasks.
- 2026-04-17: Closed Frank's Google Ads credit/current-state email decision.
  - Robert confirmed Claude owns and is taking care of Google Ads.
  - Frank should not route this item to Robert/Sonat, keep asking for an owner, or create another internal follow-up for the same source email.
  - Source email from Claude dated 2026-04-15 16:16 CDT was filed from `INBOX` to `Handled`; local automation log received a closure row. No Google Ads login, account/spend/campaign change, credential action, or external email was performed.
- 2026-04-17: Sent Robert the Sonat market events / state sales report link.
  - Local Frank task id: `frank-2026-salesreport-sonat-market-events-link`.
  - Sent Robert-only subject `Sonat market events / state sales report` with Message-ID `<177645795951.74920.1801071343736050985@kovaldistillery.com>`.
  - Draft source: `drafts/sonat-market-events-report-robert-2026-04-17.txt`; sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`.
  - Included handoff link `/salesreport/sonat-market-events-report-2026-04-17.html` and noted that local Apache returned `500` for Salesreport pages during verification, so failed HTTP rendering may need web-server config follow-up. No Salesreport files, runtime, credentials, mailbox filing, OPS, Apache config, commit, push, deploy, or external recipients were touched.
- 2026-04-17: Recovered Frank inbox polling and one-at-a-time decision behavior.
  - `com.koval.frank-auto` verified at 60-second polling with valid private credential paths and last exit `0`.
  - Runtime now skips malformed JSONL rows, scans enough unseen mail to avoid starving older unprocessed messages, logs tracked replies locally instead of sending Robert tracked-reply review/info emails, and uses one-at-a-time decision prompts instead of batch inbox summaries.
  - Metadata check showed 39 unread/open Frank INBOX messages and 0 unlogged source IDs after recovery. No secrets or private body dumps were printed; no external email was sent.
- 2026-04-17: Sent Claude the Papers path and completion-reporting guidance request.
  - Local Frank task id: `frank-2026-claude-papers-completion-reporting`.
  - Sent Claude-only subject `Papers path and completion reporting integration` with Message-ID `<177645621706.36806.2718537434665685842@kovaldistillery.com>`.
  - Draft source: `drafts/claude-papers-completion-reporting-2026-04-17.txt`; sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`.
  - The message explicitly states that Papers remains no-write/design-only unless Robert approves live read/write, that current records live in Workspaceboard history, TODO/HANDOFF, project_hub, and important OPS tasks, and that Frank only has a supplied-real-URL Papers-link insertion hook. No Papers read/write, live lookup, projection, OPS mutation, mailbox filing, LaunchAgent/runtime config change, Robert/Sonat email, or credential output was performed.
- 2026-04-17: Closed company party member invite as handled elsewhere.
  - Robert confirmed the company party invite was already sent through Lists. Frank closed the stale local TODO only; no email, mailbox state, credentials, Lists action, or external system was touched.
- 2026-04-17: Closed narrow auto-send validation/rules TODO.
  - Evidence found: Robert's medium-independent approval, completion traceability rule, `frank_auto_runner.py` source `Message-ID` dedupe behavior, `frank_morning_overview.py` task/subject/recipient duplicate checks, dry-run completion-confirmation stable-key duplicate checks, tracked-reply correction logs, and prior internal sends logged with task ids and Message-IDs.
  - Safe rules now documented: Robert-only approved reports, task-specific completion confirmations to Robert or a relevant approved internal owner, safe tracked replies on already-approved internal threads, and concise captured/routed/blocked/completed status notes when source id, recipient, duplicate checks, and approval gates are clear.
  - Remaining blocker is runtime expansion only: no generalized completion-confirmation send engine, mailbox filing automation, LaunchAgent/polling change, new credential path, live Papers lookup/projection, or external-sensitive send is approved without a separate implementation slice. Avignon should mirror the same behavior policy for Sonat where equivalent validation evidence exists.
- 2026-04-17: Closed stale Frank Mitch archive/imapsync TODO by project-hub source of truth.
  - Local evidence still does not prove the mailbox transfer completed: the last verified count review showed incomplete archive folders even after source and destination IMAP logins were working.
  - AI Workspace/project-hub records show Robert closed the Mitch archive follow-up on 2026-04-15 without additional mailbox access, credential handling, or `imapsync`; do not rerun unless Robert explicitly reopens the mailbox-transfer work.
  - Docs/TODO/HANDOFF cleanup only; no mailbox state, credentials, emails, OPS, LaunchAgents, or external systems were touched.
- 2026-04-17: Updated Frank summary directive docs.
  - Robert clarified that morning summary means upcoming work/tasks and evening summary means accomplished tasks from Task Manager/board-completed work. Updated Frank docs/TODO/HANDOFF only; no runtime, LaunchAgent, mailbox, send, filing, credential, OPS, Papers, commit, push, deploy, or external-system state changed. Separate implementation remains needed if Frank's 18:00 runtime should consume Task Manager/board accomplishments directly.
- 2026-04-17: Sent Claude the Square/Shopify list and Google Doc links status request.
  - Local Frank task id: `frank-2026-claude-square-shopify-list-links`.
  - Sent Claude-only subject `Square/Shopify list tasks and Google Doc links` with Message-ID `<177644239753.5975.5455885630894689949@kovaldistillery.com>`.
  - Draft source: `drafts/claude-square-shopify-list-links-2026-04-17.txt`; sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`.
  - No Robert/Sonat email, Screenbox work, repo code, mailbox filing, runtime config change, or credential output was performed.
- 2026-04-17: Captured Claude's corrected Screenbox workflow guidance and sent the internal follow-up.
  - Local Frank task id: `frank-2026-claude-screenbox-workflow`; follow-up task id: `frank-2026-claude-screenbox-workflow-follow-up`.
  - Claude corrected the original Web Serfer-conflated answer after Dmytro's note; saved the corrected guidance in `screenbox-workflow-recommendations.md`.
  - Sent Claude-only subject `Re: Screenbox workflow recommendations` with Message-ID `<177644226569.3386.11486062060410989476@kovaldistillery.com>`.
  - No Robert/Sonat email, mailbox filing, repo code, Screenbox install, Playwright replacement, runtime config change, or credential output was performed.
- 2026-04-17: Produced local mail-routing audit and gap map.
  - Created `mail-routing-audit-gap-map.md` for OPS/Portal tasks `366218`, `366219`, `366220`, and `366221`.
  - Documented known routing layers, address families, local evidence, gaps, failure signals, export needs, and a conservative target model for CPanel, Google routing, Portal, Forge, and Lists.
  - Docs/TODO only: no email, mailbox/admin login, credential access, routing change, forwarder deletion, LaunchAgent edit, or external system mutation was performed.
- 2026-04-17: Defined safe PR/media-opportunity workflow for Sonat's Featured.com `PR pathways` request.
  - Created `featured-pr-pathways-workflow.md` with approval gates, owner path, intake checklist, risk triage, draft format, duplicate protection, and completion criteria. This completes the local workflow-definition task only; no external pitching, platform account work, automation, email send, mailbox mutation, credential access, or outreach was performed.
- 2026-04-17: Reduced stale Frank communication TODO queue.
  - Grouped the standing OPS/Portal/receipt monitor work, grouped receipt duplicate/category follow-ups under that parent, grouped four related mail-routing audit tasks under one parent, and folded the Avignon mirror reminder into the future assistant-behavior implementation note. Closed the stale `Introduce Frank to Sonat` reminder because local TODO/HANDOFF evidence shows Frank has already sent Sonat task-capture/status communications and preserved Sonat-facing context.
- 2026-04-17: Corrected Frank EOD schedule and signature.
  - Robert corrected that EOD should arrive at 18:00 Central and that Frank's social links should not render as angle-bracket URLs. Updated the existing LaunchAgent to 06:00/18:00, fixed runtime plain-text signature links, reloaded the LaunchAgent, verified syntax/plist/dry-run previews, and confirmed today's already-sent `frank-eod-summary-2026-04-17` sent-log entry plus duplicate-skip protection. No live EOD email was sent during this correction.
- 2026-04-17: Enabled Frank live morning/EOD daily reporting runtime.
  - Robert approved the Frank daily reporting runtime slice only. Installed runtime now uses existing Frank credentials/sent-log/send helper, corrected morning OPS selection to today's tasks plus most recent overdue fill-in tasks up to 10, includes active Frank follow-ups, and sends EOD accomplished-project/task summaries at 18:00 through the existing `com.koval.frank-morning-overview` LaunchAgent. Dry-runs passed; one EOD email was sent during enablement for 2026-04-17 and duplicate protection is active.
- 2026-04-17: Fixed Frank local daily report/task-selection slice.
  - Added dry-run `scripts/frank_daily_report.py` for morning active-task selection and one-off end-of-day completed-work summaries from approved local notes, with optional approved Papers metadata links and no send/mailbox/LaunchAgent behavior. Updated Frank docs so emailed tasks route through visible workers and the standing inbox monitor stays separate. Verified syntax plus morning/EOD dry-runs; no duplicate open Frank task was created.
- 2026-04-16: Added dry-run Frank completion-confirmation helper.
  - Added `frank/scripts/frank_completion_confirmation.py` to model a task-specific completion confirmation from a stable task id plus source `Message-ID` and/or tracked outbound `task_id`.
  - Helper writes local draft previews and `completion-confirmation-log.jsonl`, checks duplicate confirmation identifiers across local dry-run log and sent-log paths, and refuses duplicate confirmations.
  - Verified help, syntax compile, first dry-run draft/log creation, duplicate-skip behavior, and preview-only mode. No email, mailbox filing, polling cadence, LaunchAgent, Papers, runtime send hook, or credential path was touched.
  - Remaining approval before actual sends: exact SMTP/send hook, recipient policy, mailbox filing behavior, credential path, and real sent-log fields.
- 2026-04-16: Created safe Papers-link insertion hook for Frank emails.
  - Added runtime helper `/Users/admin/.frank-launch/runtime/scripts/frank_papers_links.py`.
  - Extended the installed `send_frank_email.py` with opt-in `--papers-link`, `--papers-metadata-file`, and `--papers-context-id` options so approved completion/report bodies can include real Papers URLs when supplied.
  - Morning overview behavior is unchanged because it has no completed-work section; live Papers lookup/projection remains pending approval.
  - No email, Papers write/read, LaunchAgent cadence change, inbox mutation, or credential printing was performed.
- 2026-04-16: Documented Frank completion-confirmation traceability policy.
  - Current behavior found: inbox automation dedupes by source `Message-ID`, primary instructions/forwards are logged without review spam, and morning overview duplicate-checks by task id or subject/recipient; generalized runtime completion sends are not implemented.
  - Updated Frank docs so task-specific completion confirmations require a stable OPS/Portal/local task id plus source email or tracked-send id, logging, handled marking, and duplicate suppression.
  - Docs-only change; no email, mailbox, LaunchAgent, polling cadence, Papers, runtime code, or credential state was changed.
- 2026-04-16: Documented Frank report path and runtime boundary.
  - Superseded runtime/policy note: the Mac mini `com.koval.frank-morning-overview` LaunchAgent was later approved for 06:00/18:00, and the current 2026-04-17 directive is morning = upcoming work/tasks and evening = accomplished Task Manager/board work.
  - Task-specific completion confirmations are allowed but are not recurring reports.
  - No Papers read/write hook, LaunchAgent edit, inbox polling cadence change, mailbox mutation, or credential access was performed.
- 2026-04-16: Aligned Frank completion and summary policy.
  - Frank should send one concise task-specific completion confirmation when a received task is complete.
  - Superseded cadence note: current directive as of 2026-04-17 is morning = upcoming work/tasks and evening = accomplished Task Manager/board work.
  - Verified `com.koval.frank-morning-overview` is loaded at 06:00 and last exited `0`; no runtime or mailbox change was made.
- 2026-04-16: Sent Claude the data-import/manual XLS validation-order fix handoff.
  - To: `claude@koval-distillery.com`
  - Subject: `Claude task: data-import XLS mapping validation order fix`
  - Sent-log task id: `frank-2026-claude-data-import-xls-validation-order-fix`
  - Message-ID: `<177636014994.96251.687129627683676686@kovaldistillery.com>`
  - No data-import code, live imports, DB writes, production data, uploaded XLS files, commit, or push were touched by Frank/Codex.
- 2026-04-16: Corrected Frank auto-review noise that emailed Robert about Robert's own instructions.
  - Patched the live Frank runtime to log Robert's instructions, forwards, and tracked corrections for local routing without sending a `Frank inbox review` email back to Robert.
  - Added sensitive-summary redaction in the live runner, sanitized local runtime automation/stdout logs for credential-style body fragments, verified a manual installed-environment run, and filed 14 already-handled/duplicate INBOX messages to `Handled`.
  - No outgoing email was sent, no polling cadence/LaunchAgent schedule was changed, and the standing Frank monitor was not closed.
- 2026-04-15: Added shared decision-email helper to Frank runtime.
  - The helper uses central profile routing so Frank decisions route to Robert and Avignon decisions route to Sonat while persona content stays separate.
  - No Frank decision email was sent during this helper install.
- 2026-04-15: Corrected Frank tracked-reply handling for the Claude AI workspace thread.
  - Robert clarified that Frank should answer directly and copy Robert/Dmytro where instructed instead of sending tracked-reply review emails unless Frank cannot answer.
  - Patched the live Frank runtime to read HTML-only assistant replies, log Robert instructions on the Claude thread without re-reviewing them, and answer Claude's Papers-access follow-up directly with Robert and Dmytro copied.
  - Sent Claude `Re: Thoughts on our AI workspace setup` at 19:06 CDT with Robert and Dmytro copied; verified the runner under the LaunchAgent environment returned no new unseen messages requiring action.
- 2026-04-15: Closed Frank-side tracking for Sonat's organic/sustainable online magazine concept.
  - Local Frank task id: `frank-2026-sonat-organic-sustainable-magazine`
  - Robert confirmed the work was passed to Claude, so Frank no longer tracks it as active local work.
  - Frank had already captured/filed Sonat's concept and approval context; no build, external publishing, DBA, OPS task creation, or automated outreach was started here.
- 2026-04-15: Closed Frank-side tracking for AI bridge/import workflow notes.
  - Local Frank task id: `frank-2026-ai-bridge-workflow-import`
  - Robert confirmed the related Claude/BID/import decision path is handled outside Frank.
  - Frank had already captured/filed the copied Claude thread, logged the `#1185` approval/confirmation, and closed the `#1193` approval-reminder after Robert said he already emailed Claude; no new Frank email, OPS write, BID write, or reminder was created here.
- 2026-04-15: Closed Angele old-user alias and marketing-alias routing follow-up.
  - Robert confirmed he fixed the Abby/Jordan old-user alias and marketing-alias routing items externally.
  - Frank's prior audit context was preserved, including Sonat's boundary to preserve direct vendor/customer/outreach/legal/account/Robert threads and avoid broad filters without verified routing.
  - No Gmail filter, forwarder, mailbox, Google Admin, OPS, Portal, or CPanel change was made by Frank/Codex in this closeout.
- 2026-04-15: Recovered Frank's missed 6:00 AM morning overview.
  - Mac mini stayed online; launchd showed `com.koval.frank-morning-overview` loaded but with `runs = 0` because the job had been installed/updated after the 06:00 trigger.
  - Sent Robert's overview manually at 16:51 CDT with task id `frank-morning-overview-2026-04-15` and Message-ID recorded in the machine-local sent log.
  - Reloaded the LaunchAgent with `AI_WORKSPACE_ROOT=/Users/admin/.frank-launch/runtime` so the scheduled job uses the installed Frank runtime.
  - Restored `scripts/frank_ops_digest.php` from the encrypted legacy vault into the live Frank runtime at 17:10 CDT, added `/Users/werkstatt/ops/bootstrap.php` as the preferred bootstrap path, and verified a no-send 2026-04-16 dry-run generated the OPS section with `ops_error = null`.
- 2026-04-15: OpenWrt 25.12.2 upgrade reminder closed.
  - The 2026-04-15 09:00 calendar reminder had served its purpose, and Robert later approved/flashed the custom image through the router worker path.
- 2026-04-14: Captured Frank scheduled inbox-check noise guard from AI Workspace ToDo-append.
  - Rule: do not send Robert a scheduled `Frank inbox review` / inbox-check email for every inbound message.
  - Routine messages Frank can handle, log, file, or safely ignore under standing guardrails should not generate a new schedule/check prompt.
  - Only messages Frank cannot safely handle, classify, route, or that require Robert's decision should surface as scheduled inbox-check prompts.
  - Scope: docs-only operating-rule update; no mailbox mutation, external sends, polling cadence change, or LaunchAgent change.
- 2026-04-14: Implemented Robert's Daily overview catch-up request.
  - Local Frank task id: `frank-2026-daily-overview-2026-04-14`
  - Source: Robert email to Frank, subject `Daily overview`, dated 2026-04-14.
  - Sent the Robert-only daily overview at 12:13 CDT after duplicate checks found no April 14 overview in workspace/runtime sent logs or Gmail Sent/All Mail.
  - Created Robert/admin-owned OPS tasks due 2026-04-14, notifications disabled: `366704`, `366705`, `366706`, `366707`, `366708`, `366709`, `366710`, `366711`, `366712`, `366713`.
  - Installed `com.koval.frank-morning-overview` LaunchAgent for daily 06:00 local time. It runs `~/.frank-launch/runtime/scripts/frank_morning_overview.py`, sends only to Robert, and duplicate-checks by task id/subject before sending.
  - Dry-run verification for 2026-04-15 successfully rendered Robert calendar items and OPS task digest content without sending.
  - Filed the source Daily overview email to `Handled` after all requested items were completed/logged.
- 2026-04-14: Captured Robert's Daily overview format clarification, superseded for defaults on 2026-04-16.
  - Local Frank task id: `frank-2026-daily-overview-format-clarification`
  - Source: Robert reply to `Daily Overview: Tuesday, April 14`
  - Original captured rule: end-of-day Frank work/status overview was fine at end of day; morning overview should be Robert's personal briefing with upcoming calendar, important `/ops` tasks, priorities, and blockers/follow-ups. Current 2026-04-17 directive: morning = upcoming work/tasks and evening = accomplished Task Manager/board work.
  - Acknowledgement Message-ID: `<177618772112.63529.8537942129380038656@kovaldistillery.com>`
  - Filed source reply to `Handled` after logging.
- 2026-04-14: Sent Robert a concise Daily overview for Tuesday, April 14 through the approved Frank send helper.
  - Local Frank task id: `frank-2026-daily-overview-2026-04-14`
  - To: Robert only
  - Subject: `Daily Overview: Tuesday, April 14`
  - Draft source: `drafts/daily-overview-robert-2026-04-14.txt`
  - Sent-log Message-ID: `<177618680531.11061.10268802423575511091@kovaldistillery.com>`
  - Note: overview content used safe internal summary only: inbox counts/categories, today's Frank sent/logged items, waiting/escalated categories, and next actions.
- 2026-04-14: Reconfigured the existing approved `com.koval.frank-auto` LaunchAgent to poll Frank every `300` seconds in `draft-only` mode; verified same label loaded/enabled with plist/run interval `300` and last exit code `0`.
- 2026-04-13: Sent Robert's approved detailed AI workspace setup review request to Claude, copying Robert and Dmytro.
  - Local Frank task id: `frank-2026-claude-ai-workspace-setup-review`
  - To: `claude@koval-distillery.com`
  - Cc: Robert and Dmytro
  - Draft source: `drafts/claude-ai-workspace-setup-review-2026-04-13.txt`
  - Sent-log Message-ID: `<177613497877.99161.593567773976868219@kovaldistillery.com>`
- 2026-04-13: Sent the approved internal Lists closeout email for `phpList CRM activity logging workflow`.
  - Local Frank task id: `frank-2026-phplist-crm-activity-logging-closeout`
  - Recipients: Robert, Sonat, Mark, Sebastian, Dmytro
  - Draft source: `drafts/phplist-crm-activity-logging-workflow-closeout-2026-04-13.txt`
  - Sent-log Message-ID: `<177613481906.89489.8467501982353652777@kovaldistillery.com>`
- 2026-04-13: Sent Robert the internal completion email for the `Shipped vs bottled mismatches` Warehouse report after Portal worker `80cf447e` closed and Robert confirmed the live link.
  - Local Frank task id: `frank-2026-portal-shipped-bottled-report-link`
  - Live link sent: `https://portal.koval-distillery.com/`
  - Draft source: `drafts/shipped-vs-bottled-warehouse-report-live-2026-04-13.txt`
  - Sent-log Message-ID: `<177608734917.30626.1836157099638920412@kovaldistillery.com>`
- 2026-04-13: Sent Robert the corrected full URL for the `Shipped vs bottled mismatches` Warehouse report after he replied that the main Portal URL was not enough.
  - Local Frank task id: `frank-2026-portal-shipped-bottled-report-link-full-url`
  - Full URL sent: `http://portal.koval-distillery.com:8082/#/warehouse/inventory/shipped-vs-bottled-mismatches`
  - Draft source: `drafts/shipped-vs-bottled-warehouse-report-full-link-2026-04-13.txt`
  - Sent-log Message-ID: `<177610883900.62641.14622966549703577447@kovaldistillery.com>`
- 2026-04-12: Cleaned Frank INBOX under Robert's standing inbox-cleanliness direction. Processed `27` unread messages and archived all `27` to `Handled`; post-pass INBOX counts were total `0`, unread `0`.
  - Closed the Macee Outreach calendar workflow item after Robert replied that he sent the email to Macee per Frank's draft and Frank can close it.
  - Captured Sonat's organic/sustainable online magazine concept as local task `frank-2026-sonat-organic-sustainable-magazine`, sent Sonat a concise internal captured-for-discovery status update, and filed the related source thread messages.
  - Captured the Claude/Codex bridge and import-workflow notes as local task `frank-2026-ai-bridge-workflow-import`; no live OPS write was attempted from this MacBook-only pass.
  - Filed already-handled Robert task-flow confirmations, Frank signature/loop-guard confirmations, and internal Claude/Codex thread copies after their substance was captured locally.
- 2026-04-12: Sent Robert the Macee Outreach calendar workflow draft for review through the Frank send helper.
  - Local Frank task id: `frank-2026-macee-outreach-calendar-workflow`
  - Draft source: `drafts/macee-outreach-calendar-workflow-2026-04-12.txt`
  - Robert review body: `drafts/macee-outreach-calendar-workflow-robert-review-2026-04-12.txt`
  - Sent-log Message-ID: `<177600276984.98113.230012419335998640@kovaldistillery.com>`
  - Macee was not contacted because her email address is missing locally.
- 2026-04-12: Handled Sonat's `PR pathways` email to Frank under the medium-independent low-risk internal workflow. Created local task `frank-2026-sonat-pr-pathways-featured`, sent Sonat a concise captured-for-follow-up status update from Frank, and archived the source email to `Handled` after verification (`INBOX` count `0`, `Handled` count `1` for the source Message-ID). Live OPS task creation was deferred because the Mac mini/router path was unavailable and this MacBook session used the local fallback.
- Recorded Robert's 2026-04-12 approval for medium-independent Frank/Avignon task flow: clearly bounded low-risk internal email tasks can be ingested, routed, executed, logged, and filed without waiting in the inbox; higher-risk/ambiguous categories still require approval.
- Checked MacMini Frank mailbox/logs on 2026-04-11; Robert's reply to `Frank persona blurb` was received at 13:55 CDT, incorporated into `PERSONA.md`, and Frank sent Robert `Frank task-flow decision options` at 18:14 CDT with task id `frank-decision-options-task-flow-2026-04-11`.
- Archived Robert's handled `Fwd: Vacation request from Jack Dempsey` source email from Frank INBOX to `Handled` on 2026-04-11 after verifying Portal request ID `1104` was approved; post-archive verification showed INBOX count `0`, `Handled` count `1` for the source Message-ID.
- Added Robert's standing handled-mail archive directive to `WHAT_TO_DO.md`: Frank may auto-archive clearly handled/resolved emails, but not ambiguous, unprocessed, externally-sensitive, or still-needs-decision messages.
- Approved Jack Dempsey's routine Portal vacation/leave request on 2026-04-11 after Robert approved proceeding: request ID `1104`, leave type `PLA`, date `2026-04-11`, requested/approved `6.00` hours, `0.00` unpaid, note `Family crisis`; Portal returned success and verified status `Approved`, updated by `Agent Codex`.
- Added Robert's future routine vacation approval directive to `WHAT_TO_DO.md`: when Robert forwards/sends Frank a routine Portal vacation/leave request to approve, Frank may approve it automatically, but must stop for ambiguity, destructive/non-routine cases, or mismatched request details.
- Started Frank persona/reference file at `PERSONA.md`; Robert persona-blurb outreach was sent from Mac mini on 2026-04-11 with task id `frank-2026-persona-blurb` after duplicate checks.
- Added Frank machine-handoff guideline at `MACHINE_HANDOFF.md`: Mac mini is the single writer for mailbox send/check actions; other sessions may draft and transfer non-secret drafts only.
- Created Frank mailbox communication profile and templates.
- Added tracked outbound send logging and inbox reply monitoring.
- Added OPS digest generation for Robert's open OPS tasks.
- Added receipt autodraft workflow.
- Added Portal receipt automation with wallet alias handling and receipt-email archiving.
- Added scheduled draft-only inbox automation scripts and LaunchAgent installer/uninstaller.
- Installed the Mac mini `draft-only` LaunchAgent with a local runtime under `~/.frank-launch` to avoid launchd permission issues on Google Drive paths.
- Enforced Robert-only scope by default in Frank email send and autodraft paths.
- Added richer inbox classification so scheduled review can log Robert test/info replies without escalating them.
- Added an explicit scheduled-review loop guard so replies to `Frank inbox review...` / `*-auto-escalation` review messages are logged as local follow-up instead of being re-escalated, and parameterized the runner for Avignon/Sonat use.
- Sent Dmytro the meeting update for Thursday, April 9, 2026 at 2:00 PM Central.
- Sent Robert a standard-format tomorrow overview for Friday, April 10 using Frank calendar data plus due-tomorrow `/ops` tasks.
- Cleaned up Angele's inbox by archiving `5,277` clear newsletter / bulk-mail messages from recurring promo senders; `abby.boler@kovaldistillery.com` was not present in inbox.
- Follow-up Angele review found direct delivery of old-user alias mail for `abby.boler@kovaldistillery.com` and `jordan.wimby@kovaldistillery.com`, archived another `197` clear promo/newsletter messages, and identified several likely unreplied external threads that need human review.
- Manual Angele review on April 10, 2026 confirmed no Angele Sent Mail matches for recent outreach from Sofia Newgren / Choose Chicago, Zach Sattaur / Heritage Fire, Steve Stelter / Gen X Plorations, Valerie Bomar, or Allison Berg / The Bulletin.
- Verified Angele cleanup pass on April 10, 2026 moved another `93` obvious alias-routed newsletter / event-promo messages into `Newsletters`, reducing inbox from `15,573` to `15,479`, unread from `6,073` to `5,983`, `abby.boler@kovaldistillery.com` hits from `2,083` to `2,012`, and `jordan.wimby@kovaldistillery.com` hits from `334` to `311`.
- Verified a second Angele cleanup pass on April 10, 2026 moved `11` alias-routed KOVAL promo emails into `Newsletters`, reducing inbox to `15,470`, unread to `5,976`, `abby.boler@kovaldistillery.com` hits to `2,007`, and `jordan.wimby@kovaldistillery.com` hits to `305`.
- Verified a third Angele cleanup/review pass on April 10, 2026 filed handled `KOVAL Inquiry: Marketing Inquiry` conversation messages into `Contact Forms`, reducing inbox to `15,449`, marketing alias hits to `177`, and remaining `KOVAL Inquiry: Marketing Inquiry` inbox messages to `201`.
- Verified a fourth Angele cleanup pass on April 10, 2026 moved another conservative batch of obvious alias-routed newsletter, promo, and platform-notification mail into `Newsletters`, reducing inbox to `15,347`, unread to `5,895`, `abby.boler@kovaldistillery.com` hits to `1,928`, and `jordan.wimby@kovaldistillery.com` hits to `291`.
- Verified an additional conservative Angele cleanup pass on April 10, 2026 moved `4` remaining Abby-alias National Honey Board promo emails into `Newsletters`, reducing inbox to `15,343`, unread to `5,892`, and `abby.boler@kovaldistillery.com` hits to `1,924`.
- Verified a follow-up conservative Angele cleanup pass on April 10, 2026 moved another `43` obvious alias-routed newsletter / event-promo messages into `Newsletters`, reducing inbox to `15,300`, unread to `5,850`, `abby.boler@kovaldistillery.com` hits to `1,883`, and `jordan.wimby@kovaldistillery.com` hits to `289`.
- Verified an additional conservative Angele cleanup pass on April 10, 2026 moved `8` more alias-routed notification / event-promo messages into `Newsletters`, reducing inbox to `15,292`, unread to `5,843`, and `abby.boler@kovaldistillery.com` hits to `1,875`.
- Verified an additional conservative Angele cleanup pass on April 10, 2026 moved another bulk/newsletter Abby-alias batch into `Newsletters`, reducing inbox to `15,232`, unread to `5,791`, and `abby.boler@kovaldistillery.com` hits to `1,815`.
- Verified a handled-mail Angele cleanup pass on April 10, 2026 filed `19` remaining Sonat-sent `Re: KOVAL Inquiry: Marketing Inquiry` copies into `Contact Forms`, reducing inbox to `15,213` and remaining `KOVAL Inquiry: Marketing Inquiry` subject-family messages in inbox to `174`.
- Verified an additional Angele cleanup pass on April 10, 2026 using a Gmail-safe label-plus-archive method for `Newsletters`, archiving another `155` clearly safe alias-routed newsletter / promo / notification messages and reducing inbox to `15,058`, unread to `5,674`, `abby.boler@kovaldistillery.com` hits to `1,708`, and `jordan.wimby@kovaldistillery.com` hits to `241`.
- Verified a further Angele cleanup pass on April 10, 2026 using the same Gmail-safe `Newsletters` archive method, archiving another `83` clearly safe alias-routed newsletter / promo messages and reducing inbox to `14,975`, unread to `5,600`, `abby.boler@kovaldistillery.com` hits to `1,672`, and `jordan.wimby@kovaldistillery.com` hits to `194`.
- Verified a broader newsletter-focused Angele cleanup pass on April 10, 2026 using the same Gmail-safe `Newsletters` archive method, archiving another `224` clearly safe newsletter / bulk-promo messages and reducing inbox to `14,751`, unread to `5,442`, `abby.boler@kovaldistillery.com` hits to `1,450`, and `jordan.wimby@kovaldistillery.com` hits to `192`.
- Verified an explicit Gmail label-operation test set on April 10, 2026 using `info@email.worlddrinksawards.com`: `18` inbox messages went to `0` after adding `Newsletters`, marking `\\Deleted` while selected in `INBOX`, and expunging. Then archived another `1,094` clearly safe newsletter / bulk messages with the same method. Final verified counts: inbox `13,640`, unread `4,650`, `abby.boler@kovaldistillery.com` hits `1,365`, `jordan.wimby@kovaldistillery.com` hits `192`, marketing alias hits `177`, and `KOVAL Inquiry: Marketing Inquiry` messages `174`.
- Verified a residual Angele newsletter cleanup pass on April 10, 2026 archived another `60` clearly safe newsletter / list / bulk messages with the same Gmail-safe method, reducing inbox to `13,580`, unread to `4,603`, `abby.boler@kovaldistillery.com` hits to `1,364`, and leaving `jordan.wimby@kovaldistillery.com`, marketing alias, and `KOVAL Inquiry: Marketing Inquiry` counts unchanged.
- Verified a high-confidence list-header Angele newsletter cleanup pass on April 10, 2026 archived another `1,698` clearly safe newsletter / bulk / promotional messages with the same Gmail-safe method, reducing inbox to `11,882`, unread to `3,249`, `abby.boler@kovaldistillery.com` hits to `603`, `jordan.wimby@kovaldistillery.com` hits to `162`, and marketing alias hits to `169`; `KOVAL Inquiry: Marketing Inquiry` count remained `174`.
- Verified a more aggressive Angele newsletter/promotional cleanup pass on April 10, 2026 archived another `314` newsletter / promotional messages with the same Gmail-safe method while skipping `Re:` and `KOVAL Inquiry: Marketing Inquiry` subjects, reducing inbox to `11,568`, unread to `3,005`, `abby.boler@kovaldistillery.com` hits to `502`, and `jordan.wimby@kovaldistillery.com` hits to `158`; marketing alias hits remained `169`.
- Verified a Qwoted list-alert Angele cleanup pass on April 10, 2026 archived another `667` list-style alert messages with the same Gmail-safe method, reducing inbox to `10,901` and unread to `2,779`; `abby.boler@kovaldistillery.com` hits remained `502`, `jordan.wimby@kovaldistillery.com` hits remained `158`, and marketing alias hits remained `169`.
- Verified an old-mail Angele newsletter cleanup pass on April 10, 2026 archived `57` clearly stale newsletter / bulk / promo messages older than one year with the same Gmail-safe method, reducing inbox to `10,844`, unread to `2,724`, `abby.boler@kovaldistillery.com` hits to `476`, and `jordan.wimby@kovaldistillery.com` hits to `152`; marketing alias hits remained `169`.
- Verified a six-month old-mail Angele archive pass on April 10, 2026 archived `7,021` INBOX messages older than `2025-10-10`, reducing inbox to `3,823`, unread to `1,376`, `abby.boler@kovaldistillery.com` hits to `125`, `jordan.wimby@kovaldistillery.com` hits to `37`, and marketing alias hits to `95`.
- Verified a remaining-inbox classification pass on April 10, 2026 sampled representative content and archived `419` handled/stale automated messages, reducing inbox to `3,405`, unread to `1,124`, `abby.boler@kovaldistillery.com` hits to `126`, `jordan.wimby@kovaldistillery.com` hits to `26`, and marketing alias hits remained `95`.
- Verified approved CRM cleanup on April 10, 2026 archived `319` remaining `crm@koval-distillery.com` messages after Robert approved archiving CRM orders/check-ins/general CRM messages, reducing inbox to `3,086` and unread to `965`; `abby.boler@kovaldistillery.com` hits remained `126`, `jordan.wimby@kovaldistillery.com` hits remained `26`, and marketing alias hits remained `95`.
- Verified approved Qwoted and KOVAL Inquiry cleanup on April 10, 2026 archived `631` unique Qwoted media opportunity alert and KOVAL inquiry/direct reply messages after Robert approved those categories, reducing inbox to `2,495`, unread to `505`, `abby.boler@kovaldistillery.com` hits to `120`, `jordan.wimby@kovaldistillery.com` hits remained `26`, and marketing alias hits to `90`.
- Created OPS/Portal task `366462` for Sonat due `2026-04-12` to review the Angele inbox cleanup and respond to Avignon with how to proceed; Avignon emailed Sonat on April 10, 2026 with Codex session `56fd7397`, latest counts, preserved categories, and the task id.
