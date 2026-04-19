# OAuth/Token Storage Policy Review

- Status: policy closed; rejected storage targets are closed as policy, and implementation remains blocked before any OAuth/token handling or Drive-backed automation.
- Reviewed: 2026-04-16 17:18 CDT on Macmini.lan; blocker review updated 2026-04-17.
- Scope: local Digital Office planning docs only.

## Boundary Held

- Read only local AI Workspace / Digital Office docs.
- Did not read, create, copy, print, or validate credentials, OAuth tokens, Google Drive files, Papers data, runtime state, mailbox/email content, or secret-bearing files.
- Did not inspect live Google Drive, Papers, OPS/Portal, `.205`, `.17`, Frank/Avignon runtime, MCP config, keychain contents, or any external service.

## Decision Question

Where should OAuth credentials and token caches live if future Digital Office projection tooling needs Google Drive access?

## Recommendation

Use machine-local storage or an approved secret manager/keychain path. Do not store OAuth credentials, refresh tokens, access tokens, client secrets, private keys, app passwords, token caches, or session secrets in Google Drive-synced planning folders, Google Drive-synced runtime folders, Papers records, normal manifests, logs, chat, or git.

Default implementation rule:

- Single-machine or per-machine automation: store tokens in the local OS keychain or another machine-local private path with owner-only permissions.
- Shared automation: use an approved secret manager, Google-managed service account/delegated app flow, or local keychain-backed provisioning path with least privilege, named owner, rotation/revocation procedure, and non-secret reference labels in project-hub only.
- Documentation: record only the storage class, owner, app/client label, scope summary, and rotation/revocation procedure. Never record token values, client secrets, private keys, or refresh tokens.

This recommendation is strong enough for Task Manager, Decision Driver, Security Guard, and future implementation workers to reject Google Drive-synced, Papers-backed, manifest/log/chat, or git-tracked token storage without asking Robert again.

## Options

### Option A: Machine-Local Storage

Recommended default for the next slice.

- Store OAuth token cache under a machine-local private path or OS keychain.
- Keep tokens out of Google Drive and git.
- Each machine authorizes independently or receives an approved local secret provisioning step.
- Best fit for the current rule that runtimes, credentials, OAuth material, `.env`, keys, and mailbox secrets remain machine-local.

Tradeoff: each machine may need its own setup and revocation tracking.

### Option B: Approved Service Account Or Secret Manager

Acceptable if Robert wants shared automation across machines or unattended workers.

- Use a Google-managed service account or delegated app flow.
- Store private key/token material only in an approved secret manager or machine-local keychain.
- Record only non-secret references in project-hub.

Tradeoff: needs a real access/rotation owner and a least-privilege review.

### Option C: Google Drive-Synced Or Broadly Replicated OAuth Storage

Rejected by policy unless Robert explicitly overrides the recommendation after Security Guard review.

- Would place OAuth material in a sync system, planning record, normal manifest/log/chat, or repository surface that already exists for broad coordination rather than secret custody.
- Increases accidental exposure, stale token, and broad replication risk.
- Should require explicit Robert approval, Security Guard review, and a written rotation/revocation plan before use.

## Current Rule Until A Storage Path Is Approved

No Digital Office projection code should read, create, copy, or store Google Drive OAuth material. The projection pack can reference Google Drive documents as source paths only when already present as non-secret planning records.

Closed policy:

- Implementation workers may reject Google Drive-synced files/folders, Papers records, normal manifests, logs, chat, and git as token or credential storage without further escalation.
- Non-secret docs may record only the storage class, owner, app/client label, scope summary, rotation/revocation procedure, and non-secret reference labels.

Implementation gate if future Drive-backed automation is requested:

> Use Option A as the default storage class for per-machine automation, or name the approved secret manager/keychain/service-account path for shared automation.

Until an implementation slice is approved, Google Drive-backed ingestion/export/sync automation remains blocked. Local no-write projection work that does not touch OAuth, Drive, Papers, runtime, or email can continue.
