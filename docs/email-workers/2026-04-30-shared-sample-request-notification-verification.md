# Shared Sample Request Notification Verification

Status: active non-secret operating note
Created: 2026-04-30
Source Message-ID: `<CAAtX44Y7LJ3nBMe=yOgpAqzY4POdZVWBuqUhgkA_eBWOPJdnaw@mail.gmail.com>`
Visible Portal route: `760e44ab` / `Portal sample request notification follow-up`

## Classification

This is a shared Frank/Avignon mechanic plus a Portal-owned runtime/process follow-up.

It is not Frank wording customization. It is not Avignon persona customization. It does not authorize mailbox runtime, OAuth/auth, credential, external-send, deploy, live-pull, or production changes by itself.

## Rule

When Frank or Avignon routes a Portal sample request creation, the worker must treat notification delivery as part of completion, not as an optional afterthought.

For regular sample requests, the Portal route must either use the normal Portal creation path that sends the regular sample-request notifications, or report that notifications were not sent and why.

For barrel sample requests, the Portal route must either use the normal Portal creation path that sends the barrel sample request notifications, or report that notifications were not sent and why.

If the worker creates a sample request through a direct DB/table path, helper, repair path, or any path outside the normal Portal controller flow, it must not close as complete until it has verified whether the relevant notification path ran. If notification sending is expected but did not run, the worker should stop with a blocker or route a Portal-owned notification-send/fix follow-up instead of implying the request is fully done.

## Completion Report Requirement

Sample-request completion reports must state:

- the Portal sample request id
- whether it was regular or barrel sample
- whether notification emails were sent
- which route/session created the request
- what was not done, including any missing sample items, shipping fields, reviewed/shipped/pickup state, external email, or notification send
- any remaining approval gate, such as approval to send a missed notification retroactively

## Lanterna Incident Reference

Portal sample request `2707` for Lanterna was created on 2026-04-30 through a Frank-routed Portal worker, but the alert emails did not go out. Frank answered Robert with that result and then routed this follow-up to Portal session `760e44ab` so the Portal side can identify the correct notification path and safest future fix.

Do not send the missed `2707` alert retroactively without explicit approval.
