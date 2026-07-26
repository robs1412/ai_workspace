# Multi-Repo Preservation And Cleanup

- Master Incident ID: `AI-INC-20260726-MULTI-REPO-CLEANUP-01`
- Date Opened: 2026-07-26
- Date Completed: 2026-07-26
- Owner: Robert / Codex
- Priority: High
- Status: Completed

## Scope

Clean the active repositories under `/Users/werkstatt` without deleting, overwriting, or hiding source work. Preserve features and durable evidence in focused commits, keep private/runtime artifacts local under ignore rules, reconcile clean behind branches by fast-forward only, and verify final repository state.

## Symptoms

- Ten active repositories had modified or untracked work.
- Salesreport had twelve untracked report/source artifacts plus a generated Python cache.
- BID had source changes, eighty finance readback artifacts, and was one commit behind upstream.
- AI Workspace mixed source code and durable records with private mailbox bodies, runtime state, invoice PDFs, exports, and large source images.
- Workspaceboard had one unpushed commit plus three modified source files.

## Root Cause

Completed feature work and operational evidence had accumulated without focused preservation commits. Runtime and private artifacts also lacked several narrow ignore rules, making legitimate local state appear as source-code dirt.

## Repo Logs

### salesreport

- Repo Log ID: `REPO-SALESREPORT-20260726`
- Commit SHA: `9376c54`
- Change Summary: Preserved Avignon/Whole Foods and California report generators, reports, and access-gated pages. Replaced hard-coded private credential locations with environment configuration and ignored Python/private-upload runtime artifacts.

### bid

- Repo Log ID: `REPO-BID-20260726`
- Commit SHAs: `420d4fd`, `271530e`
- Change Summary: Preserved receipt capture, payroll, import, and Square reporting improvements plus eighty Naomi finance readbacks; rebased cleanly over upstream Square customer export work.

### dist

- Repo Log ID: `REPO-DIST-20260726`
- Commit SHA: `a7f372b`
- Change Summary: Preserved barrel-program manual price override behavior and deployed it to the live DIST checkout.

### workspaceboard

- Repo Log ID: `REPO-WORKSPACEBOARD-20260726`
- Commit SHAs: `6a1d02a`, `853f6d3`
- Change Summary: Preserved the model-selection update, monitor-count readback, and source-context guard for blocker emails.

### ai_workspace

- Repo Log ID: `REPO-AI-WORKSPACE-20260726`
- Commit SHAs: `d94c643`, `da8697f`, `4e5e97a`, `e92b5fe`, `3aec020`
- Change Summary: Preserved worker reliability changes, Avignon market intelligence, National Outreach execution tools, classroom and Order Assistance tooling, and project records. Added narrow ignore coverage for mailbox bodies, worker state, private downloads, generated exports, and large private source images without deleting or moving those files.

### Other Repositories

- `_birnecker.com` `27ba300`: preserved family AI class handouts.
- `database` `dc60593`: preserved self-distribution account inclusion in incoming-order selection.
- `lists` `8b4f464`: preserved the self-distribution rollout email draft; no campaign was sent.
- `playwright-scraper` `09f9585`: preserved the ILCC delinquency/cure scraper tools.
- `ai-bridge` `2f04bfb`: preserved the Claude read-only snapshot contract locally; this repository has no configured remote.
- `forge`, `ops`, and `portal`: clean fast-forward pulls only; no local source rewrite.

## Verification Notes

- Salesreport: six touched PHP files passed `php -l`; the publisher passed Python compilation; local and live checkouts read clean at `9376c54`.
- BID: seven touched PHP files passed `php -l`, the Square wrapper passed `bash -n`, and the two local commits rebased without conflict.
- DIST: both touched PHP files passed `php -l`; live checkout read clean at `a7f372b`.
- Workspaceboard: PHP/JavaScript syntax checks passed and all 129 tests passed.
- AI Workspace: 38 PHP files passed lint, nine Python files compiled, two shell scripts passed syntax checks, and the plist passed validation.
- No staged or unstaged source changes remained after preservation. Private/runtime files remained in place and became ignored.
- Workspaceboard LaunchAgent reinstall could not bootstrap because this shell had no usable macOS GUI launchd domain. The existing local API remained responsive; repository cleanup and push succeeded, but runtime restart was not claimed.

## Rollback Plan

Each feature group is isolated in a focused commit and can be reverted independently with a normal reviewed revert commit. Private/runtime artifacts were not deleted or moved, so no data restoration is required for ignored files.

## Follow-Ups

- Configure a remote for `ai-bridge` if that repository should be backed up centrally.
- Refresh the Workspaceboard LaunchAgent from an interactive GUI login session if immediate runtime reload is required.
