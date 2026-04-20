# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260418-FRANK-AVIGNON-GMAIL-PUSH-01`
- Date Opened: 2026-04-18
- Date Completed:
- Owner: AI Workspace / Frank / Avignon / Security Guard
- Priority: Medium
- Status: OAuth continuation blocked before execution pending approved Frank/Avignon token storage path/storage class and exact minimum Gmail API scope; OAuth client/source metadata is approved; 15-second polling remains active as backup

## Scope

Assess whether Frank and Avignon should move from short-interval inbox polling toward Gmail API push notifications, without exposing secrets. After Robert's explicit approval for the Gmail push/OAuth/PubSub/subscriber/runtime slice, inspect what can be completed locally and implement the closest safe improvement that reduces delay now if true push remains blocked.

This pass used local non-secret docs/runtime metadata and official Google documentation only. It did not read credential files, OAuth tokens, mailbox bodies, keychain material, `.env` files, or machine-local private runtime state.

## Current State

- Frank and Avignon currently use machine-local LaunchAgent polling, not Gmail API push.
- 2026-04-18 11:11 CDT runtime update: `com.koval.frank-auto` and `com.koval.avignon-auto` were changed from `StartInterval` `60` seconds to `15` seconds, reloaded, enabled, and kickstarted. Both loaded jobs now report `run interval = 15 seconds` and `last exit code = 0`.
- 2026-04-18 13:42 CDT pause from Robert: keep the current 15-second polling path until Monday, 2026-04-20. On Monday, verify polling health first, then resume Gmail API push/OAuth/PubSub only from the M4 ERTC Google auth context if still needed.
- Earlier LaunchAgent backup metadata showed `com.koval.frank-auto` and `com.koval.avignon-auto` at 300 seconds in the 2026-04-15 backup; later handoff notes recorded a 2026-04-17 runtime change to 60 seconds. Robert's 2026-04-18 approval allowed inspecting and updating the current live LaunchAgent files under `/Users/admin` for this slice.
- Frank runtime uses Gmail SMTP for outbound mail and IMAP-style inbox checks/filing through machine-local credential references. Avignon mirrors this with its own machine-local credential path.
- Frank has Google Calendar OAuth client/token references for calendar work, but no local evidence shows Gmail API OAuth tokens for Frank/Avignon inbox monitors.
- `/Users/werkstatt/Gmailconnector` is a separate Gmail API OAuth read-only search/export tool. It uses `gmail.readonly`, stores per-account tokens under `gmail/_private/tokens`, and has no local evidence of `users.watch`, Pub/Sub, `history.list`, Frank, or Avignon integration. Existing token metadata found local tokens for Robert, Sonat, Oleg, and Sebastian, but not for `frank.cannoli@kovaldistillery.com` or `avignon.rose@kovaldistillery.com`.
- No local non-secret evidence was found for an existing Gmail Pub/Sub topic, subscription, Gmail `users.watch` state, persisted Gmail `historyId`, watch renewal job, or `gcloud` CLI.

## Official Google Behavior Reference

- Gmail push notifications require an initial Cloud Pub/Sub setup with a topic, subscription, and publish permission for `gmail-api-push@system.gserviceaccount.com`.
- The Gmail `users.watch` request can filter to `labelIds: ["INBOX"]` with `labelFilterBehavior: "INCLUDE"` and returns a `historyId` plus `expiration`.
- The Pub/Sub topic must already exist, and the project id in `topicName` must match the Google developer project executing the watch request.
- Gmail watches must be renewed at least every 7 days; Google recommends renewing daily.
- Gmail notification payloads include the mailbox email address and new `historyId`; processing then uses `users.history.list` from the last persisted `historyId`.
- Gmail notifications can be delayed or dropped and are capped at one event per second per watched user, so a fallback periodic `history.list` sync is required.
- `users.history.list` can return `HTTP 404` when `startHistoryId` is too old or invalid; that must trigger a full sync/rebaseline.
- Pub/Sub push subscriptions deliver HTTPS POSTs to a publicly addressable endpoint. Authenticated push subscriptions send a Google-signed JWT that the subscriber should validate.

Official docs:

