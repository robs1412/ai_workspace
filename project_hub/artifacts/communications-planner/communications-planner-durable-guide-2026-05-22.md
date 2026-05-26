# Communications Planner Durable Guide

Updated: 2026-05-22
Project: `AI-INC-20260519-COMMS-PLANNER-BUILDOUT-01`
Scope: local durable guide for the communications-planner lane; no mailbox send, Forge mutation, Google Doc write, or audience import performed in this pass.

## Purpose

Give the communications planner one readable top-level guide so a worker can route or execute weekly highlights, social posting, campaign sends, and manual Square work without re-deriving the role split from old mail threads.

## Core Decision

- Use `Marketing Manager` to own organized campaign-send planning and the durable task lane for marketing-style work.
- Use `Communications Manager` to own copy shaping, send-readiness, and approval framing.
- Use `Email Coordinator` only when sender/routing mechanics need explicit mailbox or send-from handling.
- Keep `Codex` as the owner for the PHPList weekly-highlights lane.
- Keep `Claude` as the owner for the social-posting lane.
- Keep `Mark DeSimone` as the manual owner for Square direct-send work.
- Keep `Vanessa Sterling` out of campaign ownership unless the work is truly outreach scheduling or a National Outreach coordination packet.

## What This Planner Covers

Use the communications planner when the work is one of these:

1. A recurring weekly highlights packet that should become a send-ready artifact.
2. A social-posting packet that should stay on the same cadence as weekly highlights.
3. A campaign-style distributor, magazine, media, or audience send that needs owner, copy, timing, sender, and follow-up state.
4. A manual Square direct-send row that still needs durable classification so it does not get picked up as an autonomous AI lane.

Do not use the communications planner for internal staff updates, outreach scheduling, or a one-off external reply that belongs to another worker lane.

## Role Split

### Marketing Manager

- Owns the marketing send plan.
- Turns a request into an executable campaign packet with audience, purpose, sender/tool, timing, approval state, and follow-up.
- Routes technical send mechanics into `forge` when the task becomes a structured send.

### Communications Manager

- Owns the wording pass, tone, and send-readiness.
- Produces one recommended draft path instead of a loose list of options.
- Hands the approved copy back to Marketing Manager or the sender lane.

### Email Coordinator

- Owns sender identity and routing when a packet becomes a sendable artifact.
- Does not own campaign planning or content strategy by itself.

### Internal Communicator

- Owns internal staff-facing updates only.
- Do not route external marketing or distributor sends here.

### Outreach Coordinator / Vanessa Sterling

- Owns outreach scheduling and coordination packets.
- Do not route broad audience or campaign-send mechanics here.
- If the request is effectively "email everyone" or another broad audience send, route the audience/send mechanics to the mailing-list or Forge path instead.

## Lane Map

### Weekly Highlights

- Role owner: `Codex`
- Support roles: `Communications Manager`, `Email Coordinator`
- OPS tasks: `369887` and `369888`
- Forge planner row: `88`
- Channel/source: `PHPList`
- Deliverable: short send-ready weekly highlights packet

### Social Posting

- Role owner: `Claude`
- Support roles: `Communications Manager`, `Email Coordinator`
- OPS tasks: `369889` and `369890`
- Forge planner row: `89`
- Channel/source: `Social Posting`
- Deliverable: short post-ready social packet

### Square Direct Send

- Role owner: `Mark DeSimone`
- Forge planner rows: `26` and `27`
- Channel/source: `Square Direct Send`
- Deliverable: manual send confirmation or prepared draft
- Rule: manual lane only; do not convert this into an autonomous AI-runner task without a separate approval

### Campaign Send Planning

- Role owner: `Marketing Manager`
- Support roles: `Communications Manager`, `Email Coordinator`
- Workspace home: `ws ai` for planning, `ws forge` for send mechanics
- Deliverable: marketing send plan with owner, copy state, audience, timing, sender route, and approval gate

## Execution Path

1. Confirm the request is external communications or campaign work, not internal communication or outreach scheduling.
2. Classify it into one of the planner lanes above.
3. Draft or tighten the copy through `Communications Manager` if the wording is not already approval-safe.
4. Assign the durable owner lane and cite the matching OPS/Forge record when one exists.
5. Route technical sender/list/template mechanics to `forge` when the task requires structured sending.
6. Stop for approval before any external send, bulk audience action, or production send-path change.

## Approval Gates

- External sends still require approved audience, copy, sender/tool, and timing unless an exact standing send rule already covers the packet.
- Bulk audience imports, list cleanup, unsubscribe/compliance handling, sender-domain changes, OAuth/auth work, or deliverability changes stay approval-gated.
- Media, legal, finance, HR, unusual partner commitments, or ambiguous account commitments stay approval-gated.
- This guide does not authorize a live send by itself.

## Source Packet

Use these sources first when the planner wording needs to be updated:

1. `project_hub/issues/2026-05-19-communications-planner-buildout.md`
2. `worker_roles/marketing-manager.md`
3. `worker_roles/communications-manager.md`
4. `worker_roles/internal-communicator.md`
5. `nationaloutreach/PERSONA.md`
6. `project_hub/artifacts/communications-planner/weekly-highlights-task-lane-2026-05-19.md`
7. `project_hub/artifacts/communications-planner/social-posting-task-lane-2026-05-19.md`
8. `project_hub/artifacts/communications-planner/square-manual-task-lane-2026-05-19.md`

## Current Proof

- This top-level guide now exists at `project_hub/artifacts/communications-planner/communications-planner-durable-guide-2026-05-22.md`.
- The planner no longer depends on reconstructing the lane split from the email thread alone.
- Remaining optional follow-through is mirroring equivalent wording into any live Google Doc or other external planner surface when that specific path is requested and approved.
