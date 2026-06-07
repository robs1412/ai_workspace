# Shared Vanessa-Style Fast Path Reliability

Status: active shared mechanic
Owner: AI Workspace Task Manager / Email Coordinator
Created: 2026-06-07
Applies to: Frank, Avignon, Ezra, Asher, Venetia, and future approved email-worker personas

## Purpose

Vanessa feels reliable because the Outreach Coordinator lane has a narrow domain, deterministic route classes, clear routine authority, and a small finish contract. Reuse that mechanic without copying Vanessa's persona, sender identity, or outreach-specific authority.

This note is docs-only. It does not approve new mailbox body reads, sends, filing, deletes, credentials, runtime changes, production mutations, or external communication.

## Shared Finish Contract

Every worker packet should finish in exactly one of these states:

- `sent`: approved message sent through the correct worker path, with sent-log Message-ID or equivalent send proof.
- `archived/no-action`: source was FYI, duplicate, thank-you, already handled, or unsafe/no-action, with archive/handled proof.
- `routed`: visible Workspaceboard/Task Flow/OPS/Portal worker started, with hard-start or live record proof.
- `closed_with_proof`: the business work is already complete, with live source proof.
- `blocked`: one exact human-readable missing fact, approval, access issue, or policy gate is recorded and, where appropriate, sent to the owner.

Do not leave a packet in vague `waiting`, `working`, `review`, or `routed` state after the proof already establishes one of the five outcomes.

## Fast Classification Shape

For each worker, keep a short front-door table near the top of its local instructions:

```text
source type -> routine action if facts are complete -> proof surface -> blocker trigger
```

Use `routine-if-clear` only when a standing rule already allows the action and the required facts are present. Use `approval-required` for external-sensitive sends, finance/legal/security/auth, credentials, production impact, destructive/bulk actions, suspicious mail, unclear ownership, or any worker whose activation policy has not approved sends/filing.

## Proof Defaults

- Sends: runtime `sent-log.jsonl`, Message-ID, recipients, subject, and short body summary.
- OPS/Portal/CRM: live record id or URL plus readback of the changed field/state.
- Routed work: Workspaceboard session id/title plus prompt-delivery or hard-start proof.
- No-action/duplicate: source id plus archive/handled/no-action event proof.
- Blocker: one plain-English question naming the person/company/account/item, missing fact, and what the worker will do after the answer arrives.

## Transferable Behavior

- Decide first whether anything is needed. If not, file or close with proof instead of surfacing a decision.
- Prefer exact duplicate checks before creating new work.
- Convert clear owner-originated routine internal requests into action, route, or draft work without asking the owner to re-approve the same request.
- Keep owner-facing reports business-first; internal ids are trace references only.
- If body/source proof is missing, recover from the worker's own live source surfaces before asking the owner to resend.
- If a worker is not send-enabled or action-enabled, use the same finish contract with `drafted`, `routed`, or `blocked` evidence, but do not silently expand authority.