- Gmail push guide: https://developers.google.com/workspace/gmail/api/guides/push
- Gmail `users.watch`: https://developers.google.com/workspace/gmail/api/reference/rest/v1/users/watch
- Gmail `users.history.list`: https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.history/list
- Pub/Sub push subscriptions: https://cloud.google.com/pubsub/docs/push
- Pub/Sub push authentication: https://docs.cloud.google.com/pubsub/docs/authenticate-push-subscriptions

## Smallest Safe Architecture

Recommended first implementation is pull-subscriber based, not public-webhook based:

1. Create or choose one approved Google Cloud project for Frank/Avignon Gmail push.
2. Enable Gmail API and Pub/Sub API.
3. Create one Pub/Sub topic, for example `projects/<project-id>/topics/frank-avignon-gmail-inbox`.
4. Grant `roles/pubsub.publisher` on that topic to `gmail-api-push@system.gserviceaccount.com`.
5. Create one pull subscription, for example `frank-avignon-gmail-inbox-pull`.
6. Use per-mailbox OAuth tokens with the narrowest acceptable Gmail scope, preferably `gmail.metadata` if the existing classifiers can fetch only headers/metadata, otherwise `gmail.readonly` for read-only message metadata/body needs. Any broader scope requires Security Guard review.
7. Call `users.watch` separately for Frank and Avignon with `labelIds: ["INBOX"]`, `labelFilterBehavior: "INCLUDE"`, and the approved topic name.
8. Persist one state record per mailbox in machine-local state, not git or Google Drive: current `historyId`, watch expiration, last notification time, last successful fallback sync, and processed Gmail message/thread/source ids.
9. A Mac mini subscriber process pulls Pub/Sub messages, decodes notification data, verifies the mailbox is expected, runs `users.history.list(startHistoryId=<stored>)`, fetches only needed message metadata, then feeds the existing Frank/Avignon classification/routing path.
10. Persist the new history baseline only after processing succeeds.
11. Keep a fallback periodic sync, for example every 5-15 minutes, that calls `history.list` if no notification arrived recently or after subscriber downtime.
12. Run daily watch renewal for both accounts and record expiration timestamps.
13. Deduplicate by Gmail `message.id`, thread id, normalized `Message-ID` header, mailbox, and current Frank/Avignon automation-log dedupe keys.
14. Completion workflow remains unchanged: create/reroute visible Task Manager worker sessions for substantive work, verify start, monitor completion, log handled state, and send the required owner completion report when gates allow.

Push webhook alternative:

- Use only if there is an approved authenticated HTTPS endpoint, such as Cloud Run or an already approved Workspaceboard route with Portal allowlist plus Pub/Sub JWT validation.
- Do not expose a new public unauthenticated Mac mini endpoint. LAN-only Workspaceboard endpoints are not sufficient for Pub/Sub push unless fronted by an approved public HTTPS service.

## Blockers

### Pause Boundary Through Monday 2026-04-20

Robert paused the Gmail push slice on 2026-04-18. Before Monday approval/reopen:

- No Google Cloud/Pub/Sub/IAM mutation.
- No OAuth token work.
- No mailbox content read.
- No runtime cadence change.
- No deploy, push, or live pull for the Gmail push slice.
- No further Google auth changes unless Robert explicitly reopens the slice.

Monday first action: verify the health of current 15-second polling for Frank and Avignon, including LaunchAgent loaded interval, last exit, recent run timestamps, stderr/stdout health, duplicate protection, and primary-input captured/routed acknowledgements. Only after that health check should Task Manager decide whether true Gmail push is still needed.

Monday morning update addition from Robert on 2026-04-19: include the Mac mini hard-server-mode item alongside this Gmail polling/OAuth health follow-up. The update should cover wiring the Mac mini, planning hard server mode, migrating/verifying critical Workspaceboard/Frank/Avignon services so logout of the Aqua/GUI session is safe, and only then considering logout of the old workstation GUI session. This note does not approve service migration, logout, LaunchDaemon changes, service restarts, runtime cadence changes, deploy, push, or live pull.

