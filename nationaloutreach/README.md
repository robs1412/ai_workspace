# National Outreach AI Worker Inbox

Status: setup verified 2026-04-27 CDT

Mailbox: `nationaloutreach@kovaldistillery.com`

This is the shared AI-worker inbox for worker-addressed mail that should not belong to Frank or Avignon directly. Email Coordinator owns intake/routing decisions. Outreach Coordinator owns tasting, scheduling, and outreach coordination work routed from this inbox.

Do not store credentials, private mailbox bodies, OAuth tokens, app passwords, private keys, or private SOP text in this folder.

## Current Send-From Identities

- Outreach Coordinator persona: Vanessa Sterling `<vanessa.sterling@kovaldistillery.com>`, sent through the approved National Outreach mailbox/runtime route.
- Shared inbox route: `nationaloutreach@kovaldistillery.com`
- Codex route: `codex@kovaldistillery.com`

Do not send as `macee.maddox@kovaldistillery.com`. Macee has left; treat that address only as inbound legacy-recipient context when reviewing old mail.

The authoritative send-from registry is `../worker_roles/send-from-personas.md`.

## Private Runtime State

Private credential and setup state are machine-local under `.private/mailboxes/nationaloutreach/`.

Non-secret verification status may be summarized here or in project-hub notes, but secret values and mailbox bodies must never be copied here.

## Report Templates

- Whole Foods OPS coverage reports: `templates/whole-foods-ops-coverage-report.md`
- Binny's OPS coverage reports: `templates/binnys-ops-coverage-report.md`

Use HTML table email for these coverage reports. Highlight unassigned, open, partially assigned, missing OPS, or missing linked-shift rows in light red: `#fce4e4`.
