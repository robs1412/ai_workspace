# Code/Git Manager AI Bridge Merge Review

- Date: 2026-04-19 09:05 CDT
- Owner: Code/Git Manager
- Scope: AI Workspace role/task-record docs, Frank bridge note coordination, Workspaceboard organigram source
- Status: Partially integrated; AI Workspace full merge blocked by dirty overlapping files

## Source Refs

- AI Workspace local branch: `main`
- AI Workspace merge base: `501d012b461d1731faf794ddf2d055d041b095bb`
- AI Workspace local-only commit: `8a1cd86` (`Record OPS dashboard task session credential incident`)
- AI Workspace incoming head: `32d5ded` (`Add AI bridge manager handoff docs`)
- Workspaceboard incoming head merged: `88cd7a3` (`Add AI manager roles to organigram`)

## Merge Decision

`git fetch --prune` completed for AI Workspace. A full AI Workspace merge was not performed because incoming `origin/main` changes overlap dirty local tracked files:

- `AGENTS.md`
- `HANDOFF.md`
- `TODO.md`
- `frank/HANDOFF.md`
- `frank/TODO.md`
- `project_hub/INDEX.md`
- `worker_roles/operating-model.md`

Safe selective integration from `origin/main` was limited to non-overlapping AI bridge and role files so Workspaceboard's new organigram entries have local role docs available. The local untracked `frank/drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt` differs from `origin/main` and was not overwritten.

Workspaceboard was dirty but the incoming commit touched only clean paths, so `/Users/werkstatt/workspaceboard` was fast-forwarded from `c689804` to `88cd7a3`, updating:

- `worker-organigram.html`
- `worker-organigram.php`

## Files Touched By This Review

AI Workspace selective restore from `origin/main`:

- `worker_roles/README.md`
- `worker_roles/ai-manager-dmytro.md`
- `worker_roles/ai-manager-robert.md`
- `worker_roles/claude-205-structure.md`
- `worker_roles/claude-bridge-worker.md`
- `worker_roles/claude-server-agent.md`
- `worker_roles/codex-integration-manager.md`
- `worker_roles/codex-local-agent.md`
- `worker_roles/codex-workspace-worker.md`
- `worker_roles/human-owners.md`
- `worker_roles/outreach-communicator.md`
- `project_hub/issues/2026-04-19-ai-bridge-macmini-handoff.md`
- `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`
- `frank/drafts/codex-claude-integration-plan-2026-04-19.txt`

This note:

- `project_hub/issues/2026-04-19-code-git-manager-ai-bridge-merge-review.md`

Workspaceboard fast-forward:

- `/Users/werkstatt/workspaceboard/worker-organigram.html`
- `/Users/werkstatt/workspaceboard/worker-organigram.php`

## Frank Coordination

Frank live session `5cdf0be8` received a bounded Code/Git Manager handoff through the local Workspaceboard API. The session summary reports:

- Claude bridge note sent through the approved Frank helper.
- Sent-log task id: `frank-2026-claude-codex-organigram-work-record-bridge`
- Message-ID: `<177660739756.67470.17168217427046240939@kovaldistillery.com>`
- Recipient recorded: `claude@koval-distillery.com`
- Current blocker: Robert was not copied; approved CC-capable path or approved separate-copy path is still needed.

No credential material or private mailbox body was printed in this note.

## Verification

- `php -l /Users/werkstatt/workspaceboard/worker-organigram.php` passed.
- Workspaceboard git status after fast-forward remains dirty only from pre-existing unrelated local files; `worker-organigram.html` and `worker-organigram.php` are clean at `88cd7a3`.
- AI Workspace full merge remains intentionally unperformed because dirty overlapping files require owner-aware reconciliation.
- Frank session `5cdf0be8` prompt delivery returned `ok: true` and session summary confirms the bridge-note state above.

## Boundaries Preserved

No `.205` access, OAuth, Papers/MI writes, Portal/CRM mutation, mailbox credential exposure, MCP exposure, deploy, live pull, service restart, destructive git action, reset, rebase, force-push, or dirty-file discard was performed.

## Recommended Next Step