- Security Guard approval is required for the exact Gmail API scope per mailbox: `gmail.metadata` if headers/metadata are enough, `gmail.readonly` only if message body access is explicitly required, and any broader scope requires a separate review.
- Security Guard approval is required for OAuth/token handling: token storage must be machine-local private storage, OS keychain, or another named approved secret store; no Google Drive-synced path, git path, project-hub record, normal log, chat, or mailbox note is approved for OAuth material.
- Google Cloud owner approval is required for the exact Google Cloud project id and confirmation that Gmail API and Pub/Sub API are enabled there, or explicit authorization to enable them.
- Google Cloud owner approval is required for the Pub/Sub topic/subscription: either provide existing non-secret resource names, or authorize creation of one topic and one pull subscription for Frank/Avignon Gmail inbox notifications.
- Google Cloud owner/Security Guard approval is required before granting `roles/pubsub.publisher` on the approved topic to `gmail-api-push@system.gserviceaccount.com`.
- OAuth app owner approval is required to either reuse an existing OAuth client only when owner/scope/user-consent boundaries match this Gmail-push purpose, or create a dedicated Gmail-push OAuth client.
- Runtime owner approval is required for where the subscriber and state live: existing Frank/Avignon machine-local runtime, Workspaceboard runtime, or a separate approved Mac mini subscriber.
- Runtime owner approval is required for the exact machine-local state directory that will hold non-secret operational state such as current `historyId`, watch expiration, last notification time, fallback-sync timestamp, and dedupe ids.
- Runtime owner approval is required before installing or changing any LaunchAgent, daemon, subscriber schedule, daily watch-renewal job, webhook endpoint, Cloud Run service, or fallback sync cadence.
- Code and Git Manager approval is required before any runtime-code patch is committed, pushed, deployed, live-pulled, or reloaded.

## Approval Packet Cleanup

Updated: 2026-04-18 11:04 CDT.

This cleanup did not change runtime, credentials, mailbox state, Google Cloud state, OAuth scopes, Pub/Sub resources, LaunchAgents, daemons, webhooks, Cloud Run, or source code. It only restated the approval packet in local docs.

Robert later directed that this should not remain only as local `needs input`. Frank sent Robert-only subject `Frank/Avignon Gmail push: concrete approvals needed` at 2026-04-18 11:06 CDT with task id `frank-2026-gmail-push-approval-packet-2026-04-18` and Message-ID `<177652840568.70175.10644898545170796700@kovaldistillery.com>`.

### Exact Non-Secret Approvals Still Required

1. Security Guard must approve the Gmail API scope for Frank and Avignon: `gmail.metadata`, `gmail.readonly`, or a separately reviewed broader scope.
2. Security Guard must approve the OAuth/token storage class and path category, limited to machine-local private storage, OS keychain, or another named approved secret store.
3. Google Cloud owner must provide or approve the Google Cloud project id for this work.
4. Google Cloud owner must confirm Gmail API and Pub/Sub API are enabled in that project, or approve enabling them.
5. Google Cloud owner must provide existing Pub/Sub topic/subscription names or approve creating one topic and one pull subscription for Frank/Avignon Gmail inbox notifications.
6. Google Cloud owner and Security Guard must approve the Pub/Sub IAM grant allowing `gmail-api-push@system.gserviceaccount.com` to publish to the approved topic.
7. OAuth app owner must approve reusing an existing OAuth client for this purpose, or approve creating a dedicated Gmail-push OAuth client.
8. Runtime owner must approve the subscriber placement: existing Frank/Avignon runtime, Workspaceboard runtime, or separate Mac mini subscriber.
9. Runtime owner must approve the machine-local state directory category for `historyId`, watch expiration, notification timestamps, fallback-sync timestamps, and dedupe ids.
10. Runtime owner must approve any LaunchAgent, daemon, subscriber schedule, daily watch-renewal job, fallback sync cadence, webhook endpoint, or Cloud Run service before installation or change.
11. Code and Git Manager must review any runtime-code patch before commit, push, deploy, live pull, reload, or worker closeout.

### Explicitly Not Approved

