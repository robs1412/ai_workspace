# Workspaceboard / AI Work Product Backup Plan

- Master Incident ID: `AI-INC-20260420-WORKSPACEBOARD-AI-BACKUP-01`
- Date Opened: 2026-04-20
- Date Completed:
- Owner: Robert / Frank / AI Workspace
- Priority: High
- Status: Planning complete; implementation blocked pending backup-target, storage, retention, encryption, and runtime-copy approvals

## Scope

Create a non-secret implementation plan for protecting Workspaceboard and AI work product. This plan covers backup inventory, what belongs in git versus artifact snapshots, exclusions, target assumptions, retention, verification, restore testing, ownership, cadence, alerts, manual first-run, dry-run, rollout phases, rollback, non-goals, and next approvals.

Source request:

- Message-ID: `<CAAtX44b5=F-CUH_Oas__z6nVV=tEgSv6qiW_NMuE-=JY2R1KiQ@mail.gmail.com>`
- Subject: `Re: Backup context for Workspaceboard and AI work product`
- From/date: Robert Birnecker `<robert@kovaldistillery.com>` / Mon, 20 Apr 2026 09:01:14 -0700
- Context: Robert asked Frank, "Now that we have the info from Claude... what is our plan to implement a backup?"

Related local non-secret context found:

- Frank backup context request to Claude, Message-ID `<177664819744.56612.7942568387030999886@kovaldistillery.com>`, asked for category-level `.200` external-drive and Claude/Papers/AI workspace backup details.
- Frank status report to Robert, Message-ID `<177664836625.57241.7623712127106052806@kovaldistillery.com>`, recorded that git covers committed/pushed repo work but not dirty/untracked files or runtime-only state.
- Current workspace/sync policy keeps `/Users/werkstatt/ai_workspace` and `/Users/werkstatt/<repo>` git-backed, while LaunchAgents, runtime copies, tmux/session state, logs, caches, secrets, `.env`, OAuth tokens, and mailbox credentials remain machine-local.
- Existing `AI_BOX_SECURITY.md` documents `scripts/ai_box_backup.sh` as a metadata-only backup helper for LaunchAgent plists, shell mapping, git heads, and launchctl status; it does not copy private runtime directories, mailbox credentials, OAuth tokens, `.private`, `.env`, or vault contents.

Local gap: no non-secret Claude reply record with concrete `.200` target path, cadence, encryption, retention, or restore-test details was found in local project/TODO/HANDOFF files during this pass. Treat Robert's current note as confirmation that Claude context exists, but require the category-level details below before implementation.

## Backup Scope Inventory

### Tier 1: Git-Backed Source And Planning

Use git as the primary protection for deterministic text/source work:

- `/Users/werkstatt/ai_workspace`: AGENTS, TODO/HANDOFF, project-hub, worker roles, policy docs, Frank/Avignon non-secret planning records.
- `/Users/werkstatt/workspaceboard`: Workspaceboard source, server code, UI source, docs, tests.
- `/Users/werkstatt/ai-bridge`: bridge schemas/templates/traces when the repo is configured with an approved remote.
- Other module repos under `/Users/werkstatt/<repo>` as their own git-backed source of truth.

Required before relying on git coverage:

- Code/Git Manager checks dirty and untracked files.
- Commit/push only after normal ownership review.
- Do not treat uncommitted local work, private drafts, machine-local runtime files, or untracked artifacts as protected by git.

### Tier 2: Artifact-Backed Non-Git Assistant Work Product

Use encrypted artifact snapshots for non-git but important AI work product:

- Workspaceboard session metadata and board-managed task state, using approved export APIs or state files only after owner review.
- Non-secret Workspaceboard session summaries, task briefs, and completion outputs.
- Frank/Avignon non-secret drafts, completion-report records, decision logs, and handled-mail state summaries.
- Project-hub manifests and TODO/HANDOFF snapshots at backup time.
- AI-Bridge local artifacts not yet pushed to a remote, after Code/Git Manager classifies them as non-secret.
- Metadata about installed LaunchAgents and runtime health, not private credential payloads.

