# Papers Dashboard Architecture Decision Record

- Date: `2026-05-16`
- Task Flow anchor: `ai-manager-architecture-hardening-2026-05-16`
- Related issue: `project_hub/issues/2026-05-16-papers-dashboard-workspaceboard-integration.md`
- Status: `approved as gate definition; implementation blocked pending named approvals`
- Security review owner: `Security Guard` for any auth, MI/Papers, MCP, runtime, or publication boundary change

## Decision

Do not treat `Papers dashboard` as a generic product/dashboard queue item.

Until the data source, auth path, allowed read scope, publication path, and owner-visible URL are explicitly approved, this work is an architecture gate only. The next safe product surface is a Workspaceboard-owned metadata-only dashboard route or snapshot, not a live Papers/MI-authenticated dashboard integration.

## Why

- Live evidence already shows the current Papers dashboard URL redirects to MI login.
- Current approved boundary is metadata-only proxy/snapshot behavior.
- No body-read scope, no runtime publication path, and no owner-visible URL contract are approved.
- Mixing dashboard UI work with auth/data-scope work hides the real blocker and produces ambiguous queue items.

## Architecture Contract

The work must now stay split into two lanes:

1. `Architecture gate lane`
   - owns source selection, auth model, allowed read scope, publication path, and approval record.
   - output is ADRs, gate records, and Security Guard review notes.
2. `Dashboard product lane`
   - may start only after the architecture gate is closed.
   - owns route implementation, presentation, tests, and publication of the approved surface.

## Approved Now

- Workspaceboard may host a source-only or local-only dashboard route that uses approved metadata-only projection data.
- Existing no-write/read-only exporter and wrapper context may be reused for planning and tests.
- Papers remains a projection target or upstream source candidate, not the direct dashboard contract.

## Not Approved Now

- Direct owner-facing use of `https://papers.koval.lan/teams/it/dashboard.html`.
- Any MI-authenticated runtime publication path.
- Any Papers body-read path.
- Any new auth/token/session handling path.
- Any `.205`, MCP runtime, LaunchAgent, or production publication change tied to this dashboard.

## Exact Approval Gates

1. `Data source gate`
   - Decision required: name the canonical payload source.
   - Allowed outcomes now: `Workspaceboard metadata snapshot`, `approved server-side metadata proxy`, or another explicitly named read-only source.
   - Approver: `Robert` plus the responsible product/implementation owner.
   - Until approved: no generic dashboard build queue, no direct Papers page coupling.
2. `Auth path gate`
   - Decision required: name the exact auth model for the chosen source.
   - Approver: `Security Guard` for any auth, token, session, MI/Papers, MCP, or runtime boundary change; `Robert` for the resulting product choice.
   - Until approved: no new login path, cookie/session reuse, token handling, proxy auth, or embedded authenticated route.
3. `Allowed read scope gate`
   - Decision required: name the exact allowed fields, collections, document IDs, and whether body content is excluded.
   - Approver: `Security Guard` plus the data owner for any non-metadata read scope.
   - Default remains metadata-only and deny-by-default.
   - Until approved: no body reads, document fetch expansion, or ambiguous collection-wide access.
4. `Publication path gate`
   - Decision required: name where the dashboard will run: source-only/local-only, installed Workspaceboard runtime, or another approved publication surface.
   - Approver: `Robert` for the publication choice; `Security Guard` for any runtime, daemon, LaunchAgent, deploy, restart, reverse-proxy, or cross-boundary publication change.
   - Until approved: no runtime install, restart, deploy, or live publication.
5. `Owner-visible URL gate`
   - Decision required: name the final human-facing URL, or state explicitly that no owner-visible URL exists yet.
   - Approver: `Robert`.
   - Until approved: do not open a generic dashboard implementation lane or report this as owner-ready.
6. `Security Guard gate`
   - Decision required: record explicit Security Guard review for any auth, Papers, MI, runtime, MCP, token, permission, or cross-boundary change in this slice.
   - Approver: `Security Guard`.
   - Until approved: the safe surface remains Workspaceboard-owned metadata-only planning, source work, and tests.

## Gate Close Packet

All six fields below must be named together before the architecture gate is considered closed:

- Canonical data source
- Exact auth path
- Allowed read scope
- Publication path
- Owner-visible URL
- Security Guard review result

## Next Safe Implementation Only After Gates Close

- Create or update a Workspaceboard dashboard route backed by approved metadata-only data.
- Publish a stable owner-visible URL for that route.
- Keep Papers/MI auth and body-read concerns outside the dashboard route unless separately approved.

## Exact Current Blocker

No approved architecture packet yet names all six required fields together: canonical data source, exact auth path, allowed read scope, publication path, owner-visible URL, and Security Guard review result.