- No credential/token reads, printing, copying, validation, storage migration, or OAuth consent flow.
- No mailbox body reads, message filing, sent-mail action, label mutation, or mailbox state mutation.
- No Google Cloud console/API mutation, Pub/Sub topic/subscription creation, IAM change, API enablement, OAuth-client change, or app-verification change.
- No public endpoint, webhook, Cloud Run service, subscriber daemon, LaunchAgent, runtime reload, or watch-renewal job.
- No code implementation, commit, push, deploy, live pull, or source-task closure.

## 2026-04-18 Runtime Fast-Poll Slice

Robert explicitly approved Gmail push/OAuth/PubSub/subscriber/runtime/LaunchAgent/token/historyId storage as needed for near-instant Frank/Avignon email handling. Local inspection still found no usable Frank/Avignon Gmail API OAuth tokens and no local Google Cloud/PubSub admin surface. Therefore true Gmail `users.watch` / `users.history.list` could not be completed safely from this machine.

Immediate improvement installed:

- Changed `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist` `StartInterval` from `60` to `15`.
- Changed `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist` `StartInterval` from `60` to `15`.
- Created rollback backups:
  - `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist.bak-20260418-gmail-fastpoll`
  - `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist.bak-20260418-gmail-fastpoll`
- Reloaded, enabled, and kickstarted both LaunchAgents in `gui/501`.
- The kickstarted live cycles used the existing approved inbox runners and may process current inbox items under the established duplicate-protected rules. No private message content is recorded here.
- No OAuth token, app password, mailbox body, Gmail API message content, Pub/Sub resource, Google Cloud IAM, public endpoint, webhook, subscriber daemon, code repo, commit, push, deploy, or live pull was changed.

This is a safe equivalent, not true push. New mail is now checked by the existing duplicate-protected IMAP inbox cycle about every 15 seconds, using the existing automation logs, handled-mail filing rules, decision/completion routing, and persona-specific behavior.

Exact one-step blocker for true push:

- The Google/OAuth owner must provide or authorize the complete Frank/Avignon Gmail push setup bundle: a Google Cloud project with Pub/Sub topic, pull subscription, and `gmail-api-push@system.gserviceaccount.com` publisher IAM, plus Gmail API OAuth authorization for `frank.cannoli@kovaldistillery.com` and `avignon.rose@kovaldistillery.com` with the minimum approved Gmail scope. Once that bundle exists, the next implementation step is to install the pull subscriber/watch-renewal/historyId processor in the same machine-local runtime.

## Repo Logs

### ai_workspace

- Repo Log ID: local planning update
- Commit SHA: uncommitted
- Commit Date:
- Change Summary: Recorded Gmail push feasibility/design, official-doc behavior, blockers, and follow-up tasks. No credentials, mailbox contents, runtime state, Google Cloud admin state, or LaunchAgents changed.
- 2026-04-18 11:04 CDT cleanup: Restated the exact non-secret approvals still required and the still-closed gates. No runtime, credentials, mailbox, Google Cloud, OAuth, Pub/Sub, LaunchAgent, daemon, webhook, Cloud Run, or code state changed.
- 2026-04-18 11:11 CDT runtime fast-poll docs: recorded machine-local LaunchAgent interval reduction from 60 seconds to 15 seconds for Frank and Avignon. AI Workspace is dirty/diverged and was not committed or pushed.
- 2026-04-18 13:20 CDT Google auth retry: tried the existing local Gmailconnector OAuth start path using the approved private Frank credential source as input, but Google stopped before any password or 2FA/app-approval step with `401 deleted_client`. No OAuth token was created, no Gmail mailbox content was read, no Google Cloud/PubSub/IAM/API state was changed, and no credential values were printed. This confirms the old Gmailconnector OAuth client is not a usable setup bundle for Frank/Avignon push.
- 2026-04-18 13:25 CDT Robert clarified the relevant Google auth state is on the M4 from the ERTC work. Do not continue trying the deleted local Gmailconnector OAuth client on this Mac mini path; the next Gmail push/OAuth worker should inspect the M4-approved ERTC Google auth context under the same credential/token guardrails.
- 2026-04-18 13:42 CDT Robert paused further Gmail push/OAuth/PubSub work until Monday, 2026-04-20. Keep 15-second polling active, verify polling health first on Monday, and do not perform Google auth, OAuth token work, Pub/Sub/IAM mutation, mailbox content reads, cadence changes, deploy/push/live pull, subscriber work, or Workspaceboard changes for this slice before Monday unless Robert explicitly reopens it.

