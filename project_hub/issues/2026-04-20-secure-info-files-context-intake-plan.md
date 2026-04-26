# Secure Info / Files Context Intake Plan

- Master Incident ID: `AI-INC-20260420-INFO-FILES-CONTEXT-INTAKE-01`
- Date Opened: 2026-04-20
- Owner: AI Workspace / Frank / Codex Integration Manager
- Priority: Medium
- Status: Metadata-only Frank prep verified; live execution blocked pending Infisical/env/token inputs
- Source Message-ID: `<CAAtX44ZX0u0toGJ7O4grpZY7j6MW9n_S=Anj8M8k-sQhY4gZXQ@mail.gmail.com>`
- Source subject: `Re: Info / files`
- Source from/date: Robert Birnecker `<robert@kovaldistillery.com>` / Mon, 20 Apr 2026 09:00:19 -0700
- Session: `516e1be9` / `Secure info files storage Drive API plan`; related prior design session `64ea6f84` / `Secure info files context storage design`
- Attached worker prompt source: `<CAAtX44Z0DxQ+ruJfOY2fSA2Un617-dfQiF3BQ7R8aaxDiQiQrA@mail.gmail.com>`; session `0774d4a8` / `file-management project intake and plan`; excerpt available to this worker was truncated after `Project: File management.` Note: the same Message-ID is already recorded locally for session `124bba8f` / `AI Improvement Manager role expansion`, so source/context clarification is required before treating the Message-ID as unambiguous.

## Scope

Robert approved adding the Info/files proposal as a plan and asked what is needed next to implement it safely, especially around Google Drive API.

The later file-management source is attached to this same project because the local non-secret records already contain a secure files/context intake plan covering file storage, Drive/API boundaries, source-of-truth, document analysis, metadata logging, backup/retention interactions, and approval gates. The excerpt available to this worker did not include enough detail to justify a separate project or to infer an implementation request.

There is also a source-record ambiguity: local records already associate the same supplied Message-ID with the AI Improvement Manager role-expansion project. This plan therefore records the file-management request by worker session and truncated excerpt, and asks Frank to clarify the source/context with Robert before relying on that Message-ID as a unique dedupe key.

This slice is documentation and state only. It did not create Google Drive folders, change permissions, read or download Drive content, start OAuth, inspect credentials, access mailbox bodies, call Google Cloud, configure IAM, touch Pub/Sub, create token storage, edit runtime services, deploy, commit, push, or start daemons.

## Existing Context

Related local planning already exists in:

- `project_hub/issues/2026-04-14-digital-office-project-task-work-records-proposal.md`
- `project_hub/digital-office/storage-decision-needed.md`
- `project_hub/digital-office/security-review-checklist.md`
- `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`
- `frank/drafts/info-files-document-intake-recommendation-robert-2026-04-19.txt`

Those records establish the current policy: OAuth/token material must not live in Google Drive-synced folders, Papers, MI, normal manifests, logs, chat, or git; live Papers/MI writes and `.205` access remain gated; and Markdown/project-hub/AI-Bridge records may store only non-secret metadata.

## Recommended Storage Model

Use a layered model:

1. Raw files live in a restricted Google Drive area owned or explicitly approved by Robert.
2. AI Workspace/project-hub stores only non-secret routing and approval metadata.
3. AI-Bridge can later store structured no-secret manifests, schemas, and handoff records.
4. Papers/MI remain later projection/index targets, not the first raw-file storage surface.
5. Credentials, secrets, OAuth tokens, private keys, app passwords, client secrets, and `.env` values never go into Drive intake folders, project-hub, Papers, MI, git, chat, or normal logs.

For the truncated `Project: File management` source, the safe interpretation is planning and clarification only:

- Treat `file management` as a possible broader umbrella for secure document intake, storage organization, analysis, backup/retention, and ownership workflows.
- Do not assume Robert wants agents to reorganize, move, delete, upload, download, index, or read files.
- Do not assume Google Drive is the source of truth until Robert names the folder, Shared Drive, account, and approval model.
- Do not assume Papers/MI, Workspaceboard, AI-Bridge, local folders, or backup targets become storage systems for raw documents.

Recommended Google Drive folder concept:

- `AI Intake - Uploads`: human-uploaded incoming documents, not automatically read by agents.
- `AI Intake - Approved For Agent Read`: documents Robert or an approved owner explicitly clears for agent read/download.
- `AI Intake - Processed`: files already summarized or converted into non-secret task/context records.
- `AI Intake - Quarantine`: suspicious, secret-bearing, duplicate, or not-yet-classified files.
- Optional later subfolders by workspace or initiative, for example `salesreport`, `ops`, `bid`, `frank`, `avignon`, and `digital-office`.

Folder creation and permission assignment should be human-created at first. Agents should record folder IDs only after Robert supplies them as non-secret metadata.

## Intake Record Model

Every file or link should get a metadata record before any automated read:

```yaml
intake_id: info-file:<date>:<slug-or-hash>
source_ref: email-message-id | drive-file-id | drive-folder-id | supplied-url | local-path
owner: Robert | Sonat | Dmytro | module owner
workspace: ai | ops | portal | salesreport | bid | lists | frank | avignon | other
storage_location: drive | supplied-link | local-approved-path
sensitivity: public_reference | internal_business | private_internal | secret_adjacent | blocked_secret
allowed_actions: metadata_only | read_summary | extract_text | route_task | create_non_secret_projection
disallowed_actions:
  - credential extraction
  - secret storage
  - broad sharing
  - production mutation
approval_state: needed | approved | rejected | expired
approved_by:
approved_at:
drive_file_id:
drive_folder_id:
mime_type:
content_hash:
dedupe_keys:
summary:
next_action:
```

This record should store Drive IDs and safe summaries, not file contents unless a later approved no-secret extraction path explicitly allows generated summaries.

## Access Boundaries

