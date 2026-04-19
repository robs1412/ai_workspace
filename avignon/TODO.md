# TODO — avignon

Updated: 2026-04-19 10:16 CDT (Machine: Macmini.lan)

## In Progress

- `avignon-sonat-crm-intake-recovery-2026-04-17`
  - Status: active recovery/email-quality correction for 10 missed Sonat CRM/status items. Robert corrected on 2026-04-19 that this is not simply waiting on Sonat; current owner/path is Robert -> Frank/Claude-context coordination -> Avignon worker `b583edb6` with Task Manager visibility.
  - Importer execution: Importer session `86dc0b04` completed Import ID `56` for the 5 importer-safe rows; contacts `367141`, `367143`, `367144`, `367146`, `367148`; accounts `367142`, `367145`, `367147`; 0 skipped rows; phpList/account-filter/contact-filter all `none`.
  - Portal execution: source `9` completed as bounded account-only CRM work with account `367149`; source `5` completed with account `367150`, 2 existing contact links, and activity/note `367151`.
  - Remaining recovery questions must be handled as a concrete action plan, not a vague wait: privately re-check source `1`, source `10`, source `7`, Robert's forwarded Frank message, and Claude/Frank bridge context; decide what can be resolved from existing context; route safe bounded Portal/Importer work if a unique target is verified; otherwise send one corrected concise Sonat-facing answer sheet with exact answer format.
  - Reports sent to Sonat: `avignon-sonat-crm-intake-recovery-2026-04-17-status-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-follow-up-2026-04-18`, `avignon-sonat-crm-intake-recovery-2026-04-17-current-state-2026-04-18`, and `avignon-sonat-crm-intake-recovery-2026-04-17-target-link-decisions-2026-04-18`; Robert was not copied.
  - Latest decision email: subject `CRM additions: target/link decisions needed`, Message-ID `<177652842151.70937.3224022845392947786@kovaldistillery.com>`.
  - Frank corrective reports sent to Robert: task id `frank-avignon-crm-recovery-corrected-path-2026-04-19`, Message-ID `<177661098259.95485.12446032407156880410@kovaldistillery.com>`; Task Manager/worker route acknowledgement `frank-2026-avignon-crm-claude-context-route-2026-04-19`, Message-ID `<177661099509.95877.3244850234872230469@kovaldistillery.com>`.
  - Boundary: no phpList action, broad import, unrelated mailbox filing, credential/security/auth work, external-sensitive send, or destructive/bulk action was performed.

## Waiting Next Step

- Gmail push parked follow-up:
  - Monday, 2026-04-20: verify Frank/Avignon 15-second polling health before any Gmail API push/OAuth/PubSub work resumes.
  - Robert pause directive from 2026-04-18: keep Frank/Avignon email handling on the current 15-second polling path until Monday, 2026-04-20.
  - First Monday action: verify polling health from non-secret LaunchAgent/runtime metadata.
  - Resume Gmail API push/OAuth/PubSub only if still needed and only from the M4 ERTC Google auth context.
  - Before Monday approval: no Google Cloud/PubSub/IAM mutation, no OAuth token work, no mailbox content read, no runtime cadence change, and no deploy/push/live pull for the Gmail push slice.
  - Do not attempt more Google auth changes before Monday unless Robert explicitly reopens it.

- CRM recovery next action:
  - Avignon worker `b583edb6` should use the private Frank context capture at `/Users/werkstatt/ai_workspace/frank/drafts/claude-avignon-context-frank-mail-2026-04-19.private.txt` and metadata at `/Users/werkstatt/ai_workspace/frank/drafts/claude-avignon-context-frank-mail-2026-04-19.meta.json`, plus private Avignon source artifacts, without printing private bodies/contact fields.
  - If a unique safe target can be determined, route only that bounded action to Portal/Importer. If ambiguity remains, send a corrected concise Avignon email to Sonat with Robert copied for visibility; copy Claude only if Robert explicitly wants Claude in the CRM decision thread.
  - Source `7` should be handled in the final closeout only after the source `1` / source `10` recovery path is resolved or explicitly held by Robert/Task Manager.
  - Do not run phpList actions, broad imports, unrelated mailbox filing, credential work, destructive changes, or external-sensitive sends under this routine CRM authority.

## Done

- 2026-04-19: Sent Sonat the pricing unification / Portal pricing scope note.
  - Task id `ops-pricing-unification-portal-2026-04-19`; subject `Pricing unification and Portal pricing scope`; Message-ID `<177661177342.12519.5475020165538054926@kovaldistillery.com>`. No production pricing data or Portal behavior changed.

- 2026-04-18: Parked Gmail API push/OAuth/PubSub slice until Monday health check.
  - Recorded Robert's pause directive: stay on current 15-second polling until Monday, 2026-04-20; verify polling health first; resume Gmail API push/OAuth/PubSub only from the M4 ERTC Google auth context if still needed. Docs-only; no Google auth, mailbox read, runtime cadence change, Cloud/PubSub/IAM mutation, deploy, push, live pull, credential, OPS, or external-system state changed.

- 2026-04-18: Installed Avignon Gmail fast-poll runtime improvement.
  - `com.koval.avignon-auto` now polls every 15 seconds instead of 60 seconds, using the existing duplicate-protected inbox cycle. True Gmail push is still blocked on Google Cloud/PubSub/IAM plus Avignon Gmail API OAuth setup.

- 2026-04-18: Cleaned active Avignon TODO.
  - Collapsed verbose history into the current CRM recovery item plus exact waiting gates. Older Done history remains in `HANDOFF.md` and `TODO-done-archive-2026-04-18.md`. No mailbox/runtime/CRM/Portal/phpList mutation was performed.
- 2026-04-18: Mandatory Avignon completion-report correction recorded.
  - Avignon task-completion report email is required by default unless explicitly suppressed. Reports go to Sonat by default and include Robert only when task context or approval path requires it.
- 2026-04-18: Authorized Avignon chief-of-staff inbox cleanup sweep completed.
  - Final verified Avignon INBOX/unread was `0` / `0`. No follow-up email, worker routing, credential output, runtime change, CRM/Portal write, or external-system action was performed.
- 2026-04-18: Chief-of-staff email-worker directive recorded.
  - Avignon routes clear low-risk internal email tasks to visible workers, verifies start/completion, updates durable state, sends required completion reports, suppresses duplicate surfacing, files FYI/CC/no-action items, and follows 24-hour decision follow-up rules.
- 2026-04-17 and earlier: Older Avignon setup, runtime, inbox, decision-loop, CRM recovery, Google Ads routing, and historical completion entries archived out of the active TODO.
  - See `TODO-done-archive-2026-04-18.md` and `HANDOFF.md`.

## Backlog

No open items.