### machine-local runtime

- Runtime Log ID: `2026-04-18-gmail-fastpoll`
- Changed files:
  - `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist`
  - `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist`
- Backups:
  - `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist.bak-20260418-gmail-fastpoll`
  - `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist.bak-20260418-gmail-fastpoll`
- Change Summary: Reduced existing duplicate-protected inbox polling interval from 60 seconds to 15 seconds and reloaded/kickstarted the same LaunchAgent labels.

## Verification Notes

- Read AI Workspace `TODO.md`, append queues, Frank/Avignon docs, non-secret LaunchAgent backup metadata, and `Gmailconnector` read-only source/docs.
- Searched local files for Gmail API push/PubSub/watch/history usage; no integrated Frank/Avignon push path was found.
- Verified official Google behavior against the Gmail and Pub/Sub docs linked above.
- Verified current live LaunchAgent metadata with `plutil -p` and `launchctl print`; both auto jobs now report `run interval = 15 seconds` and `last exit code = 0`.
- Verified `plutil -lint` on both changed LaunchAgent plists.
- Verified `Gmailconnector` token metadata without printing tokens: local Gmail API tokens exist for Robert/Sonat/Oleg/Sebastian only, not Frank or Avignon.
- Verified no local `gcloud` CLI was available for Pub/Sub project/topic/subscription/IAM setup.
- Ran a Frank dry-run with `--limit 0` and confirmed `0` actions.
- Ran synthetic non-private routing checks: Frank synthetic mail reached the existing classifier path; Avignon synthetic self-mail classified as `assistant-self-mail` with `logged-no-action` and no decision item.
- Retried Gmailconnector OAuth for Frank in headless Chrome with credential values kept in-process only; Google returned `deleted_client` before password submission or 2FA.
- Robert clarified after the retry that the useful Google auth path lives on the M4, not this Mac mini local Gmailconnector client.

## Rollback Plan

To roll back the immediate runtime change, restore the backup plists and reload the same labels:

1. `cp /Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist.bak-20260418-gmail-fastpoll /Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist`
2. `cp /Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist.bak-20260418-gmail-fastpoll /Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist`
3. `launchctl bootout gui/501 /Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist 2>/dev/null || true`
4. `launchctl bootout gui/501 /Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist 2>/dev/null || true`
5. `launchctl bootstrap gui/501 /Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist`
6. `launchctl bootstrap gui/501 /Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist`
7. `launchctl enable gui/501/com.koval.frank-auto`
8. `launchctl enable gui/501/com.koval.avignon-auto`

## Follow-Ups

1. Monday, 2026-04-20 polling-health check: verify `com.koval.frank-auto` and `com.koval.avignon-auto` loaded intervals, last exits, recent run timestamps, error logs, duplicate protection, and captured/routed acknowledgement behavior while keeping the 15-second polling path unchanged.
2. After the Monday health check only, decide whether true Gmail push is still needed.
3. If still needed, resume from the M4 ERTC Google auth context under credential/token guardrails; do not use the deleted local Gmailconnector OAuth client.
4. Code and Git Manager: review any future runtime-code patch before commit, push, deploy, live pull, reload, or closeout.

## 2026-04-20 OAuth Continuation Blocker

Source Message-ID: `<CAAtX44bSqrWb2twfLvj_45oOkFLKcSDtjGQ6fqwRbm16xBSprA@mail.gmail.com>`.

Robert approved the OAuth next step after the Monday polling-health verification and directed that the existing 15-second polling path stay in place as backup. Task Manager then clarified the guardrail: continue only inside OAuth-next-step scope, do not open or print `.private` credential contents, do not rely on `/Users/admin` credential/token paths except documented non-secret runtime metadata, do not mutate Pub/Sub/IAM/subscriber/project/LaunchAgent/runtime state, and stop if no documented approved Frank/Avignon token storage path exists.

