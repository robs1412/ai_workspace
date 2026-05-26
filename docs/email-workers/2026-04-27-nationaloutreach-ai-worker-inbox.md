# National Outreach AI Worker Inbox Setup

Status: setup verified; full body review and approved queued send capability installed; Drive OAuth completed
Created: 2026-04-27 CDT

Robert approved using `nationaloutreach@kovaldistillery.com` as the main inbox for AI workers, while keeping Frank and Avignon separate.

## Current Model

- `nationaloutreach@kovaldistillery.com` is the shared AI-worker inbox.
- `codex@kovaldistillery.com` is the first alias on this account and is routed as Codex Local Agent, separate from Frank.
- Email Coordinator owns shared-worker mailbox intake and routing.
- Outreach Coordinator owns outreach/tasting scheduling and OPS Outreach coordination routed from this inbox.
- `macee.maddox@kovaldistillery.com` is not an allowed send-from identity. Treat it only as inbound legacy-recipient context for old-mail review.
- Frank and Avignon remain separate mailbox workers and are not merged into this inbox.

## Send-From Rule

Every allowed worker `From` identity must be listed in `worker_roles/send-from-personas.md` and mapped to an organigram role before use.

Current enabled send-from identities:

- `frank.cannoli@kovaldistillery.com`
- `avignon.rose@kovaldistillery.com`
- `codex@kovaldistillery.com`

Provisioned but not send-enabled until final persona/action approval:

- `asher@thecultivater.com`
- `venetia@thecultivater.com`

## Verification

The setup verifier used the approved private credential file and did not print credential values.

Verified on 2026-04-27:

- IMAP SSL login succeeded.
- SMTP SSL login succeeded.
- Standard AI-worker labels were created.
- Header-only polling succeeded for the latest 25 INBOX messages.
- Manual runtime runner verification succeeded for 200 INBOX headers.
- Full-body runtime review succeeded for 300 recent INBOX messages.
- Message bodies are stored only in owner-only private runtime state.
- No mail was sent during verification because no approved queued send drafts existed.

## Labels Created

- `Handled - AI Workers`
- `Handled - National Outreach`
- `Handled - Marketing`
- `Handled - Internal Communicator`
- `Handled - Frank Route`
- `Handled - Avignon Route`
- `Waiting - AI Workers`
- `Blocked - AI Workers`
- `Needs Robert`
- `Needs Sonat`

## Local Surfaces

- Worker folder: `nationaloutreach/`
- Persona: `nationaloutreach/PERSONA.md`
- Send-from registry: `worker_roles/send-from-personas.md`
- Private machine-local credential and setup state: `.private/mailboxes/nationaloutreach/`
- Prepared runtime: `/Users/admin/.nationaloutreach-launch/`
- Staged LaunchDaemon plist: `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist`
- Staged install helper: `tmp/nationaloutreach-launch/install-launchdaemon.sh`
- Codex/National Outreach Drive API bundle: `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/`

Do not copy credential values, private mailbox bodies, OAuth tokens, app passwords, private keys, or private SOP text into shared docs or git.

## LaunchDaemon State

Robert ran the staged helper and `com.koval.nationaloutreach-auto` is installed as the National Outreach mail-cycle LaunchDaemon. It is a `StartInterval` job, so it may show as not running between successful short runs.

The prepared runtime now uses `nationaloutreach_mail_cycle.py`, which:

- reads full message bodies into private state;
- classifies messages into Outreach Coordinator, Marketing Manager, Internal Communicator, Email Coordinator, Naomi Stern, Ezra Katz, or Security Guard review buckets;
- writes non-secret metadata/route suggestions to the worker workspace;
- sends only queued `*.approved.json` drafts from the private outbox; and
- does not move, delete, or file mailbox messages yet.

## First Body-Read Review

First pass, 300 recent messages:

- Outreach Coordinator: 222.
- Marketing Manager: 49.
- Email Coordinator: 11.
- Internal Communicator: 5.
- Security Guard / sensitive-review: 13.

Initial team suggestions:

- Reconcile accepted tasting/calendar messages into OPS Outreach state so accepted tastings do not remain only in email/calendar.
- Review Malloy's, Garfield's, Mariano's, Whiskeyfest, and similar tasting/event threads as Outreach Coordinator follow-ups.
- Route Earth Day, New Beer's Eve, Ravenswood, media/magazine, and broader campaign-style items to Marketing Manager / Communications Manager rather than treating them as simple scheduling mail.
- Preserve Macee transition/SOP messages as guidance sources, then convert only reusable non-secret rules into worker docs.
- Keep Google/security alerts, payment/auth/security-looking notices, and ambiguous system approvals out of automatic sending until reviewed.

## Send-From Correction

Robert clarified on 2026-04-27 that National Outreach must not send as `macee.maddox@kovaldistillery.com` again because Macee has left.

The National Outreach mailbox is intake-only. It is not an outbound `From` identity. Outbound mail from work routed through this inbox must use a real worker/persona address such as `codex@kovaldistillery.com`, `vanessa.sterling@kovaldistillery.com`, `naomi.stern@kovaldistillery.com`, or `ezra.katz@kovaldistillery.com` when approved.

`macee.maddox@kovaldistillery.com` remains only old-mail inbound-recipient context.

## Codex / National Outreach Drive API

Prepared bundle: `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/`.

- OAuth login account: `nationaloutreach@kovaldistillery.com`
- Codex alias on same account route: `codex@kovaldistillery.com`
- Scopes: `drive.metadata.readonly` and `drive.file`
- Local token target: `.private/google-oauth/nationaloutreach-google-drive-token.json`
- Future Infisical refresh-token secret: `GOOGLE_DRIVE_CODEX_NATIONALOUTREACH_REFRESH_TOKEN`

OAuth was completed on 2026-04-27 using the private callback-file method, because direct high-port callback access from Robert's browser to the Mac mini was blocked and the temporary Workspaceboard low-port relay path served PHP as text instead of executing it.

Exact working method:

1. Run `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/authorize.sh`.
2. Open the printed Google consent URL and approve `nationaloutreach@kovaldistillery.com`.
3. After Google redirects to the broken localhost callback URL, copy the full browser address bar. It must include `code=`.
4. Paste the full URL into `.private/google-oauth/nationaloutreach-callback-url.txt`.
5. The helper reads that private file, validates `state`, exchanges the code, writes `.private/google-oauth/nationaloutreach-google-drive-token.json`, then clears the callback file.

Do not paste the failed callback URL into chat, email, docs, or git. Treat it as credential-adjacent material.

Verification:

- `whoami.sh` confirms Drive authentication for `nationaloutreach@kovaldistillery.com`.
- After Robert added National Outreach to the shared Drive, a write test succeeded.
- Uploaded test file: `nationaloutreach-codex-write-test-2026-04-27.txt`
- Drive file ID: `10KLYqHsIF3yyvYC2CUZdv8aHIMFDWipH`
- Link: `https://drive.google.com/file/d/10KLYqHsIF3yyvYC2CUZdv8aHIMFDWipH/view?usp=drivesdk`
- Read-after-write metadata listing confirmed the file is present under shared Drive `0AP-Yf32mH4IHUk9PVA`.