Recommended format:

- Per-run manifest: `manifest.json` plus human-readable `README.md`.
- One tar/zstd archive or rsync snapshot per run, encrypted at rest if it contains non-public internal assistant state.
- Include hashes and file counts for restore verification.
- Store only category labels for sensitive exclusions, never secret values.

### Tier 3: Machine-Local Runtime State Candidates

Runtime state may be backed up only after Robert/Security Guard approves exact categories:

- Workspaceboard installed runtime metadata and non-secret state needed to restore sessions.
- Frank/Avignon runtime state needed for duplicate protection and completion-report continuity.
- LaunchAgent plist copies and launchctl status snapshots.
- Shell/`ws` mapping and local service inventory.

Do not copy private runtime directories blindly. Runtime backup must be inventory-first, then dry-run, then narrow approved copy.

## Exclusions And Secrets

Never include these in git or plain backup manifests:

- passwords, app passwords, API keys, OAuth refresh/access tokens, client secrets, SSH private keys, private key material, Keychain secrets, `.env` values, mailbox credentials, private mailbox bodies, private Papers/MI document bodies, private customer/contact content beyond approved metadata, and vault passphrases.

Approval-gated and category-only until approved:

- `.private`, `.env*`, encrypted sparsebundle payloads, private vault contents, raw mailbox stores, OAuth token caches, live browser profiles, SSH config/private identities, `.205`, `.200`, system LaunchAgent/LaunchDaemon directories outside `/Users/werkstatt`, and any path outside the workspace boundary.

## Backup Target Assumptions

No target is approved by this plan. Candidate targets:

- Primary local staging: an approved owner-only path under `/Users/werkstatt` for dry-run manifests and encrypted test artifacts.
- External/offsite target: Claude-referenced `.200` external-drive path, if Robert/Claude/Dmytro approve the exact device/path, mount/access method, encryption policy, and retention.
- Git remotes: only for safe source/planning repos, not runtime/private artifacts.

The `.200` external drive is a candidate only. Do not access `.200`, mount drives, create folders, rsync, tar, copy, or test restore against it until the exact approved target and method are recorded.

## Retention And Versioning

Proposed default, pending Robert approval:

- Daily encrypted snapshots for 14 days.
- Weekly encrypted snapshots for 8 weeks.
- Monthly encrypted snapshots for 6 months.
- Keep git history separately through normal remotes.
- Keep first-run baseline and first successful restore-test artifact until Robert approves pruning.

Versioning requirements:

- Timestamped run id, machine id, host, source commit heads, included category list, excluded category list, snapshot method, encryption state, target label, and verification result.
- Never record secrets in manifests.

## Verification And Restore Test

Every run should produce:

- Archive hash.
- File count and byte count by category.
- Git head list for each included repo.
- Exclusion checklist.
- Dry-run diff for rsync-like phases.
- Restore checklist result.

Restore test proposal:

1. Restore only to a temporary approved test path under `/Users/werkstatt`.
2. Verify manifest parsing, hashes, and expected category counts.
3. Verify docs/project-hub/TODO readability.
4. Verify Workspaceboard session export can be parsed without starting runtime services.
5. Verify Frank/Avignon non-secret state can be read as logs/manifests without mailbox access.
6. Do not load LaunchAgents, start services, send mail, mutate mailbox state, or overwrite live runtime during restore tests unless separately approved.

## Ownership

- Robert: approves target, cadence, retention, encryption/storage policy, runtime-state categories, and whether `.200` is in scope.
- Frank: sends Robert-facing completion report and tracks email-derived source state.
- Claude: provides non-secret `.200` and Claude/Papers/AI backup context at category level.
- Dmytro: confirms `.200`/Claude-side storage assumptions, service-account/SSH path if any, and whether Claude/Papers artifacts should be included directly or represented by manifests.
- Security Guard: reviews secret exclusions, encryption/storage, service-account/SSH, runtime-copy, `.200`/`.205`, and restore-test boundaries.
- Code/Git Manager: reviews dirty/untracked repo state and decides what must be committed/pushed versus artifact-backed.
- Workspaceboard worker: implements any future exporter or runtime-state manifest only after Code/Git and Security gates.