Outcome: stopped before OAuth. No documented approved Frank/Avignon token storage path was found under the current workspace-boundary guardrail. The generic Gmail export path documents `~/.config/koval-gmail-export/token.json` for ERTC/read-only exports, but it is not a documented Frank/Avignon push token store. The older `/Users/werkstatt/Gmailconnector` route remains unsuitable because the prior attempt was documented as `401 deleted_client`.

Verification and metadata only:

- Read active TODO/append queues and this project note.
- Located Gmail/OAuth docs and scripts by filename/content while excluding `.private` and other secret paths from broad searches.
- Confirmed `.private` credential candidates exist by path/metadata only after the guardrail clarification; no credential values were used for OAuth.
- Confirmed the documented LaunchAgent plist backup state still has `StartInterval` `15` for both Frank and Avignon. `launchctl print` did not return additional state from this shell context, so live last-exit/state was not revalidated here.

Not done:

- No OAuth authorization flow, browser login, token creation, token refresh, token validation, mailbox read/search/export, Pub/Sub/IAM/project mutation, subscriber/webhook work, LaunchAgent/cadence/runtime/production change, external-sensitive email, deploy, live pull, commit, push, or service restart.

Exact next approval needed:

- Approve the named Frank/Avignon OAuth token storage path and storage class.
- Approve the minimum Gmail API scope for this assistant-mailbox purpose.
- Approve the OAuth client/source to use, replacing the deleted Gmailconnector client.
- If the approved token/client path is outside `/Users/werkstatt/ai_workspace`, explicitly approve that path and state whether only metadata checks or actual token writes are allowed.

## 2026-04-20 OAuth Client/Source Partial Approval

Continuation source Message-ID: `<CAAtX44ampWj6PrHdE4meHgrUqWsSn=eoUC49h7Rxuc99dC9=+g@mail.gmail.com>`.

Robert supplied the approved OAuth client/source metadata:

- Google Cloud project: `gmailconnector-485021`
- OAuth client id: `261057116535-9gf1pqfg090mm2038sackt82p1r8t8i9.apps.googleusercontent.com`

This clears the prior OAuth client/source blocker only. No Google Console page was opened, no Google Cloud/IAM/PubSub/project/API setting was read or mutated, and no OAuth/browser flow was started.

Remaining blocker before OAuth login/token generation:

- Named Frank/Avignon token storage path and storage class.
- Exact minimum Gmail API scope for this assistant-mailbox token flow. The existing Security Guard checklist gives preferences and boundaries (`gmail.metadata` if headers/metadata are sufficient; `gmail.readonly` only if body read is explicitly required), but this continuation still needs the exact scope to authorize.
- If the approved token path is outside `/Users/werkstatt/ai_workspace`, explicit approval for that path and for token writes there.

Not done:

- No OAuth authorization flow, browser login, token write, token validation, mailbox read/search/export, Pub/Sub/IAM/project/subscriber mutation, LaunchAgent/cadence/runtime/production change, external-sensitive email, deploy, live pull, commit, push, or service restart.

## 2026-04-20 OAuth Approval Reaffirmation

Additional source Message-ID: `<CAAtX44ZUHKpHbNWANyLc8bA9wK3X5bxqnUfPP3QrCm9zyJrhnQ@mail.gmail.com>`.

Robert reaffirmed that OAuth work is approved for the same Gmail push/OAuth/Pub/Sub blocker thread. This is attached as approval/dedupe evidence for the existing OAuth task, not a new work item.

Current narrowed state:

- OAuth work is approved in principle.
- OAuth client/source metadata is approved: project `gmailconnector-485021`, client id `261057116535-9gf1pqfg090mm2038sackt82p1r8t8i9.apps.googleusercontent.com`.
- OAuth/browser login/token generation remains blocked until the named Frank/Avignon token storage path/storage class and exact minimum Gmail API scope are approved.
- If the approved token path is outside `/Users/werkstatt/ai_workspace`, explicit approval for that path and for token writes there is still required.

Not done:

- No OAuth authorization flow, browser login, token write/read/validation, mailbox read/search/export, Pub/Sub/IAM/project/subscriber mutation, Google Console access, LaunchAgent/cadence/runtime/production change, external-sensitive email, deploy, live pull, commit, push, or service restart.

## 2026-04-19 Security Guard OAuth Follow-Up Review