- Default is metadata-only until a specific file, folder, account, scope, and action is approved.
- Agents may not read or download every file in a Drive folder just because the folder exists.
- Private email bodies and attachments require their own email-source approval; a Drive link does not automatically authorize mailbox reads.
- Secret-bearing files are blocked from normal intake and must route to Security Guard/private credential handling.
- Sensitive finance, legal, HR, auth, security, production, and customer/private records need owner approval before content extraction.
- Keep raw files out of git, project-hub, AI-Bridge manifests, Papers, MI, chat, and normal logs.
- Record only non-secret metadata: owner, source ID, Drive ID, MIME type, sensitivity tier, allowed actions, approval state, and a short safe summary.

## Google Drive API Safe Path

Phase 0: Human-created intake area.

- Robert creates or approves the Drive folder or Shared Drive location.
- Robert supplies non-secret folder IDs and allowed accounts.
- Agents record metadata only. No API use.

Phase 1: Manual-link metadata intake.

- Frank/Task Manager records Drive links and owner approvals in project-hub/HANDOFF/TODO or AI-Bridge manifests.
- No OAuth, no Drive API, no downloads.

Phase 2: Read-only Drive metadata probe.

- After approval, use the narrowest scope that can list file metadata for the approved folder.
- Candidate scope: `https://www.googleapis.com/auth/drive.metadata.readonly`.
- Output only file IDs, names, MIME types, owners where safe, modified time, and folder membership.
- No file content download in this phase.

Phase 3: Controlled read/download for approved files.

- After a second approval, read only files explicitly approved by Drive file ID or an approved allowlist.
- Candidate scope if content access is required: `https://www.googleapis.com/auth/drive.readonly`.
- Download to an approved machine-local private working path or stream to a parser without durable raw-file copies, depending on Security Guard decision.
- Extract only approved text/metadata and write non-secret summaries/manifests.

Phase 4: Workspace routing and no-write projection.

- Convert approved summaries into task briefs, project-hub notes, AI-Bridge handoffs, or future Papers/MI projection records.
- Do not write Papers/MI until the existing Papers read/write gates are separately approved.

Phase 5: Optional live index.

- Build a Workspaceboard or AI-Bridge read-only index showing approved intake records, status, owners, duplicate state, and next action.
- This still should not change Drive permissions, move files, write Papers/MI, or mutate production systems unless separately approved.

## Token And Storage Requirements

Before any Drive API implementation, Robert/Security must approve:

- OAuth client/source or service-account source.
- Whether this is user OAuth or a service account / delegated Workspace flow.
- Exact scopes for each phase.
- Token storage class and path.
- Whether token writes are allowed on this machine.
- Rotation/revocation owner and procedure.
- Whether any path outside `/Users/werkstatt/ai_workspace` is approved.

Default recommendation:

- Per-machine user OAuth: token in macOS Keychain or a machine-local owner-only private path, not Drive, git, Papers, MI, project-hub, AI-Bridge, logs, or chat.
- Shared automation: approved secret manager, Google-managed service account/delegated flow, or keychain-backed provisioning with least privilege and explicit revocation owner.
- Non-secret project-hub records may store only app/client label, account label, scope summary, storage class, owner, and revocation procedure.

## Audit And Logging

Every action should produce a non-secret audit event:

- source Message-ID or task ID;
- intake ID;
- Drive folder/file ID, if approved;
- acting worker/session;
- approved action;
- scope used;
- files counted or summarized;
- created output records;
- skipped/blocked reason;
- duplicate match if any;
- no-secret confirmation.

Do not log file bodies, private mailbox bodies, credentials, token paths containing secrets, signed URLs, download URLs, or raw parser output before redaction.

## Dedupe

Dedupe should compare:

- Drive file ID;
- source Message-ID;
- normalized filename;
- MIME type and size;
- modified time;
- content hash only after content read/download is approved;
- explicit external URL;
- project/task/source aliases.

Duplicate findings should update the intake record with `duplicate_of` and avoid repeated reads or repeated Robert prompts unless a new file version, new source message, or new approval gate appears.

## Supported File Types

Initial supported types after approval:

- Google Docs, exported as plain text or Markdown where allowed.
- PDF, text extraction only when not scanned or after OCR is separately approved.
- DOCX, XLSX, CSV, TXT, Markdown, HTML, JSON.
- Email-export artifacts only when mailbox/export approval already exists.

Blocked or special-review types:

- archives such as ZIP unless explicitly approved and scanned/classified;
- password-protected files;
- binaries and executables;
- files likely to contain credentials, private keys, OAuth tokens, app passwords, `.env`, database dumps, or full mailbox exports;
- legal/HR/finance/security-sensitive documents without owner approval.

## Human Approval Points

Robert needs to approve or provide:

1. Drive folder or Shared Drive IDs, preferably human-created first. Robert supplied the Frank/Avignon shared target on 2026-04-20: `https://drive.google.com/drive/folders/0AP-Yf32mH4IHUk9PVA` / ID `0AP-Yf32mH4IHUk9PVA`.
2. Allowed Google accounts and whether Frank/Avignon/Codex have any access or only Robert uploads/approves.
3. OAuth vs service account / delegated Workspace decision.
4. OAuth client/source or Google Cloud project/app label for Drive API.
5. Exact scopes for Phase 2 metadata and Phase 3 file-content read.
6. Token storage path/class and whether token writes are approved.
7. Whether any implementation path outside `/Users/werkstatt/ai_workspace` is approved, such as machine-local Keychain/private runtime state.
8. Initial allowed sensitivity tiers and file types.

## 2026-04-24 Shared-Drive Access Clarification

Robert clarified that both of the assistant mailbox identities already have access to the approved shared Drive:

- `frank.cannoli@kovaldistillery.com`
- `avignon.rose@kovaldistillery.com`

Effect on the blocker:

- shared-Drive entitlement for Frank and Avignon is no longer the main unknown;
- the main remaining implementation gate is now OAuth and its surrounding approval packet.

