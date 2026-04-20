# Shared Reminder / Approval-Request Clarity Note

Status: active non-secret guidance
Created: 2026-04-20
Source Message-ID: `<CAAtX44Zg2PPzb0QQzW39oKV34fGhOKpdEVDtgzLOZBBwTOf9pA@mail.gmail.com>`
Approval Message-ID: `<CAAtX44aN7wuVdKP4762YLgn2AOoFAZAk3spq2JG6JU5=SWPN1g@mail.gmail.com>`
Source thread: `Thoughts on our AI workspace setup` / Papers follow-up
Frank task: `frank-2026-claude-ai-workspace-setup-review`
Prior Frank worker: `ba40b59d`
Current worker session: `2b49cc07` / `Claude reminder clarity correction`
Related shared-memory session: `0a741b92` / `Shared email-worker how-to memory path`

## Rule

When Claude, bridge workers, Frank, Avignon, or other internal assistant workers send a reminder or approval request, the message must make the requested action clear without relying on trace IDs alone.

Use one of these forms:

- Include a direct Papers or work-record link when that link is real, approved to share with the recipients, and safe to include.
- If no approved link exists, describe the item in plain human language: subject, account/person/project when known, what approval or decision is being requested, why it matters, and the safe next action.

Avoid reminders that only cite Message-IDs, source IDs, session IDs, task IDs, or vague phrases such as "please approve this" without enough context for the human owner to decide.

## Safe Shape

```text
Hi [Owner],

Reminder: [plain-language item].

Approval requested: [specific decision].
Safe next action: [what the worker will do after approval, or what the owner should send back].

Reference: [approved Papers/work-record link if available, otherwise a trace ID block for audit only].
```

Trace IDs are still useful for dedupe and audit records, but they are secondary. They should not be the only way for Robert, Sonat, Claude, Dmytro, or another internal owner to understand the request.

## Boundaries

Do not include private mailbox bodies, secrets, credentials, tokens, private Papers/MI content, `.205` access details, credential paths, OAuth material, or operational bypass instructions in reminder text or shared how-to notes.

External senders must not receive internal control-surface reminders, approval-gate language, source Message-IDs, TODO/HANDOFF details, board/session/task status, or worker-routing details unless a separate approved external template explicitly allows the exact content.