Source: Robert input in active Codex Integration Manager chat on 2026-04-19. Coordinating session `b66fdade`; Security Guard review session `71ab6f94`.

Security decision: planning-only is allowed. No OAuth, Google auth, mailbox-content read, Google Cloud/Pub/Sub/IAM mutation, runtime cadence change, deploy/live pull/service restart, credential/token inspection, or external send is approved by this review.

### Frank And Avignon Monday Checklist

- Owner path: Codex Integration Manager coordinates; Security Guard owns scope/storage approval; Google/OAuth owner provides or authorizes the approved Google Cloud/OAuth setup bundle from the M4 ERTC Google auth context; Code and Git Manager reviews any later code/runtime change; Frank/Avignon runtime owner installs only after explicit approval.
- Due date: Monday, 2026-04-20, first action only.
- Allowed planning-only or health-check steps: verify current 15-second polling health from non-secret metadata; review existing non-secret logs for last exit, recent run timing, duplicate protection, and captured/routed acknowledgement behavior; update TODO/project notes with non-secret status.
- Remaining Robert decision after health check: decide whether true Gmail API push is still needed, and if yes approve the exact Google Cloud/OAuth/PubSub/runtime implementation slice.
- Minimum OAuth scope: prefer no new OAuth if polling is acceptable. If push is approved, use `gmail.metadata` when headers/metadata are sufficient for routing; use `gmail.readonly` only if message-body read is explicitly required for the existing classifier. `gmail.modify`, `gmail.send`, `mail.google.com`, delegated domain-wide access, or any broader scope requires a separate Security Guard review and explicit Robert approval.
- Storage boundary: OAuth material, refresh/access tokens, client secrets, app passwords, private keys, and token caches must stay in OS keychain, owner-only machine-local private storage, or another named approved secret store. Only non-secret references such as account name, approved scope, current owner, and state category may be written to project-hub, TODO, handoff, logs, git, or chat.
- Runtime state boundary: non-secret operational state such as `historyId`, watch expiration, last notification time, fallback-sync time, and dedupe ids may be recorded only in an approved machine-local runtime/state location after runtime-owner approval. It must not be placed in Google Drive-synced folders, git, project-hub, normal chat, or mailbox notes.
- Must not be done before approval: no OAuth consent flow, token read/print/copy/validation/migration, credential-path disclosure, mailbox body read, Gmail label/file/send mutation, Pub/Sub topic/subscription creation, IAM grant, API enablement, OAuth-client change, subscriber/daemon/webhook/Cloud Run install, LaunchAgent change, service restart, cadence change, deploy, live pull, push, commit, or external send.

### Future Macee Inbox OAuth/Template Task

- Owner path: Codex Integration Manager scopes the request; Outreach Communicator owns template/outreach copy; Security Guard owns any mailbox/OAuth decision; Robert and the mailbox owner must approve any Macee inbox access before a worker starts; Code and Git Manager joins only if code/template files in a git-backed repo will be changed.
- Due date: none set by this review. Treat as a future approval-gated task, not part of the Monday Frank/Avignon health check.
- Allowed planning-only steps now: define the desired template output, list non-secret source requirements, prepare a no-access template brief, and request a supplied sanitized export/example set as the preferred path.
- Minimum access path: prefer supplied sanitized examples or an owner-approved export over OAuth. If OAuth is later approved, start with `gmail.metadata` only for locating candidate messages; request `gmail.readonly` only if Robert and the mailbox owner explicitly approve body reads for bounded template extraction. Sending, modifying, filing, deleting, or broad mailbox scopes are not approved.
- Storage boundary: same as Frank/Avignon. No Macee credentials, tokens, mailbox bodies, private examples, private addresses, or credential/token paths may be written to chat, project-hub, TODO, git, normal logs, or reusable templates. Approved reusable templates must be scrubbed of private mailbox content and source-specific personal data.
- Must not be done before approval: no Macee OAuth, no mailbox login, no mailbox search/read/export, no template extraction from private mail, no external send, no Portal/CRM/OPS mutation, no runtime/service change, no credential/token handling, and no Google Cloud/Pub/Sub/IAM mutation.