What still needs explicit approval or confirmation before implementation:

1. whether the approved executable path is user OAuth for Frank, Avignon, Claude, or some narrower single-account path;
2. the OAuth client/source to use for Drive on the approved machine;
3. exact scopes for the first read-only metadata phase and any later content-read or write phase;
4. token storage class and approved location;
5. whether Infisical is approved for the Drive client/refresh-secret workflow described in Claude Task `#1326`;
6. revocation/rotation owner and non-secret audit destination.

Practical consequence:

- the next approval packet should be framed as "Drive OAuth implementation and storage approval" rather than "do these accounts have access to the shared Drive?"

## Recommended Drive OAuth Approval Packet

Recommended owner-facing packet:

```text
Subject: Shared Drive OAuth implementation approval needed for Frank / Avignon / Claude path

We have narrowed the Google Drive blocker.

Known approved context:
- Shared Drive target: `0AP-Yf32mH4IHUk9PVA`
- Frank mailbox identity `frank.cannoli@kovaldistillery.com` already has access
- Avignon mailbox identity `avignon.rose@kovaldistillery.com` already has access
- First safe test remains `metadata_only` under login-root `admin`
- Claude Task `#1326` reports a Drive integration design using `GOOGLE_DRIVE_CLIENT_ID`, `GOOGLE_DRIVE_CLIENT_SECRET`, and `GOOGLE_DRIVE_REFRESH_TOKEN`

Decision needed:
- approve the actual Drive OAuth execution path and token-storage model for the first implementation slice

Recommended first slice:
1. Read-only metadata probe only
2. Scope limited to `drive.metadata.readonly`
3. One approved shared Drive target only: `0AP-Yf32mH4IHUk9PVA`
4. No file-content reads, uploads, moves, deletes, permission changes, or broad Drive traversal

Please confirm these decisions:
1. Which account should execute the first OAuth path?
   - Frank
   - Avignon
   - Claude
   - another named single-account path
2. Which OAuth client/source is approved for this Drive workflow?
3. Is Claude Task `#1326`'s Infisical-backed secret model approved for this Drive workflow?
4. What token storage class/location is approved?
   - machine-local keychain/private runtime path
   - Infisical-backed workflow
   - another approved named location
5. Who owns token revocation/rotation?
6. Where should the non-secret audit log live?

If approved as recommended, the first implementation will be:
- OAuth setup for the one approved execution identity
- metadata-only listing for shared Drive `0AP-Yf32mH4IHUk9PVA`
- non-secret audit output only
- no raw-file download or content extraction

Nothing has been changed yet in Google Drive, OAuth, tokens, permissions, file content, or runtime automation.
```

Recommended default if Robert wants the narrowest safe start:

1. execute as one named account only, not all three at once;
2. start with `drive.metadata.readonly` only;
3. store tokens in an approved machine-local private path or keychain-backed location, not Drive/git/Papers/project-hub/chat;
4. use non-secret audit logging in AI Workspace/project-hub only;
5. leave file-content reads and any write scope for a second approval.

2026-04-24 send status:

- Frank sent this approval request to Robert.
- Subject: `Shared Drive OAuth implementation approval needed for Frank / Avignon / Claude path`
- Recipient: `robert@kovaldistillery.com`
- Frank task id: `frank-drive-oauth-approval-robert-2026-04-24`
- Message-ID: `<177705249613.91760.4938565830557936013@kovaldistillery.com>`

Current next step:

- wait for Robert's decision on execution identity, OAuth client/source, Infisical approval for the Task `#1326` model, token storage class/location, revocation owner, and audit destination.

## 2026-04-24 Robert Reply To Drive OAuth Approval Packet

Frank received Robert's tracked reply on 2026-04-24 to the approval request above. Message metadata:

- Source Message-ID: `<CAAtX44YP11jVyzBPzLQMOETWsXb+QQM7=m-oRMqey-7ED1YfaA@mail.gmail.com>`
- Subject: `Re: Shared Drive OAuth implementation approval needed for Frank / Avignon / Claude path`
- Thread task id: `frank-drive-oauth-approval-robert-2026-04-24`

Decision payload now recorded:

1. Execution identity
   - approved first OAuth path: `Frank`
   - Robert also noted that Claude is already authorized on `.205`, but the approved first execution path here is Frank.
2. Infisical-backed model
   - approved: `Yes`
3. Token storage
   - `Infisical preferred`
   - if local storage on the Mac mini is needed, it is approved as a temporary path but should be moved to Infisical.
4. Revocation / rotation owner
   - `Codex / Frank`
5. Non-secret audit log location
   - `on Mac mini`
6. Recommended first slice
   - approved as proposed:
     - one execution identity;
     - `drive.metadata.readonly` only;
     - shared Drive `0AP-Yf32mH4IHUk9PVA` only;
     - no raw-file download/content extraction;
     - no write operations.

Resolved clarification:

- Robert approved reusing the Claude Drive OAuth app/client tied to Task `#1326` for Frank's first metadata-only Drive slice.

Current blocker after Robert's reply and follow-up clarification:

- policy approvals for the first metadata-only slice are now effectively in place;
- the remaining implementation blocker is operational, not policy: the exact `#1326` implementation bundle or equivalent local review path still needs to be available on this machine before the live Frank metadata-only slice can be wired and verified here.

Recommended next action:

1. obtain the `#1326` Google Drive implementation bundle in an approved local review path, or re-stage it where this machine can inspect it;
2. verify the reusable Claude OAuth client/app details in that bundle;
3. wire the Frank metadata-only path against that approved client with `drive.metadata.readonly` only, shared Drive `0AP-Yf32mH4IHUk9PVA` only, and non-secret Mac mini audit logging only.

2026-04-24 Claude handoff request sent:

- Subject: `Frank follow-up: Task #1326 Drive bundle and OAuth client for Frank metadata-only slice`
- Recipient: `claude@koval-distillery.com`
- Cc: `robert@kovaldistillery.com`
- Frank task id: `frank-claude-drive-1326-bundle-request-2026-04-24`
- Message-ID: `<177705384959.23861.5232576410051903187@kovaldistillery.com>`

Requested from Claude:

1. exact OAuth app/client or Google project/app label tied to Task `#1326`;
2. the current bundle or approved local review path for `list.sh`, `download.sh`, `upload.sh`, `test.sh`, and `CLAUDE.md`;
3. any non-secret setup notes needed to run the metadata-only listing path with Frank as the execution identity;
4. whether the bundle should be re-staged somewhere other than `/tmp/gdrive-impl/`.

## 2026-04-24 Actual Bundle Read: Mac Mini Adaptation Plan

The actual server bundle was read live from `.205`.

Concrete code facts from `/srv/tools/gdrive/drive.py`:

1. server-only secret source is hardcoded:
   - `SECRETS_ENV = '/srv/secrets/machine-identity.env'`
2. current secret names are Claude-oriented:
   - `GOOGLE_DRIVE_CLIENT_ID`
   - `GOOGLE_DRIVE_CLIENT_SECRET`
   - `GOOGLE_DRIVE_REFRESH_TOKEN`
3. current Google scope is hardcoded to full Drive:
   - `scopes=['https://www.googleapis.com/auth/drive']`
4. `cmd_test()` currently lists recent files broadly rather than testing only the approved shared Drive target.
5. `cmd_list()` already supports Shared Drive listing by `driveId`, so the approved target `0AP-Yf32mH4IHUk9PVA` fits the current command structure without a larger redesign.

Concrete wrapper facts:

1. `list.sh` is already sufficient for the approved first slice once the scope/secret wiring is corrected.
2. `download.sh` and `upload.sh` exist, but they should remain unused for Frank until a later approval opens content reads or writes.
3. `test.sh` currently calls the broad `test` path and should be narrowed for the Frank metadata-only slice.

Recommended Mac mini patch shape:

1. replace hardcoded `SECRETS_ENV` with a Mac-mini-safe credential source:
   - env override first, for example `INFISICAL_MACHINE_ENV_FILE`;
   - keep the server default only as fallback for `.205`.
2. replace hardcoded refresh-token secret selection with a selectable key:
   - Claude keeps `GOOGLE_DRIVE_REFRESH_TOKEN`;
   - Frank uses a separate key such as `GOOGLE_DRIVE_FRANK_REFRESH_TOKEN`.
3. replace hardcoded full-Drive scope with a selectable scope:
   - Frank slice uses `https://www.googleapis.com/auth/drive.metadata.readonly`;
   - broader scope stays only for the Claude-side server lane if still needed there.
4. narrow the test path:
   - test should authenticate and list the approved shared Drive `0AP-Yf32mH4IHUk9PVA` only;
   - do not default to broad recent-file listing for Frank's slice.
5. keep the first live Frank path to `list` and `test` only:
   - no `download` or `upload` use in the first Mac mini slice.

Resulting concrete blocker:

- not policy;
- not bundle discovery;
- now a small implementation-and-auth packet:
  1. patch credential sourcing for Mac mini;
  2. patch refresh-token secret selection for Frank;
  3. patch scope to metadata-only;
  4. run Frank OAuth consent;
  5. write Frank refresh token to Infisical;
  6. verify metadata-only listing against shared Drive `0AP-Yf32mH4IHUk9PVA`.

Local reviewed artifact now created:

- `project_hub/artifacts/gdrive-frank-metadata-bundle/CLAUDE.md`
- `project_hub/artifacts/gdrive-frank-metadata-bundle/drive.py`
- `project_hub/artifacts/gdrive-frank-metadata-bundle/list.sh`
- `project_hub/artifacts/gdrive-frank-metadata-bundle/test.sh`
- `project_hub/artifacts/gdrive-frank-metadata-bundle/README.md`

Verification completed on the local reviewed artifact:

- `python3 -m py_compile` passed for `drive.py`
- `bash -n` passed for `list.sh` and `test.sh`

Current next step:

- wait for Claude's reply with the bundle or approved review path, then inspect locally before wiring the live Frank metadata-only slice.
9. Whether agents may download raw files locally, or must stream/read without durable raw copies.
10. Who may approve individual file reads after upload.
11. Audit log location for non-secret intake events.
12. Rollback behavior for accidental ingestion or wrong-file summaries.

## 2026-04-26 Frank Metadata-Only Mac Mini Prep Verification

This pass verified the reviewed local bundle at `project_hub/artifacts/gdrive-frank-metadata-bundle/` without starting OAuth, reading token values, calling Google Drive APIs, or changing Google Cloud/IAM.

Verified local bundle files:

- `CLAUDE.md`
- `README.md`
- `drive.py`
- `authorize_frank_drive.py`
- `list.sh`
- `test.sh`

Scope behavior after the prep adjustment:

- `drive.py` defaults to `https://www.googleapis.com/auth/drive.metadata.readonly`.
- `test.sh` targets only shared Drive `0AP-Yf32mH4IHUk9PVA` by default.
- `list.sh` / `drive.py list` now default to shared Drive `0AP-Yf32mH4IHUk9PVA` rather than broad Drive listing.
- Broad Drive listing is disabled unless `GOOGLE_DRIVE_ALLOW_BROAD_LIST=1` is explicitly set; do not set that for Frank's first slice.
- `authorize_frank_drive.py show-config --json` is non-secret config inspection only.
- `authorize_frank_drive.py authorize` remains gated because it starts live OAuth and writes a temporary local token payload.

Remaining concrete inputs before live execution:

1. Approved Infisical machine-identity env path on the Mac mini, supplied through `INFISICAL_MACHINE_ENV_FILE`, or an approved equivalent.
2. Infisical CLI availability on the Mac mini execution path.
3. Infisical project/environment values in the machine-identity env, without exposing them in chat or project docs.
4. Drive OAuth client JSON at `.private/google-oauth/frank-drive-desktop-client.json` or another approved local path. The file exists locally, but its contents were not printed or inspected in this pass.
5. Frank-specific refresh token stored in Infisical as `GOOGLE_DRIVE_FRANK_REFRESH_TOKEN`, or explicit approval to run the temporary local-token OAuth path and then migrate the token to Infisical.
6. Confirmation that the runtime command environment exports `GOOGLE_DRIVE_REFRESH_TOKEN_SECRET_NAME=GOOGLE_DRIVE_FRANK_REFRESH_TOKEN` if the default is not relied on.
7. Non-secret audit log destination on the Mac mini.

Verification run:

- `python3 -m py_compile project_hub/artifacts/gdrive-frank-metadata-bundle/drive.py project_hub/artifacts/gdrive-frank-metadata-bundle/authorize_frank_drive.py`
- `bash -n project_hub/artifacts/gdrive-frank-metadata-bundle/list.sh project_hub/artifacts/gdrive-frank-metadata-bundle/test.sh`
- `python3 project_hub/artifacts/gdrive-frank-metadata-bundle/authorize_frank_drive.py show-config --json`
- static search for broad scopes and content/write operations in the reviewed bundle

Current blocker:

- Live execution is blocked because `INFISICAL_MACHINE_ENV_FILE` is not set in this shell, the `infisical` CLI is not currently present on this execution path, and the Frank refresh token is not confirmed in Infisical. The local OAuth client JSON path exists, and the local temporary token path is missing. No OAuth/token/API action was performed.

## File-Management Clarification Packet

Because the file-management source was truncated after `Project: File management.`, the following details are missing before implementation can start:

1. Source context: whether the supplied Message-ID belongs to this file-management request or the already-recorded AI Improvement Manager role expansion, and what subject/thread should be used as the durable dedupe key.
2. Goal: whether Robert wants secure intake only, file organization, duplicate cleanup, document analysis, backup/retention, search/indexing, or a combination.
3. Scope: which accounts, folders, Shared Drives, local paths, or workspaces are in scope, and which are explicitly out of scope.
4. Source of truth: whether raw files should live in a restricted Google Drive area, a local approved path, an external/offsite storage target, an existing business system, or remain human-managed.
5. Allowed accounts: which Google/Drive accounts or assistant roles may see metadata, request content reads, or approve individual files.
6. Metadata log: where non-secret intake records should live, such as this project log, AI-Bridge records, Workspaceboard read-only index, or a separate manifest.
7. Document analysis path: whether agents may extract text, summarize, classify, OCR, dedupe, or route tasks from files, and which file types and sensitivity tiers are allowed first.
8. Backup/retention: whether this project should connect to the Workspaceboard/AI work product backup plan, a separate raw-file retention policy, or no backup automation yet.
9. Ownership: who owns approvals, folder permissions, revocation, deletion/retention decisions, and incident response for wrong-file ingestion.
10. Approval gates: whether any Drive API/OAuth/service-account setup, local download/streaming, file movement, folder creation, permission change, external sharing, or Papers/MI projection is approved.
11. First safe test: one non-secret test file or folder ID, its owner, sensitivity tier, allowed action, and expected output.

Recommended clarification request for Frank to send Robert:

```text
I attached the truncated "Project: File management" note to the existing Secure Info / Files Context Intake project, because it appears to overlap with the secure files/context plan rather than clearly creating a separate project.

Before implementation, please confirm the intended goal and first safe slice:
- Does the Message-ID belong to this file-management request, or should we use a different source/thread id for this project?
- Is this about secure file intake, Drive organization, document analysis, duplicate cleanup, backup/retention, search/indexing, or another file-management workflow?
- What folder/account/source should be the source of truth, if any?
- Which accounts or roles may access metadata, and who may approve file-content reads?
- Should raw files stay in a restricted human-managed Drive area, or somewhere else?
- Where should non-secret metadata/audit records live?
- What file types and sensitivity tiers are allowed for the first test?
- May agents only record metadata, or may they extract/summarize one approved file?

No Drive/API/OAuth, file movement, upload/download/delete, mailbox read, credential access, Papers/MI write, production change, deploy, commit, or push has been performed.
```

## Initial Implementation Phases

Recommended first implementation only after approval:

1. Add a no-API intake metadata template under AI-Bridge or project-hub.
2. Record manually supplied Drive folder/file IDs and approval state.
3. Build a no-Drive dry-run parser that validates intake records and dedupe fields.
4. Add a read-only metadata probe for one approved folder with `drive.metadata.readonly`.
5. Add controlled content extraction for one approved test file with `drive.readonly`.
6. Add Workspaceboard or AI-Bridge read-only view.
7. Decide separately whether summaries project into Papers/MI.

## 2026-04-22 Per-User And Shared File-Space Plan

Source Message-ID: `<CAAtX44a=rFARtKyiDJ8Ha45KiH+AkJhNXPeaTJ1_UYifyY9LqQ@mail.gmail.com>`; dedupe key `frank-direct-primary-CAAtX44a-rFARtKyiDJ8Ha45KiH-AkJhNXPeaTJ1-UYifyY9LqQ-mail-gmail-com`; owner/source Robert; subject `Next project`; Frank visible route `b7f9729b` / `Frank direct Robert: Next project`; AI Workspace planning route `f0846b6f` / `File spaces project next action` reached `finished` / `review-ready`.

Decision: attach this to the existing Secure Info / Files Context Intake project, not a new project. The request is a direct continuation of the same file-management lane: per-user file spaces, a shared/general Google Drive surface, folder-transfer planning, and approval gates before agents touch Drive or local files.

Practical first slice:

1. Define the target information architecture in docs only:
   - One login-named user-root Drive area per approved user login, for example `admin` and `sonat`.
   - One shared/general Drive area for cross-role work, policies, templates, approved reference files, and project materials that should not live in a single user's space.
   - Optional workspace subfolders under shared/general only after the owner model is clear, for example `AI Workspace`, `OPS`, `Portal`, `Salesreport`, `BID`, `Lists`, and `Admin`.
2. Create a non-secret folder register before any file movement. The register should store folder name, Drive folder ID when supplied by a human, owner, allowed roles, sensitivity tier, allowed actions, and whether agent access is metadata-only, read-summary, or blocked.
3. Use human-created folders first. Agents should not create folders or set permissions in the first slice.
4. Start with metadata-only intake for one approved test folder. No content reads, downloads, upload, move/copy, delete, permission change, or API call happens until the folder, account, scope, and token-storage decisions are approved.
5. After metadata-only review, choose one non-secret test folder or file and approve the exact action: summarize, classify, route into a task, or leave as metadata-only.

Folder-transfer guidance without moving files yet:

- Inventory first: Robert or the owner lists candidate folders to classify or test, including current location, intended login-root or shared area, sensitivity tier, duplicates/old versions, and whether the folder belongs under a login-named root or shared/general. Do not treat arbitrary top-level folders as user roots.
- Map before copy: build a proposed source-to-destination table. Each row should say `source folder`, `target owner/shared area`, `keep/copy/move later`, `permission model`, `retention note`, and `approval needed`.
- Prefer staged copy over move for the first migration. The first approved implementation should copy one low-risk test folder, verify counts and permissions, then leave the original untouched until Robert approves cleanup or archival.
- Keep shared/general for genuinely shared material. Personal drafts, private owner records, credentials, HR/legal/finance/security-sensitive files, and unclear ownership should stay in owner/private or quarantine areas until classified.
- Do not download full folders locally as a transfer method unless Robert/Security approves the local path, storage class, retention, cleanup, and audit log.
- Do not treat Google Drive links or folder membership as permission for agents to read contents. Content reads need explicit per-folder or per-file approval.

Approval gates still closed:

- No Drive API/OAuth/browser login/service-account/delegated Workspace setup.
- No Google Cloud/IAM/Pub/Sub mutation.
- No folder creation, permission change, sharing change, move, copy, upload, download, delete, or bulk operation.
- No local raw-file download/cache, unless a path/storage class/retention/cleanup rule is separately approved.
- No Papers/MI read/write/projection, `.205` access, production change, deploy, commit, push, CRM/Portal/OPS mutation, or external-sensitive reply.
- No private mailbox bodies, credentials, tokens, private keys, `.env` files, signed URLs, or secret paths in docs, chat, TODOs, handoffs, git, Papers, or MI.

Immediate next action for Frank to report: Robert has now supplied the first low-risk shared Drive test packet. The approved shared Drive target is `https://drive.google.com/drive/folders/0AP-Yf32mH4IHUk9PVA` with ID `0AP-Yf32mH4IHUk9PVA`; the canonical Robert login-root for the first test is `admin`; and the first-pass allowed action is `metadata_only`. The next safe action is to prepare the no-API metadata-only test-inventory record and folder-register row for that shared Drive / `admin` root model, while leaving all Drive/API/auth/storage implementation gates closed.

## 2026-04-22 Docs-Only Folder Model Approved

Source Message-ID: `<CAAtX44YSN9Mr+xcP9woKfcKhONgVYYU73bV7xhqFkf1Nkue52A@mail.gmail.com>`; dedupe key `frank-direct-primary-CAAtX44YSN9Mr-xcP9woKfcKhONgVYYU73bV7xhqFkf1Nkue52A-mail-gmail-com`; owner/source Robert; subject `Re: File spaces next project plan`; from/date Robert Birnecker `<robert@kovaldistillery.com>` / Wed, 22 Apr 2026 14:34:20 -0700.

Decision: Robert approved the docs-only per-user/private plus shared/general file-spaces model from the prior `Next project` file/folder-management task. This remains attached to the existing Secure Info / Files Context Intake project and does not open a new project.

Concrete next action, superseded by the user-root clarification below: wait for Robert's first low-risk shared Drive test packet containing exactly:

1. exact login-root name, such as `admin` or `sonat`;
2. shared Drive folder/name or ID for the first test;
3. allowed first action, with `metadata_only` recommended first;
4. Drive/API/auth/token-storage approvals for that test.

State: TODO remains open because implementation is still blocked on that inventory packet plus the already recorded Drive/API/auth/storage approval gates. This update reconciles non-secret AI Workspace state only.

Scope preserved: no Drive API, OAuth, tokens, Google Cloud/IAM/Pub/Sub, browser auth, service account, folder creation, permission/share change, move/copy/upload/download/delete, local raw-file cache, Papers/MI, `.205`, production/deploy/commit/push, CRM/Portal/OPS mutation, mailbox body access, external reply, credential handling, or private folder-name inference was performed.

## 2026-04-22 User-Root Folder Clarification

Source Message-ID: `<CAAtX44a4y1DxTkza-T-Eg0huGXDOvzgO4wC7EPZUdG0KCs3Wrw@mail.gmail.com>`; dedupe key `frank-direct-primary-CAAtX44a4y1DxTkza-T-Eg0huGXDOvzgO4wC7EPZUdG0KCs3Wrw-mail-gmail-com`; owner/source Robert; subject `Re: File spaces folder model approved`; from/date Robert Birnecker `<robert@kovaldistillery.com>` / Wed, 22 Apr 2026 14:45:59 -0700.

Clarification: user-root folders are named by login, for example `admin` and `sonat`. Do not model user roots from arbitrary top-level folders. Frank and Avignon Google accounts have access to the shared Google Drive after the normal auth/API/storage approval path. The next test should happen inside the approved shared Drive model, not by agents creating, moving, copying, or reorganizing real top-level folders.

Current docs-only folder model:

1. Login-named user roots, such as `admin` and `sonat`, are the root folder names for user spaces.
2. Shared/general Drive remains the cross-role area for approved shared materials.
3. Frank/Avignon shared Drive access may be planned as available after auth approval, but no OAuth/API/browser-auth/token/storage action is approved by this clarification alone.
4. The first implementation slice remains docs-only until Robert provides the first low-risk test folder/name and Drive/API/auth/storage approvals.

Next exact input Frank should ask Robert for: provide the first low-risk shared Drive test folder or proposed folder name, the login-root it belongs under, allowed first action (`metadata_only` recommended first), and explicit Drive/API/auth/token-storage approvals for that test.

## 2026-04-23 First Test Packet Recorded

Approved inputs from Robert:

- Shared Drive target: `https://drive.google.com/drive/folders/0AP-Yf32mH4IHUk9PVA`
- Shared Drive / folder ID: `0AP-Yf32mH4IHUk9PVA`
- Starting user-root model for the first test: Robert's canonical documented login `admin`
- First-pass allowed action: `metadata_only`

Decision: the file-spaces approval inventory next action is now unblocked at the docs/planning/test-inventory level. The missing packet has been supplied strongly enough to define the first test model without inventing any new folder naming.

Approved first-test model to preserve:

1. shared Drive target remains `0AP-Yf32mH4IHUk9PVA`;
2. user-root naming continues to follow login slugs;
3. Robert's first test root is `admin`, using the canonical username already documented in this workspace;
4. first-pass action is limited to `metadata_only`;
5. no folder creation, permission change, copy/move, content read, or API/auth work is approved by this packet.

No-API metadata-only test-inventory record:

```yaml
intake_id: info-file-space-test:2026-04-23:shared-drive-0AP-Yf32mH4IHUk9PVA-admin
source_ref: drive-folder-id:0AP-Yf32mH4IHUk9PVA
owner: Robert
workspace: ai
storage_location: drive
sensitivity: internal_business
login_root: admin
shared_drive_target: https://drive.google.com/drive/folders/0AP-Yf32mH4IHUk9PVA
shared_drive_id: 0AP-Yf32mH4IHUk9PVA
allowed_actions:
  - metadata_only
disallowed_actions:
  - content_read
  - folder_create
  - permission_change
  - move_copy_delete
  - upload_download
  - oauth_or_token_setup
approval_state: planning_ready
approved_by: Robert
approved_at: 2026-04-23
summary: First approved file-spaces test record for the shared Drive model using Robert's canonical login-root `admin`; no-API and metadata-only only.
next_action: Prepare the folder-register row and future no-API dry-run parser inputs; keep Drive/API/auth/storage gates closed.
```

Folder-register row to carry forward:

```yaml
folder_register_row:
  folder_label: admin
  drive_folder_id: 0AP-Yf32mH4IHUk9PVA
  owner: Robert
  allowed_roles:
    - Robert
    - Frank
    - Avignon
  access_mode: metadata_only
  status: planning_ready
  notes: Shared Drive test model only; executable Drive/API/auth access remains separately gated.
```

Concrete next safe action:

- Use the recorded test-inventory row and folder-register row as the source packet for any future no-API dry-run parser/template work inside `ai_workspace`, while continuing to block all Drive/API/auth/storage implementation.

Remaining real blocker after this update:

- Drive/API/auth implementation is still blocked until the already-recorded approvals are provided: allowed accounts in executable form, OAuth vs service-account/delegated decision, exact scope grant path, token storage class/path, revocation owner, approved local path if outside `/Users/werkstatt/ai_workspace`, and non-secret audit log location.

Robert input still needed after this update:

- Not for the docs/planning/test-inventory slice.
- Yes for any actual Drive/API/auth implementation, because that existing gate remains open.

Scope preserved: no Drive API, OAuth, tokens, browser auth, mailbox access, Papers/MI, `.205`, Portal/CRM/OPS, production, deploy, commit, push, file move/copy/upload/download/delete, or folder creation was performed.

## 2026-04-24 Claude Google Drive Integration Packet Attached

User-supplied task summary attached to this same project:

- Task: `#1326`
- Title: `Google Drive integration via Claude Google Workspace account`
- Reported implementation bundle: `list.sh`, `download.sh`, `upload.sh`, `test.sh`, `CLAUDE.md`
- Reported secret contract: Infisical-backed env vars `GOOGLE_DRIVE_CLIENT_ID`, `GOOGLE_DRIVE_CLIENT_SECRET`, and `GOOGLE_DRIVE_REFRESH_TOKEN`
- Reported storage property: no credential files required on disk

Decision: this is enough to reduce blocker ambiguity and record a concrete implementation path, but not enough to treat the integration as locally reviewed or approved for execution. During this session the cited staging path `/tmp/gdrive-impl/` was not present on this machine, so the packet is recorded from the supplied summary only and remains pending local file-level verification if needed.

Blockers reduced by this packet:

1. The implementation shape is now concrete rather than hypothetical.
2. The secret-delivery model is narrowed to env-var injection from Infisical, which is materially better than ad hoc local credential files.
3. The account model is narrowed toward a Claude Google Workspace OAuth path instead of an unspecified Drive auth approach.

Remaining approvals still required before any implementation or live access:

1. Confirm that the Claude Google Workspace OAuth/refresh-token path is the approved executable-account path for this workflow.
2. Approve use of Infisical as the secret source for these three Drive secrets in this specific flow.
3. Confirm exact scopes by phase:
   - `drive.metadata.readonly` first for metadata-only listing;
   - `drive.readonly` only for approved content reads;
   - any write scope only after separate explicit approval for upload behavior.
4. Name the revocation owner and rotation path for the refresh token.
5. Confirm whether any runtime path outside `/Users/werkstatt/ai_workspace` is approved for non-secret working files or temporary downloads, or require stream-only handling.
6. Confirm the initial allowed file types and sensitivity tiers for the first live test.
7. Confirm the non-secret audit log destination for executed actions.

