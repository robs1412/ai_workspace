# Shared Vanessa-Style Fast Path Reliability

Status: active shared mechanic
Owner: AI Workspace Task Manager / Email Coordinator
Created: 2026-06-07
Applies to: Frank, Avignon, Ezra, Naomi, Asher, Venetia, and future approved email-worker personas

## Purpose

Vanessa feels reliable because the Outreach Coordinator lane has a narrow domain, deterministic route classes, clear routine authority, and a small finish contract. Reuse that mechanic without copying Vanessa's persona, sender identity, or outreach-specific authority.

This note is docs-only. It does not approve new mailbox body reads, sends, filing, deletes, credentials, runtime changes, finance-system mutations, production mutations, or external communication.

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
- If a worker is not send-enabled or action-enabled, use the same finish contract with `drafted`, `briefed`, `routed`, or `blocked` evidence, but do not silently expand authority.

## Shared Lane Ownership Anchors

Use these as non-secret first-pass routing anchors when classifying internal scheduler-bridge, Task Flow, or direct-owner packets. They do not grant new send authority, finance-system authority, mailbox body access, or live data mutation.

- COTeam staffing, shift, schedule, team-member, tasting, or Outreach follow-through belongs to Vanessa / National Outreach unless the packet clearly names another owner.
- Finance, BID, QBO, Square, payroll, invoice, reimbursement, receipt, or financial-reporting follow-through belongs to Naomi / finance unless the packet clearly names another owner.
- If a packet mixes COTeam and finance, split it into separate visible routes or block with one exact ownership question when the work cannot be separated safely.

Trace source: Robert correction on 2026-06-25, Message-ID `<CAAtX44aMjGcFO8T2nEh5Oozx5eJxFM=P9AgtJN1NAUk7eXtUhg@mail.gmail.com>`.

## Shift-Change Continuity

Treat staffing changes as a connected operational thread, not as isolated mailbox replies.

- The newest source-backed assignment, cancellation, release, unavailability, or reschedule instruction supersedes older approvals and stale Task Flow or OPS projections.
- Keep the affected team member, the lane owner, the operational manager, and the requester informed on the same completion path. For KOVAL Tasting Room / Outreach changes, include Vanessa, Mark, and Robert by default unless the current source explicitly narrows the recipients.
- A cancellation or release is not complete merely because the person was removed. Verify the shift is visibly open or reassigned, start replacement coverage or record one exact coverage blocker, and preserve the team member's unavailability signal when the source supplies it.
- Before filing the source, read back the live OPS assignment, verify sent-recipient proof, and confirm the replacement/open-shift state. If those surfaces disagree, keep the task open.
- Do not restore a canceled assignment from an older instruction. A later reassignment requires a new source-backed confirmation from the affected team member or the current operational owner.

## Naomi Finance Variant

Naomi should use the same fast path for finance operations, with stricter finance gates:

- Complete low-risk finance operations packet -> produce finance status, missing-source list, owner/action matrix, or route visible BID/Portal/OPS/Finance Analyst worker -> proof is the saved packet, live task id, or Workspaceboard hard-start/readback.
- Finance-account setup, QuickBooks/BID/Portal/login/payroll/banking/permissions -> route through Task Manager/Workspaceboard as visible work; hidden inbox handling is not completion.
- Receipt/reimbursement/source-file metadata with complete approved facts -> route to the approved Portal/BID/Finance Analyst path; verify live readback before closing.
- Payments, bank/vendor changes, payroll, tax/accounting/legal decisions, private finance source access, external finance/vendor communication, suspicious payment mail, or live finance mutation -> block with one exact approval/security question and state what must not be changed or promised.

Naomi is not send-enabled by default; use `sent` only after a separate approved sender route exists.
