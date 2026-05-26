# Repeating Access Guide

Updated: 2026-05-20

## Purpose

This guide captures repeatable operational recipes so the next session does not rediscover the same access steps for SSH, Google Drive / Docs, and sample-request work.

Use this as the first stop for:

- approved SSH to the Claude backup lane on `.205`
- Google Docs / Drive read-write work in AI Cloud
- Portal sample-request creation or notification repair
- creating a sample request "example" or request skeleton from a source packet

## Source Order

When a task repeats, check durable sources in this order:

1. `HANDOFF.md`
2. project-hub issue note for the task
3. this guide
4. the workspace-specific `HANDOFF.md` or runbook
5. the live service or DB readback

Do not re-derive a known access path from scratch if the approved route is already recorded.

## SSH Recipe: Claude Backup Lane

Approved default route:

- host: `koval.lan`
- user: `claude`
- backup path: `/home/claude/backups/codex/`
- askpass helper: `/Users/werkstatt/ai_workspace/.private/scripts/ssh_askpass_claude_koval.sh`

Use this lane for the AI box backup push and similar approved `.205` access.

Rules:

- Do not print private key material, passwords, or auth files.
- Do not treat the old `admin@192.168.55.205` failure as the default state.
- Do not invent a second SSH identity if the approved route is already recorded.

## Google Drive / Docs Recipe

Approved local OAuth path:

- client JSON: `/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json`
- token JSON: `/Users/werkstatt/ai_workspace/.private/google-oauth/frank-google-drive-token.json`
- auth shape: `google.oauth2.credentials.Credentials`
- API client: `googleapiclient.discovery.build`

Recommended pattern:

1. Load the local client JSON and token JSON.
2. Build credentials from the stored token and client metadata.
3. Refresh only if needed.
4. Use the `docs` API for document reads and writes.
5. Read back the live document after write.

Do not:

- re-derive scopes through `gcloud` when the local token path already works
- assume a missing CLI scope means the workspace has no writable Google path
- print token values or credentials

## Naomi QBO Finance Planning Recipe

Use this when the task is not just to pull Naomi reports, but to rerun the Financial Planning workbook without leaving stale past-dated forecasts in place.

Required same-session QBO export set:

1. `Profit and Loss`
2. `Balance Sheet`
3. `Accounts receivable aging summary`
4. `Accounts payable aging summary`
5. `Transaction List by Date`
6. `Deposit Detail`
7. `General Ledger`

Why this matters:

- Summary reports alone are not enough for dated planning rows like payroll, Visa, insurance, store income, and other cash-planning lines.
- Transaction-detail exports are the proof surface for replacing or clearing past-dated forecast rows.
- Store / bar / events actuals in the workbook should follow QuickBooks actuals once available, not stale separate Square assumptions.

Rule:

- future rows may remain forecast
- once a dated row's actual is available in QBO, do not leave the old forecast in place for that same already-passed period

Local references:

- workspace skill: `skills/naomi-finance-planning/SKILL.md`
- summary export helper: `.private/scripts/qbo_naomi_export_reports_tty.js`
- transaction-detail export helper: `.private/scripts/qbo_naomi_export_may_bank_transactions.js`
- planning reconciliation helper: `.private/scripts/reconcile_financial_planning_income_actuals.py`
- SMS MFA waiter: `.private/scripts/qbo_naomi_live_code_file_waiter.js`
- email MFA waiter: `.private/scripts/qbo_naomi_email_code_file_waiter.js`

MFA recovery rule:

- use the saved-state recovery script first
- keep one waiter/browser page open from challenge creation through code submission
- write Robert's matching code into that waiter's `code.txt`
- if Intuit asks for a second verification factor or SMS codes lag, switch to the email-code waiter instead of repeatedly triggering new SMS challenges

### AI Cloud Pointer-First Rule

If the user gives a Google Docs URL and the file id 404s from the approved tokens:

1. check the local Drive-for-Desktop pointer tree under `.private/drive-exports/`
2. read the `.gdoc` pointer JSON to recover the real doc id
3. export or read the document body from that recovered id
4. treat the pointer path as the current AI Cloud source of truth when it exists

This is often the right route for AI Cloud documents that are already synced locally, even when the pasted URL is not visible to the current Google identity.

## Sample Request Recipe

Use the Portal sample-request controller path, not a direct DB insert, when the goal is a real sample request.

Core rules:

- preflight for duplicates before mutation
- reuse existing accounts when there is an exact match
- create or update only the missing account/contact/request fields
- require notification proof when the request needs a mail alert
- verify by live Portal readback

For repeatable Portal work:

- regular sample requests use the normal `PUT /sample-requests` controller path
- barrel sample requests use the barrel-sample controller path and the barrel notification event
- `_require_notifications=true` should fail closed if the required mail did not send
- do not file the task as complete until the live request and notification state are both read back

### Example Shape

Use this as a working structure for new sample-request packets:

- source: who asked and where the request came from
- target: account / contact / recipient
- needed date: the exact date from the packet
- items: the exact products and quantities
- route: regular sample vs barrel sample
- proof: request id plus notification readback
- blocker: one exact missing field or access gate

## Sample Request "Example" / Request Skeleton

If the user wants a sample request example, produce a short deterministic packet:

- requester
- account
- contact
- needed date
- delivery type
- exact items
- notes / reason
- notification requirement
- duplicate check result

If one of those fields is missing, stop and name the exact blocker instead of guessing.

## Portal Entity Recipe

Use this when the task is to add or repair Portal data such as accounts, contacts, projects, or activities.

Primary references:

- OPS manual: `https://www.koval-distillery.com/ops/docs/portal_manual.php`
- Portal handoff: `portal/HANDOFF.md`
- Portal sample-request runbook: `portal/docs/sample-request-notifications-runbook.md`

Core module map from the Portal manual:

- Relationship management -> `Accounts`, `Contacts`
- Project management -> `Projects`, `Tasks`, `Kanban`, `Gantt`
- Account touchpoints -> `Activities`
- Reports -> report submission and review

Repeatable pattern:

1. Read the source packet first.
2. Search for exact duplicates before creating anything.
3. Reuse existing exact-match accounts, contacts, or projects when they already exist.
4. Create only the missing entity or linkage.
5. For activities, attach the right account and contact and set the date from the packet.
6. For projects, create the project first, then the child tasks or follow-up items.
7. Read back the live Portal record to confirm the new or repaired item is present.

Guardrails:

- do not invent a new account when an exact match already exists
- do not invent a new contact if the source packet already maps to an existing one
- do not create a duplicate project when the same work can be attached to the existing one
- keep external email separate unless the task explicitly asks for the send

### Quick Routing Cue

If the task is a Sonat/Avignon/Frank portal packet, the next question is usually one of:

- which existing account should this attach to?
- which contact name is already known?
- does this need a project, a task, or just an activity?
- is this a sample request, and if so does it need the normal notification path?

### Portal One-Page Checklist

Use this when you are about to add or repair a Portal account, contact, project, or activity.

1. Read the source packet.
2. Name the target type: account, contact, project, activity, or sample request.
3. Check duplicates first.
4. Reuse an exact match if it already exists.
5. Create only the missing entity or link.
6. For activities, attach the correct account, contact, and date.
7. For projects, create the project before child tasks.
8. If it is a sample request, use the normal Portal notification path and require proof.
9. Read back the live Portal record.
10. Write the new id and blocker, if any, into the task log or handoff.

Stop early if:

- the source packet is missing a required field
- the account or contact is ambiguous
- the task needs approval before external mail
- the live Portal readback does not match the packet

## Repeating Memory Rule

For repeating access work:

- write the approved path once in durable notes
- link back to that note from the task log
- do not leave the next session to rediscover the same route
- prefer a single approved recipe over multiple ad hoc snippets

### Repeating Reply Pattern: Vanessa / Darla

Use this same pattern for Customer Outreach and tasting reschedules:

- default the lane to `Vanessa Sterling / Outreach Coordinator`
- keep Robert in `cc` when Vanessa confirms the reschedule with Darla, unless Robert or Sonat overrides the packet
- use unassigned shifts plus `koval_tracktime.shift2user` for the assignment path
- do not use `event_booking_staff` for this lane
- include a real Vanessa signature block
- preserve thread context by quoting or summarizing the original request from Robert or Darla
- treat this as a repeatable how-to, like a sample request packet, not a one-off reply

## Current Canonical References

- AI Cloud Google Drive / Docs write how-to: `project_hub/artifacts/google-drive-integration/google-drive-write-path-howto-2026-05-19.md`
- Claude skills guide: `project_hub/artifacts/claude-skills-guide-2026-05-20.md`
- Claude skills skill: `project_hub/artifacts/claude-skills-guide-skill/SKILL.md`
- AI Manager recorder skill: `/Users/admin/.codex/skills/ai-manager-recorder/SKILL.md`
- Robert-supplied memory example doc: `https://docs.google.com/document/d/1CY7QsFYPKgM4MaXf6V7wsACcgvr4Q1WX9-G07j9G_lA/edit?tab=t.0#heading=h.o1e6u5l9f77v`
- AI Cloud pointer example: `.private/drive-exports/frank-ai-cloud-ops-coteam-2026-05-07/source/ai-cloud-ops-coteam-project.gdoc`
- AI box backup helper: `scripts/ai_box_backup.sh`
- Portal sample request notification runbook: `portal/docs/sample-request-notifications-runbook.md`
- Portal handoff: `portal/HANDOFF.md`
- Workspace handoff: `HANDOFF.md`

## What This Guide Is Not

- not a secret store
- not a replacement for the live service readback
- not a dump of token values or private paths
- not a substitute for the workspace-specific handoff when a task needs more detail
