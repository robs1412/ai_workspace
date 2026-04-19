# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260417-FRANK-AVIGNON-RUNTIME-CRM-INTAKE-01`
- Date Opened: 2026-04-17
- Date Completed:
- Owner: AI Workspace / Avignon / Frank
- Priority: Urgent
- Status: Open

## Scope

Inspect Frank and Avignon LaunchAgents/runtime status, switch supported auto polling to 60 seconds, and audit Avignon's Sonat-originated CRM-addition intake from the week of 2026-04-13 without exposing private email bodies, credentials, or CRM field values.

## Symptoms

Robert reported that Sonat said Avignon had not acted on CRM-addition requests all week/day and did not respond with an update of everything uploaded to CRM based on Sonat's requests.

## Root Cause

Avignon's live inbox cycle has a special CRM branch only for Sonat messages with attachments. Text-only CRM-addition messages fell through to the generic ambiguous-email-review path. The runtime archived those messages to `Handled` and recorded or reused broad `avignon-email-review-*` decision items, but did not create visible Avignon/importer work, did not run Importer, and did not send Sonat a completion/update response.

Frank also had a runtime health issue: the auto job was at `StartInterval = 300` and last exit `1` because a malformed historical JSONL row in its machine-local automation log stopped `frank_auto_runner.py`.

## Repo Logs

### ai_workspace

- Repo Log ID: `avignon-sonat-crm-intake-recovery-2026-04-17`
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Recorded the Avignon CRM intake miss in `avignon/TODO.md`, `avignon/HANDOFF.md`, `avignon/EMAIL_DERIVED_DECISIONS.md`, and routed a guarded Importer queue item in `/Users/werkstatt/importer/ToDo-append.md`.

### machine-local LaunchAgent/runtime state

- `com.koval.frank-auto`: changed `StartInterval` from `300` to `60`, reloaded/kickstarted, and verified loaded `run interval = 60 seconds`.
- `com.koval.avignon-auto`: changed `StartInterval` from `300` to `60`, reloaded/kickstarted, and verified loaded `run interval = 60 seconds`.
- `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`: hardened `load_automation_log` to skip malformed JSONL rows.
- `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`: increased unseen scan default to `100`, changed generic tracked replies to local/no-email handling, and replaced batch inbox-review escalation with one-at-a-time decision prompts.
- `/Users/admin/.frank-launch/runtime/scripts/frank_auto_runner.py`: added `Handled` filing for future no-action messages.
- `/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py`: stopped archiving ambiguous/unprocessed decision items by default; only handled/no-action/local-follow-up categories are archived automatically.
- `/Users/admin/.avignon-launch/state/EMAIL_DERIVED_DECISIONS.md`: added the active recovery item so the runtime/local ledger reflects the miss.

## Verification Notes

- `plutil -lint` passed for both modified auto LaunchAgent plists.
- `launchctl print` verified `run interval = 60 seconds` for Frank and Avignon auto jobs.
- Avignon auto job verified last exit `0`.
- Frank auto job verified last exit `0` after the malformed JSONL skip patch.
- Frank INBOX check after runtime patch showed `39` unread/open messages and `0` unlogged source IDs. A synthetic no-send prompt-shape check verified labels: `Subject`, `From/date`, `Context`, `Proposed safe next action`, `Approval boundary`, `Needed`, `Next`, and `Decision`.
- Decision-vs-file cleanup pass filed two already-completed Frank INBOX CRM messages to `Handled`. Frank post-pass count: `37` unread/open, `16` unclear one-at-a-time decision candidates, `21` local/routed or approval-gated open items, and `0` remaining no-action filing candidates. Avignon post-pass count: `0` INBOX messages.
- Metadata-only Avignon mailbox audit found 13 Sonat-originated CRM-related messages since 2026-04-13. The 2026-04-14/2026-04-15 pair was completed through Importer session `10b9346d` / Import ID `52`; ten 2026-04-17 CRM-addition messages remain queued for recovery.
- 2026-04-18 execution update: Importer session `86dc0b04` completed Import ID `56` for the five importer-safe rows with 5 contact creates, 3 account creates, 0 skipped rows, and phpList/account-filter/contact-filter modes left `none`. Portal session `44b8a370` completed source `9` with account `367149` and source `5` with account `367150`, 2 existing contact links, and activity/note `367151`; verification found the expected account/contact and activity relations. Avignon sent Sonat status/follow-up/current-state reports under task ids `avignon-sonat-crm-intake-recovery-2026-04-17-status-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-follow-up-2026-04-18`, and `avignon-sonat-crm-intake-recovery-2026-04-17-current-state-2026-04-18`. Remaining blockers are source `1` target/contact ambiguity and source `10` target distributor-account ambiguity; source `7` is held until recovery decisions close.

## Rollback Plan

- Restore `StartInterval` to `300` in `/Users/admin/Library/LaunchAgents/com.koval.frank-auto.plist` and `/Users/admin/Library/LaunchAgents/com.koval.avignon-auto.plist`, then `launchctl bootout/bootstrap/enable` the two labels.
- Revert the Frank runtime JSONL skip patch only if a stricter log-repair path replaces it.

## Follow-Ups

- Importer/Portal deterministic execution for `avignon-sonat-crm-intake-recovery-2026-04-17` is complete except source `1` and source `10`, which need Sonat target/link decisions after deterministic checks did not resolve unique targets. Hold source `7` until those decisions close, then send the final completion/status report.
- Avignon runtime should get a separate safe CRM-intake routing patch so future text-only Sonat CRM-addition requests create visible work instead of generic ambiguous review items.
- Sonat has received the required status/follow-up/current-state reports for the completed slices; send the final completion report only after source `1`, source `10`, and held source `7` are resolved and verified.
