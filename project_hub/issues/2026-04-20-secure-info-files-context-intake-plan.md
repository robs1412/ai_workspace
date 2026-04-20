# Secure Info / Files Context Intake Plan

- Master Incident ID: `AI-INC-20260420-INFO-FILES-CONTEXT-INTAKE-01`
- Date Opened: 2026-04-20
- Owner: AI Workspace / Frank / Codex Integration Manager
- Priority: Medium
- Status: Planning complete; implementation blocked pending Robert/Security approvals
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
9. Whether agents may download raw files locally, or must stream/read without durable raw copies.
10. Who may approve individual file reads after upload.
11. Audit log location for non-secret intake events.
12. Rollback behavior for accidental ingestion or wrong-file summaries.

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
