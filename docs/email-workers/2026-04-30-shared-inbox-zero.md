# Shared Email-Worker Inbox-Zero Directive

Status: active
Owner: AI Workspace Task Manager / Email Coordinator
Recorded: 2026-04-30

All email workers and approved send-from personas must operate toward inbox zero: `0` open / `0` unread in their active inboxes.

This applies to Frank, Avignon, National Outreach, Vanessa Sterling, Naomi Stern, Ezra Katz, Asher, Venetia, Codex mail routed through National Outreach, and future email-worker personas unless Robert explicitly defines a different mailbox policy.

Inbox zero means every inbound message is classified and moved out of the active inbox once it is no longer genuinely open. Valid states are:

- no-action/FYI
- duplicate or already routed
- routed to a visible worker/task
- completed and reported when a report is required
- blocked with a concrete blocker/decision surfaced
- intentionally waiting on a named human/system dependency

Classification must be diligent enough to catch embedded instructions. Before filing a message, review the full safe thread/body context available to that worker, identify each distinct requested action, and record a real disposition for each action. Do not rely on subject lines, headers, or a quick route label when the body contains multiple asks.

Handled, no-action, duplicate, already-routed, completed, and logged messages should be filed out of the active inbox. Open inbox residue is allowed only when it is a real unprocessed item, active blocker, pending decision, or active dependency.

For any blocker or context email, send one source email at a time and include the source email in the message body so the owner has the full context. Do not let an item sit through more than one polling cycle without an action taken; each cycle must end with send, archive, route, or an explicit blocker note.

Every successful outbound email from any email worker or approved send-from persona must be present in that account's IMAP Sent folder. Local `sent-log.jsonl`, Task Flow proof, or runtime archive files are audit supplements, not substitutes for the mailbox Sent folder. Send helpers must append the exact sent RFC822 message to IMAP Sent before reporting normal success; if the Sent append fails, record an explicit send-path blocker instead of treating the send as complete.

Asher and Venetia outbound emails must keep Sonat copied by default. For those two workers, every approved outbound send must include Sonat Birnecker Hart at `sonat@kovaldistillery.com` as a Bcc recipient unless Sonat is already an explicit To/Cc/Bcc recipient on that exact message.

For National Outreach and shared-inbox persona aliases, prefer one operational archive folder for old/resolved residue rather than multiplying worker-specific handled folders. Worker routing belongs in durable logs, TODO/HANDOFF notes, and visible worker/task state; the inbox should stay clean.

For account-access, finance, legal, compliance, auth, or other sensitive operational setup, the mailbox worker should capture and route the item to Task Manager/Workspaceboard instead of completing it invisibly inside the inbox. The durable state must name the visible route or the exact blocker.

This directive does not override safety gates. Keep approval gates for external-sensitive replies, suspicious mail, finance/legal/HR/security/auth/credential/payment issues, destructive/bulk actions, production-impacting changes, unclear ownership, and private-content handling.
