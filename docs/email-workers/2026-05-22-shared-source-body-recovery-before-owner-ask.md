# Shared Source-Body Recovery Before Owner Ask

Status: active shared directive
Owner: AI Workspace Task Manager / Email Coordinator
Applies to: Frank, Avignon, National Outreach, Asher, Venetia, and approved send-from personas
Created: 2026-05-22

## Rule

Before any email worker asks an owner to resend, forward, restate, or retype an email-derived request, the worker must first re-read its own mailbox thread and try to recover the original request body from the live inbox or all-mail store using the source `Message-ID`, thread headers, or later quoted-thread copies.

Do not ask an owner to forward a message that already exists in the worker's mailbox unless the worker has verified that the body is genuinely unavailable from the approved mailbox path.

## Required Order

1. Check the live mailbox thread first.
2. Re-fetch the original message by `Message-ID` when the worker still has that reference.
3. Check later replies or forwards in the same thread for quoted original context.
4. Only if the body is still unavailable, ask for the missing business details.

## Owner-Facing Behavior

If the original body is recoverable:
- use that recovered context to continue the work or ask one concrete business question;
- do not send subject-only blockers like "I need one more piece" or "missing workflow/target details."

If the original body is not recoverable after the mailbox re-read:
- say that the worker re-checked its own mailbox/thread and only the subject or partial metadata remains;
- ask for the exact missing business action in plain English;
- do not ask the owner to hunt down internal ids or route labels.

## Bad Pattern

Avoid subject-only blockers such as:
- "Please forward the original message."
- "Please resend the email."
- "Please reply with the missing workflow/target details."

when the worker has not yet re-checked the live mailbox path.

## Good Pattern

Use wording like:
- "I re-checked my inbox thread for this request. I still only have the subject line and not the original action details. Please reply with the exact action you want handled for this item."

## Accessible Report Delivery Rule

When a worker tells an owner that a full report exists, the report must be delivered on an owner-accessible surface.

Do not send owner-facing lines such as:
- "The full report is here: `/Users/...`"
- "See my local file at `/Users/...`"

Required behavior:
1. Put the short business answer in the email body.
2. If the full report is longer, send it as an actual email attachment or publish it to an approved readable surface such as Papers.
3. Share the Papers path or Papers link in the owner-facing message, not a local machine path.

This rule applies to all email workers and approved send-from personas.

## Trace References

- Workspaceboard stale blocker cleanup on 2026-05-22:
  - `3c6c4a4e` ChiTown duplicate blocker resend
  - `04fc8021` Cultivater duplicate blocker resend
  - `617ed81b` Bottles and Cans subject-only blocker correction