## Schedule / Cadence Proposal

Phase cadence, pending approval:

- Manual first run only.
- Then daily at a low-activity window if the first restore test passes.
- Weekly human-readable summary to project-hub/HANDOFF.
- Failure alert to Frank/Robert only after the alert channel and send authority are approved.

No LaunchAgent, LaunchDaemon, cron, schedule, or cadence change is approved by this planning record.

## Failure Alerts

Proposed alert levels:

- `warning`: backup skipped, target unavailable, dirty repo inventory not reviewed, non-critical category omitted.
- `critical`: archive failed, encryption failed, manifest/hash mismatch, retention prune error, restore-test mismatch.

Alert channel candidates:

- Frank Robert-only report.
- Workspaceboard task/status row.
- Project-hub issue update.

No automated alert send is approved until Robert approves recipient, channel, frequency, and duplicate-suppression behavior.

## Manual First-Run Procedure

Implementation-ready procedure after approvals:

1. Confirm exact target path/device and encryption policy.
2. Confirm source category allowlist and exclusions.
3. Run inventory-only mode and write a non-secret manifest.
4. Run dry-run copy/snapshot and review includes/excludes.
5. Code/Git Manager reviews dirty/untracked work and commits/pushes safe source work separately when approved.
6. Security Guard approves the final first-run command and destination.
7. Run first snapshot.
8. Verify hashes and manifest.
9. Restore to approved temporary test path.
10. Record result in project-hub and HANDOFF.

## Dry-Run Phase

Dry-run must print only:

- category names,
- counts,
- sizes,
- relative non-sensitive paths where safe,
- excluded category labels,
- target label, not secret target credentials,
- planned operations.

Dry-run must not:

- mount external drives,
- copy files,
- read private payload contents,
- print secrets,
- access `.200`/`.205`,
- mutate runtime state,
- start/stop services,
- send mail,
- commit/push,
- deploy,
- live-pull,
- prune/delete.

## Rollout Phases

### Phase 0: Approval Packet

Gather Robert/Claude/Dmytro inputs and Security Guard approval. No implementation.

### Phase 1: Inventory-Only

Create a script or documented command that lists approved categories and exclusions without copying.

### Phase 2: Local Encrypted Snapshot Dry Run

Build manifest and dry-run artifact plan to an approved local staging label only.

### Phase 3: First Manual Snapshot

Run one manual encrypted snapshot after final approval.

### Phase 4: Restore Test

Restore to an approved temporary path and verify without starting services.

### Phase 5: External Mirror

Mirror encrypted snapshots to `.200` or another approved target only after target approval and first restore test.

### Phase 6: Cadence And Alerts

Add a schedule and failure reporting only after the manual run and restore test are proven.

## Rollback Plan

- If inventory/dry-run is wrong: edit the allowlist/exclusion list; no data should have moved.
- If a manual snapshot fails: delete only the incomplete new snapshot after approval; keep prior snapshots.
- If restore test fails: preserve failed test output manifest for review; do not overwrite live state.
- If external mirror fails: keep local encrypted snapshot; retry only after target/mount/network issue is resolved.
- If any secret is accidentally included: stop, quarantine the artifact, rotate affected secret through approved owner path, and record non-secret incident metadata only.

## Non-Goals

- No backup execution from this planning task.
- No `.200` or `.205` access.
- No external drive mount.
- No rsync/tar/git bundle execution.
- No LaunchAgent/LaunchDaemon/schedule creation or edit.
- No runtime copy.
- No mailbox read/export/body exposure.
- No credential/token/private-key access.
- No production mutation.
- No commit/push/deploy/live pull.
- No restore into live paths.

## Needed Approvals / Inputs

Robert must approve or provide:

- Backup target path/device label.
- Whether `.200` external-drive path is approved and who owns it.
- Allowed first implementation strategy: inventory-only, rsync dry-run, tar/zstd archive, git bundle, or a combination.
- Schedule/cadence.
- Retention period.
- Encryption/storage policy.
- Whether runtime state may be copied and which categories.
- Restore-test scope and temporary test path.
- Failure alert channel and recipient behavior.

Claude must provide:

- Category-level description of current Claude/Papers/AI workspace backup process.
- Whether `.200` currently receives AI work product backups.
- Included/excluded categories.
- Manual versus automated cadence.
- Encryption/versioning/offsite status.
- Restore/test-restore approach.
- Recommended additions for Workspaceboard, Frank, Avignon, Codex, and AI-Bridge.

Dmytro must provide or approve:

- `.200` host/device/path ownership and access boundary.
- Whether a service account, SSH identity, or human-mounted path is intended, without sharing secrets in chat/docs.
- Whether `.200` should receive encrypted archives only or also git bundles.
- Whether Claude/Papers work product should be included directly, mirrored separately, or represented by manifests.
- Recovery contact/rollback expectation if `.200` or the backup path is unavailable.

Security Guard must approve:

- Secret exclusions.
- Encryption method/storage class.
- Key/passphrase handling.
- Whether any path outside `/Users/werkstatt` may be touched.
- Runtime-state copy boundary.
- `.200`/`.205` access boundary.
- Any automated alert/send behavior.

Code/Git Manager must approve:

- Dirty/untracked file treatment before claiming git coverage.
- Any commit/push or git bundle strategy.
- Ownership for a future Workspaceboard exporter or backup helper.

## Proposed Safe Next Action

Send Robert a Frank completion report with this plan location and ask for the approval packet above. The first implementation worker should be limited to inventory-only design after Robert/Claude/Dmytro provide the missing target and storage answers.

## Approval Boundary

This plan approves documentation and state recording only. It does not approve backup execution, copying, drive mounting, remote access, credential access, runtime-state reads beyond non-secret metadata, service changes, scheduling, commits, pushes, deploys, live pulls, or restore into live paths.

## Completion Report Draft

Subject: `Workspaceboard / AI backup plan ready for approval`

Robert,

I created the non-secret backup implementation plan for Workspaceboard and AI work product:

`project_hub/issues/2026-04-20-workspaceboard-ai-backup-plan.md`

The recommended model is git for committed source/planning records, encrypted artifact snapshots for non-git assistant work product, and only then an approved external/offsite mirror such as the `.200` external-drive path if you, Claude, and Dmytro confirm the target and storage rules.

Before implementation, I need approval for the backup target/device path, whether `.200` is in scope, the allowed rsync/tar/git-bundle strategy, cadence, retention, encryption/storage policy, service-account or SSH path if any, whether runtime state may be copied, and the restore-test boundary. Claude/Dmytro also need to provide category-level `.200` and Claude/Papers backup details if they are not already in the approved notes.

No backup was run, no files were copied, no external drive was mounted, no `.200`/`.205` access occurred, no credentials or private contents were accessed, no runtime/schedule/deploy/git action was performed.

Frank

## Verification Notes

Planning-only verification performed:

- Read root TODO and append queues.
- Searched local non-secret TODO, HANDOFF, Frank, project-hub, worker-role, and docs surfaces for backup, Claude context, Workspaceboard, AI work product, external drive, `.200`, git sync, and hard-server-mode references.
- Read relevant non-secret project logs for AI workstation sync, Workspaceboard/Frank response recovery, Codex/Claude/Papers integration, AI box security, and legacy archive handling.
- Did not read `.private`, `.env`, credential files, mailbox bodies, private Papers/MI contents, external drive contents, or backup payloads.

## Follow-Ups

- Frank should send the completion report above to Robert unless Robert suppresses email.
- Once approvals are supplied, create a new implementation worker for Phase 1 inventory-only design.
- Keep implementation blocked until Security Guard and Code/Git Manager close their respective gates.