Recorded implementation instructions from the Claude packet summary:

1. Prefer env-injected credentials from Infisical over local JSON credential files.
2. Treat `list.sh` plus `drive.metadata.readonly` as the first live access slice.
3. Keep `download.sh` gated behind per-file or per-folder content-read approval.
4. Keep `upload.sh` fully gated until Robert separately approves write behavior.
5. Use `test.sh` only after the approved secrets are available through the approved runtime path and the first metadata-only target is confirmed.

Recommended next management packet:

- Approved account owner: Claude Google Workspace account or another named account.
- Secret source: Infisical approved for `GOOGLE_DRIVE_CLIENT_ID`, `GOOGLE_DRIVE_CLIENT_SECRET`, `GOOGLE_DRIVE_REFRESH_TOKEN`.
- First live scope: `drive.metadata.readonly`.
- First live target: shared Drive `0AP-Yf32mH4IHUk9PVA`, login-root `admin`, metadata-only only.
- Content read: not yet approved.
- Upload/write: not approved.
- Artifact review note: local `/tmp/gdrive-impl/` bundle was unavailable in this session, so implementation details remain summary-backed until the bundle is re-staged or copied into an approved local review path.

## Rollback And Non-Goals

Rollback:

- Disable API token or revoke OAuth grant.
- Remove or rotate service-account access.
- Delete local token from approved storage path.
- Delete generated non-secret summaries/manifests if wrong or overbroad.
- Move affected Drive files back to human-only access if permissions were changed in a later approved phase.
- Record incident in project-hub with affected IDs and corrective action.

Non-goals for this plan:

- No Drive folder creation by agents in this slice.
- No permission mutation by agents in this slice.
- No OAuth/browser login in this slice.
- No token storage or token path creation in this slice.
- No file download/upload in this slice.
- No mailbox reads.
- No Google Cloud/IAM/Pub/Sub mutation.
- No Papers/MI writes.
- No `.205` access.
- No production deploy, runtime service, LaunchAgent, or daemon changes.
- No credential, secret, or private document content exposure.

## Frank-Ready Completion Report

Subject: `Info/files intake plan added`

From/date: Robert Birnecker `<robert@kovaldistillery.com>` / Mon, 20 Apr 2026 09:00:19 -0700

Context: Robert approved the Info/files proposal as a plan and asked what is needed next to implement it safely, especially Google Drive API.

Proposed safe next action: Robert should approve or provide the Drive intake folder/shared-drive IDs, allowed accounts, OAuth vs service-account decision, Drive API scopes, token storage class/path, approved local runtime path if outside `/Users/werkstatt/ai_workspace`, and the first test file type/sensitivity tier. After that, a separate implementation worker can start with metadata-only intake records and a no-API dry run before any Drive API call.

Approval boundary: No Drive API, OAuth, Google Cloud/IAM/Pub/Sub, token storage, folder/permission change, file upload/download, mailbox read, Papers/MI write, `.205` access, runtime/daemon change, deploy, commit, push, or production change was performed. Those remain blocked until separate explicit approval.

Needed:

- Human-created or human-approved Drive folder/shared-drive ID.
- Allowed accounts and access model.
- OAuth client/source or service-account/delegated flow decision.
- Exact scopes: likely `drive.metadata.readonly` first, `drive.readonly` only after content-read approval.
- Token storage class/path and revocation owner.
- Decision on local download vs stream-only parsing.
- Initial allowed file types and sensitivity tiers.

Next: Frank may send Robert this completion report and ask for the approvals above. If Robert approves implementation, route a new worker; do not continue from this planning worker into API/auth/runtime work.

Decision state: Planning complete; implementation waiting on Robert/Security approvals.

Files updated: `project_hub/issues/2026-04-20-secure-info-files-context-intake-plan.md`, `project_hub/INDEX.md`, `TODO.md`, `HANDOFF.md`.

Confirmation: No secrets, Drive/API/auth/token/runtime/mailbox/Papers/MI/production changes were touched.

## Frank-Ready File-Management Intake Report

Subject: `File-management project intake attached to secure files plan`

Worker prompt source: `<CAAtX44Z0DxQ+ruJfOY2fSA2Un617-dfQiF3BQ7R8aaxDiQiQrA@mail.gmail.com>`; worker session `0774d4a8` / `file-management project intake and plan`. The same Message-ID is already recorded locally for AI Improvement Manager role expansion, so the source/context needs Robert clarification.

Decision: attached this to the existing `Secure Info / Files Context Intake Plan` instead of creating a new project. The available excerpt was truncated after `Project: File management.`, so the safe outcome is a clarification packet and approval-gated plan, not implementation.

Files updated: `project_hub/issues/2026-04-20-secure-info-files-context-intake-plan.md`, `project_hub/INDEX.md`, `TODO.md`, `HANDOFF.md`.

Plan produced: added a file-management clarification packet covering source-context ambiguity, likely goals, source-of-truth choice, allowed accounts, metadata logging, document analysis path, backup/retention, ownership, approval gates, and first safe test requirements.

Approval gates: no Drive/API/OAuth/service-account work, credentials, private mailbox bodies, Google Cloud/IAM/Pub/Sub, raw file upload/download/move/delete, live storage, external services, Papers/MI writes, production mutation, deploy, commit, or push. Any implementation requires Robert/Security/Drive or Code/Git approval depending on the chosen slice.

Checks run: read local non-secret `TODO.md`, `ToDo-append.md`, `HANDOFF.md`, `project_hub/INDEX.md`, and existing secure files/project-hub notes; checked `git status --short` only to identify pre-existing dirty state. No private file contents or external services were accessed.

Next safe action: Frank should ask Robert for the missing file-management requirements in the clarification packet, including whether the supplied Message-ID belongs to this file-management request. After Robert names the goal, source of truth, allowed accounts, first test file/folder, and approved action, Task Manager can route a separate implementation worker with the relevant gates still closed by default.
