# Avignon CRM Recovery Action-Plan Review

Date: 2026-04-19
Task: `avignon-sonat-crm-intake-recovery-2026-04-17`

## Result

Safe resolution is not possible from the currently recorded context.

The Frank/Claude-side context corrected the owner/routing path and confirmed that the previous Sonat-facing decision email was a quality problem. It did not provide a unique CRM target for the remaining ambiguous records.

## Current State

- Completed: Importer completed the five importer-safe rows as Import ID `56`; no phpList or filter action.
- Completed: Portal completed source `9` as bounded account-only CRM work.
- Completed: Portal completed source `5` with bounded account/contact/activity work.
- Blocked: source `1` still has both target-account ambiguity and duplicate/existing-contact ambiguity.
- Blocked: source `10` still has distributor/account target ambiguity.
- Held: source `7` remains status/update-only and should be included in final closeout only after sources `1` and `10` are resolved or explicitly held.

## Blocker

Avignon cannot safely route further Portal/Importer mutation because sources `1` and `10` do not resolve to one unique exact/high-confidence CRM target. Proceeding would risk linking or updating the wrong CRM records.

No CRM/Portal mutation, phpList action, broad import, mailbox filing, credential access, or external-sensitive mail send should occur from this review.

## Exact Answer Format

Use this format for the next human answer request:

```text
Source 1:
- Target account to use, or "create new":
- Existing contact record to link/update, or "create new":

Source 10:
- Distributor/account to use, or "create new":

Source 7:
- Include as status/update-only in final closeout? yes/no
```

## Next Safe Action

Do not send the existing source-heavy private answer-sheet draft as-is. If Robert approves a follow-up email, send one concise Avignon note to Sonat with Robert copied for visibility, using only the exact answer format above and non-sensitive completion state. Copy Claude only if Robert explicitly asks to include Claude in the CRM decision thread.