Use an owner-aware manual merge plan for the seven overlapping AI Workspace files listed above. Reconcile `worker_roles/operating-model.md` first because it is the shared role-routing source. Then reconcile `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `frank/HANDOFF.md`, `frank/TODO.md`, and `project_hub/INDEX.md`. Keep the differing local Frank bridge draft until Robert or Task Manager decides whether the local sent draft or the incoming origin draft is canonical.

## Robert Correction Addendum

2026-04-19 09:06 CDT: Robert clarified that Frank must CC/copy Robert on the Claude bridge email. Frank history shows the Claude note was already sent Claude-only before that correction landed. The resulting Robert-copy/CC blocker is now local Mac mini work in:

- `frank/TODO.md`
- `frank/HANDOFF.md`

These files must be preserved during any AI Workspace merge. They are dirty local owner state from the live Frank session and overlap the incoming AI Workspace history. Do not overwrite them with `origin/main`.

Current Mac mini state after this review:

- `ai_workspace`: dirty/divergent, `main...origin/main [ahead 1, behind 8]`; full merge intentionally blocked.
- `workspaceboard`: dirty, now aligned with `origin/main` at `88cd7a3` after a safe fast-forward of clean organigram paths only.

TODO-count reconciliation signal:

- Robert reports MacBook local board total: `62` open items.
- Mac mini live board API reports: `13` open items from `/api/management/overview` at 2026-04-19 09:05 CDT.
- Treat this as a source reconciliation signal, not as proof that either side is authoritative. Compare MacBook board/TODO source exports with Mac mini live TODO/project-hub/board sources before changing counts, closing tasks, or syncing TODO files. Do not blindly overwrite local board/TODO state.

Additional boundary reaffirmed by Robert: no `.205`, OAuth, Papers/MI writes, Portal/CRM mutation, mailbox credential exposure, MCP exposure, deploy, live pull, service restart, or dirty-tree pull is approved.

## Frank Robert-Copy Resolution Addendum

2026-04-19 09:30 CDT: Robert reported the CC/BCC blocker was resolved by Frank worker `40bd2541`.

Resolved state:

- Frank and Avignon installed send helpers now support `--cc` and `--bcc`.
- To/Cc/Bcc validation preserves the primary-audience guardrails; external or non-primary recipients still require `--allow-non-primary`.
- Bcc addresses are not logged; only Bcc presence/count are recorded.
- The original Claude-only bridge email could not be retroactively CC'd, so Frank sent Robert a post-send copy.
- Robert-copy task id: `frank-2026-claude-codex-organigram-work-record-bridge-robert-copy`
- Robert-copy Message-ID: `<177660868352.77456.17905572612484589347@kovaldistillery.com>`

Protected local ownership added to this merge review:

- Machine-local runtime helper changes documented by Frank/Avignon:
  - `/Users/admin/.frank-launch/runtime/scripts/send_frank_email.py`
  - `/Users/admin/.avignon-launch/runtime/scripts/send_frank_email.py`
  - backups with suffix `send_frank_email.py.bak-20260419-cc-bcc`
- Git-tracked local docs containing the helper/change record:
  - `frank/HANDOFF.md`
  - `frank/TODO.md`
  - `frank/README_AGENT.md`
  - `avignon/HANDOFF.md`
  - `avignon/README.md`
- Local draft/source artifacts:
  - `frank/drafts/claude-codex-organigram-work-record-bridge-robert-copy-2026-04-19.txt`
  - `frank/drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt`

Merge implication: the previous Robert-copy/CC blocker is closed, but the resulting local Mac mini edits are now part of the protected dirty-tree state. Do not pull, restore, or merge over these files. Any eventual AI Workspace merge must preserve the 09:25 CDT Frank/Avignon helper-support records and the Robert-copy Message-ID above.

## Current Integration Plan

2026-04-19 09:40 CDT re-check:

- `ai_workspace` remains dirty/divergent: `main...origin/main [ahead 1, behind 8]`.
- `workspaceboard` is aligned with `origin/main` at `88cd7a3`; its remaining dirty files are pre-existing local UI/runtime/auth docs and source edits, not incoming remote organigram conflicts.
- A non-mutating `git merge-tree` check indicates committed `main` and `origin/main` can merge cleanly, so the blocker is the live dirty Mac mini working tree, not a committed-history conflict.

Already safe/integrated or matching `origin/main`:

- Workspaceboard organigram source: `worker-organigram.html`, `worker-organigram.php`.
- Role docs already matching `origin/main`: `worker_roles/README.md`, `worker_roles/claude-bridge-worker.md`, `worker_roles/codex-workspace-worker.md`, `worker_roles/human-owners.md`.
- Untracked local transfer helpers are byte-identical to `origin/main`: `scripts/ai_transfer_fetch.py`, `scripts/fetch_from_m4.sh`.
- Added AI bridge docs matching `origin/main`: `project_hub/issues/2026-04-19-ai-bridge-macmini-handoff.md`, `project_hub/issues/2026-04-19-codex-claude-papers-integration-plan.md`, `frank/drafts/codex-claude-integration-plan-2026-04-19.txt`.

Protected Mac mini owner state:

- Frank/Avignon CC/BCC helper resolution:
  - `frank/HANDOFF.md`
  - `frank/TODO.md`
  - `frank/README_AGENT.md`
  - `avignon/HANDOFF.md`
  - `avignon/README.md`
  - `frank/drafts/claude-codex-organigram-work-record-bridge-robert-copy-2026-04-19.txt`
- Broader Mac mini operational directives from 2026-04-17/18:
  - chief-of-staff routing
  - direct primary-owner intake acknowledgement
  - Gmail push pause until Monday, 2026-04-20 health check
  - mandatory completion reports
  - Avignon routine CRM/OPS/calendar authority
  - UI/report/page completion-location requirements
  - Salesreport live-pull completion rule
  - TODO-count reduction/source-access blocker cleanup records

Remaining files needing manual synthesis, not blind checkout/merge:

- `AGENTS.md`
- `HANDOFF.md`
- `TODO.md`
- `frank/HANDOFF.md`
- `frank/TODO.md`
- `project_hub/INDEX.md`
- `worker_roles/operating-model.md`
- `frank/drafts/claude-codex-organigram-work-record-bridge-2026-04-19.txt`

Recommended synthesis direction:

1. Treat the Mac mini dirty working tree as canonical for live operational policy, Frank/Avignon helper state, and current TODO counts.
2. Cherry-pick/synthesize only the MacBook `origin/main` AI Manager / Codex Integration / task-record spine additions into the Mac mini versions of `AGENTS.md`, `HANDOFF.md`, `TODO.md`, `project_hub/INDEX.md`, and `worker_roles/operating-model.md`.
3. Preserve the local sent Frank bridge draft and Robert-copy draft as canonical send artifacts; keep the differing `origin/main` bridge draft only as the MacBook-prepared source if Robert wants it archived separately.
4. Do not stage, commit, push, deploy, live-pull, restart services, access `.205`, perform OAuth work, write Papers/MI, mutate Portal/CRM, expose mailbox credentials, expose MCP, reset/rebase/force-push, or discard dirty files.

One concrete decision required before mutating the overlapping files:

**Decision:** Should Code/Git Manager manually synthesize the MacBook AI Manager / Codex Integration / task-record additions into the Mac mini canonical dirty docs while preserving all Mac mini Frank/Avignon, Gmail-pause, TODO-count, and completion-output edits?

Options:

- **Approve synthesis:** Edit only the eight overlap files listed above, preserving Mac mini operational content and adding the missing role-chain/task-record material from `origin/main`. No commit/push/deploy/service action.
- **Hold:** Leave all overlap files untouched and keep the current project note as the handoff until Robert or a dedicated doc-integration worker reviews the overlap.

## Synthesis Completion Addendum

2026-04-19 10:16 CDT: Robert approved the safe manual synthesis path. Code/Git Manager manually integrated the missing MacBook AI Manager / Codex Integration / task-record spine material into the Mac mini canonical dirty docs while preserving Mac mini operational content.

Files touched by this synthesis:

- `AGENTS.md`
- `HANDOFF.md`
- `worker_roles/operating-model.md`
- `frank/TODO.md`
- `project_hub/issues/2026-04-19-code-git-manager-ai-bridge-merge-review.md`

Source material synthesized:

- `origin/main` at `32d5ded` (`Add AI bridge manager handoff docs`)
- Workspaceboard organigram source already fast-forwarded to `88cd7a3` (`Add AI manager roles to organigram`)

Preserved Mac mini owner state:

- Frank/Avignon CC/BCC helper records and Robert-copy resolution
- Gmail push pause through Monday, 2026-04-20 health check
- mandatory completion-report rules
- chief-of-staff routing and direct primary-owner intake rules
- TODO-count cleanup and source-access cleanup records
- UI/report/page completion-location rules
- Salesreport live-pull completion rule
- local Frank bridge draft and Robert-copy draft send artifacts

Verification:

- `rg` confirmed the synthesized AI Manager, Codex Integration Manager, shared task-record, and agent registration boundary markers.
- `rg` confirmed `frank/TODO.md` no longer leaves the Robert-copy/CC item as an unresolved blocker.
- `git diff --check` passed for the synthesis-touched files.

Remaining state:

- `ai_workspace` remains dirty/divergent: `main...origin/main [ahead 1, behind 8]`.
- No full AI Workspace merge, pull over dirty files, staging, commit, push, deploy, live pull, service restart, reset, rebase, force-push, `.205` access, OAuth, Papers/MI write, Portal/CRM mutation, mailbox credential exposure, or MCP exposure was performed.
