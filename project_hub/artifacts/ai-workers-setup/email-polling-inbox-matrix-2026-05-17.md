# AI Workers Setup Email Polling / Inbox Matrix

Project: `AI-INC-20260501-AI-WORKERS-SETUP-01`
Date: 2026-05-17 CDT
Scope: non-secret planning/readback only

## Purpose

Capture current mailbox polling cadence, read scope, send/follow-through authority, runtime source, and approval gates by worker.

## Matrix

| Worker / lane | Mailbox / source | Poll interval | Read scope | Current authority | Runtime / source proof | Exact gate or next action |
| --- | --- | --- | --- | --- | --- | --- |
| Frank | Frank mailbox | 15-second practical mail polling; separate Task Flow due-runner check on 60-second throttle inside Frank auto runner | Full-body worker path | Full Frank email-worker routing, review, approved send/report path, and handled filing under Frank guidance | `TODO.md`; `HANDOFF.md`; `frank/runtime-source/frank-launch/scripts/frank_auto_runner.py` | Gmail push/OAuth remains a separate approval-gated infrastructure lane. |
| Avignon | Avignon mailbox | 15-second practical mail polling | Full-body worker path | Avignon direct-owner/body review, approved completion/blocker reporting, and handled filing under Avignon SOP guidance | `TODO.md`; `HANDOFF.md`; `avignon/runtime-source/avignon-launch/scripts/avignon_inbox_cycle.py` | Gmail push/OAuth remains a separate approval-gated infrastructure lane. |
| National Outreach | `nationaloutreach@kovaldistillery.com` shared inbox | 60-second LaunchDaemon path | Full-body worker path | Intake/routing, private-state capture, route suggestion/classification, and approved queued-send capability; no automatic filing/moves | `docs/email-workers/2026-04-27-nationaloutreach-ai-worker-inbox.md`; `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist`; `scripts/nationaloutreach_mail_cycle.py` | Keep send authority on approved queued-send paths only. |
| Asher | Separate Asher mailbox | 60-second | Header metadata only | Header-only tracking only; no body reads, filing, deletes, routine actions, or send behavior | `docs/email-workers/2026-04-27-asher-venetia-setup.md` | Final persona/action policy still needed before body reads or action authority. |
| Venetia | Separate Venetia mailbox | 60-second | Header metadata only | Header-only tracking only; no body reads, filing, deletes, routine actions, or send behavior | `docs/email-workers/2026-04-27-asher-venetia-setup.md` | Final persona/action policy still needed before body reads or action authority. |
| Customer Service | `customerservice@kovaldistillery.com` local OPS event-support candidate | Unknown | Not approved | None yet; planning only | `project_hub/issues/2026-05-01-ai-workers-setup.md`; `ops/event_support/action_handler.php` | Exact blocker: authoritative FOH guide source is still unnamed. |

## Summary

- Frank and Avignon are the only current worker lanes in this setup with documented 15-second practical polling and end-to-end review/routing/reporting authority.
- National Outreach has broader shared-inbox capability than Asher/Venetia and can send only through approved queued-send paths.
- Asher and Venetia are intentionally constrained to header-only polling until policy is widened.
- Customer Service remains planning-only until the FOH answer-authority source is named and approved.

## Verification Checklist

1. Verify cadence and current-practical-path proof in `TODO.md`, `HANDOFF.md`, and worker-local handoff/runtime docs.
2. Verify National Outreach cadence/scope in:
   - `docs/email-workers/2026-04-27-nationaloutreach-ai-worker-inbox.md`
   - `tmp/nationaloutreach-launch/com.koval.nationaloutreach-auto.plist`
   - `scripts/nationaloutreach_mail_cycle.py`
3. Verify Asher/Venetia scope in `docs/email-workers/2026-04-27-asher-venetia-setup.md`.
4. Verify routed closeout state in Task Flow surfaces and packet `verification_readback`.

## Boundary

- No external email was sent.
- No mailbox bodies were printed.
- No runtime, LaunchAgent, OAuth, or production mutation was performed in this setup slice.
