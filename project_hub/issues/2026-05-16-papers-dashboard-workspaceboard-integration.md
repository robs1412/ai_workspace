# Incident / Project Slice Log

- Master Incident ID: `AI-20260516-PAPERS-DASHBOARD-WORKSPACEBOARD-INTEGRATION-01`
- Date Opened: `2026-05-16`
- Owner: `Robert`
- Priority: `High`
- Status: `Architecture gate defined; product implementation blocked pending approvals`
- Source Input UUID: `ai-manager-papers-dashboard-2026-05-16`
- Source Input ID: `1957`
- Task Flow key: `taskflow-papers-dashboard-workspaceboard-integration-2026-05-16`
- Related Task Flow anchor: `ai-manager-architecture-hardening-2026-05-16`
- Architecture ADR: `project_hub/issues/2026-05-16-papers-dashboard-architecture-decision-record.md`

## Scope

- Define the architecture gate before any dashboard product implementation proceeds.
- Integrate a Papers-related dashboard surface into Workspaceboard only after the gate is closed.
- Treat `https://papers.koval.lan/teams/it/dashboard.html` as an authenticated Papers/MI integration target, not a public scrape.
- Preserve deny-by-default behavior for live Papers access: no credentials printed, no auth bypass, no token/cache exposure, no body reads unless explicit scope/document IDs are approved.
- Reuse existing Papers read-only wrapper / bridge context where safe, but keep the live dashboard path gated until Security Guard reviews the auth/read-only/body-scope boundary.

## Owner Workspace

- Primary owner workspace: `ws workspaceboard`
- Responsible worker/persona: `Task Manager -> Workspaceboard code worker`
- Route mode: `route_or_focus_one_worker_when_safe`
- Output channel: `AI Manager page`

## Requested Deliverable

- Produce a one-page architecture decision record and exact approval gates.
- Do not open a generic dashboard build queue until data source, auth path, allowed read scope, publication path, and owner-visible URL are named.
- Treat Security Guard review as mandatory for any auth, Papers, MI, MCP, token/session, runtime, deploy, LaunchAgent, reverse-proxy, or publication boundary change.
- Prefer source-only/design + tests first if auth/runtime is gated.
- If embedding/linking the external dashboard is blocked by auth/X-Frame/security, return the exact blocker and recommended safe design:
  - authenticated link-out
  - server-side read-only summary proxy
  - dashboard index card using approved metadata only

## Finish Contract

- Proof required: current live blockers/gates, chosen design, exact files/worker session if implementation starts, and whether runtime restart/deploy is needed.
- Security Guard review is required before runtime publication or any authenticated Papers/MI access path.
- The architecture gate is not closed until the approval packet names all six fields together:
  - canonical data source
  - exact auth path
  - allowed read scope
  - publication path
  - owner-visible URL
  - Security Guard review result
- Blocker allowed: one exact blocker only.
- Next update: route confirmation, implementation file list, and verification results.

## Verification Notes

- Live probe from AI Manager returned `307` redirect to MI login for the Papers dashboard URL.
- Architecture decision recorded in `project_hub/issues/2026-05-16-papers-dashboard-architecture-decision-record.md`.
- Existing source context already includes Papers read-only wrapper and bridge/digital-office integration points:
  - `server/papers-readonly-wrapper.js`
  - `server/test/papers-readonly-wrapper.test.js`
  - `server/digital-office-index.js`
  - `server/bridge-work-record-exporter.js`
  - `server/index.js`
- Existing task-flow projection already exists and is writable for eligible records.
- No commit, push, deploy, runtime restart, credential/auth mutation, mailbox handling, or live Papers body exposure has been approved in the manager lane.
