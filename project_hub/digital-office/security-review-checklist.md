# Security Review Checklist: No-Write Papers Projection

Status: local checklist for Security Guard review before implementation or live writer approval.

## Current Slice

- [x] Local docs/projection pack only.
- [x] No live Papers writes.
- [x] No `.205` or `.17` writes.
- [x] No OPS/Portal database changes.
- [x] No credential/OAuth/token/key reads.
- [x] No MCP exposure changes.
- [x] No notifications or email sends.
- [x] No Frank/Avignon runtime changes.
- [x] No service restart, background daemon, deploy, or live runtime mutation.

## Required Before Code Implementation

- [ ] Code and Git Manager preflight for target repo and dirty worktree state.
- [ ] Confirm implementation target: likely `/Users/werkstatt/workspaceboard`.
- [ ] Confirm generated exports go to an approved local path.
- [ ] Confirm no parser reads `.private`, `.env`, credential, mailbox, cache, log, or token files.
- [ ] Confirm fixture/sample data contains no private email body content.
- [ ] Confirm export files are rebuildable and disposable.

## Required Before Any Live Papers Writer

- [ ] Robert approves writer identity.
- [ ] Robert approves target Papers space.
- [ ] Robert approves first record types.
- [ ] Robert approves redaction level.
- [ ] Robert approves duplicate/update behavior.
- [ ] Robert approves rollback/export procedure.
- [ ] Security Guard reviews API auth and least-privilege scope.
- [ ] Dry-run diff mode exists and defaults to no-write.
- [ ] Live writer is disabled by default and cannot run through MCP exposure by accident.

## Required Before Google Drive OAuth Automation

- [ ] Robert decides OAuth/token storage location.
- [ ] Tokens are not stored in Google Drive-synced planning files unless Robert explicitly accepts that risk.
- [ ] Tokens are not stored in git.
- [ ] Machine-local/keychain/secret-manager path is documented without printing secret contents.
- [ ] Revocation/rotation procedure is documented.

## Blockers

- Google Drive OAuth/token storage decision is still open.
- Live Papers write authority is not approved.
- OPS/Portal read/write expansion is not approved.
- Frank/Avignon email-derived projection requires stricter redaction approval.
