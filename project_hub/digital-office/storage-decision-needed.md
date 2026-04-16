# Storage Decision Needed: Google Drive OAuth Versus Machine-Local

Status: human decision needed before any Google Drive OAuth-backed ingestion, export, or sync automation.

## Decision Question

Where should OAuth credentials and token caches live if future Digital Office projection tooling needs Google Drive access?

## Recommendation

Use machine-local storage or an approved secret manager/keychain path. Do not store OAuth credentials, refresh tokens, access tokens, client secrets, private keys, or app passwords in Google Drive-synced planning folders or git.

## Options

### Option A: Machine-Local Storage

Recommended default.

- Store OAuth token cache under a machine-local private path or OS keychain.
- Keep tokens out of Google Drive and git.
- Each machine authorizes independently or receives an approved local secret provisioning step.
- Best fit for the current rule that runtimes, credentials, OAuth material, `.env`, keys, and mailbox secrets remain machine-local.

Tradeoff: each machine may need its own setup and revocation tracking.

### Option B: Approved Service Account Or Secret Manager

Acceptable if Robert wants shared automation.

- Use a Google-managed service account or delegated app flow.
- Store private key/token material only in an approved secret manager or machine-local keychain.
- Record only non-secret references in project-hub.

Tradeoff: needs a real access/rotation owner and a least-privilege review.

### Option C: Google Drive-Synced OAuth Storage

Not recommended.

- Would place OAuth material in a sync system that already holds planning files and is visible across machines.
- Increases accidental exposure, stale token, and broad replication risk.
- Should require explicit Robert approval, Security Guard review, and a written rotation/revocation plan before use.

## Current Rule Until Decided

No Digital Office projection code should read, create, copy, or store Google Drive OAuth material. The projection pack can reference Google Drive documents as source paths only when already present as non-secret planning records.
