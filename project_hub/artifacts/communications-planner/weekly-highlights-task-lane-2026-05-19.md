# Weekly Highlights Task Lane

Updated: 2026-05-19

## Purpose

Create a durable weekly highlights lane for communications work so the team has one repeatable owner, one repeatable source packet, and one repeatable send path.

## Decision

- `Codex` owns the PHPList weekly-highlights lane.
- `Communications Manager` supplies copy/tone/editing support.
- `Email Coordinator` keeps send-from and routing aligned when the PHPList send is prepared.
- `Claude` owns the social-posting lane separately; do not collapse the two lanes into one owner.
- `Mark DeSimone` owns the manual Square lane separately; do not route Square direct-send work into the AI lanes.
- `Vanessa Sterling` is not a separate marketing persona for this lane unless the actual channel is the National Outreach/outreach route.
- The lane should live in OPS as a repeating task, not as a one-off markdown note.

## Proposed Task Shape

- OPS task: `369887` / `Communications planner: weekly highlights repeating task`
- OPS task: `369888` / `Communications planner: Forge calendar surface`
- Forge planner row: `88` / `Weekly Highlights`
- OPS task: `369889` / `Communications planner: social posting repeating task`
- OPS task: `369890` / `Communications planner: Forge social posting surface`
- Forge planner row: `89` / `Social Posting`
- Task owner: `Codex`
- Role owner: `Codex`
- Human owner / approver: `Robert Birnecker <robert@kovaldistillery.com>`
- Cadence: weekly
- Deliverable: a concise weekly highlights email draft or send-ready packet
- Proof: owner-visible Message-ID plus source readback, or one exact blocker

## Source Packet

Use these sources when drafting the weekly highlights packet:

1. `project_hub/issues/2026-05-19-communications-planner-buildout.md`
2. `worker_roles/marketing-manager.md`
3. `worker_roles/communications-manager.md`
4. `nationaloutreach/PERSONA.md`
5. `worker_roles/internal-communicator.md`
6. `project_hub/artifacts/internal-communicator/weekly-internal-recap-workflow-packet-2026-05-07.md`

## Working Rules

- Keep the lane focused on weekly highlights and PHPList send-ready work.
- Do not create a separate marketing persona unless the role boundary changes.
- Do not route the lane through Vanessa unless the channel is truly outreach scheduling or the National Outreach mailbox route.
- Keep the output short, readable, and approval-safe.
- If the source packet is not ready, record one exact blocker instead of forcing a draft.

## Mirror Later

The lane is now mirrored into the live task spine and Forge planner row. Keep the local packet as the source note, and update the live planner surface from these ids when the wording changes.

## Social Posting Companion

The social-posting lane uses the same ownership split and should be kept on the same weekly cadence unless a separate approval says otherwise.

- OPS task: `369889` / `Communications planner: Forge social posting surface`
- OPS task: `369890` / `Communications planner: social posting repeating task`
- Forge planner row: `89` / `Social Posting`
- Role owner: `Marketing Manager`
- Support roles: `Communications Manager`, `Email Coordinator`
- Use this lane for short campaign-style or highlight-adjacent social copy, not for outreach scheduling or National Outreach mailbox work.
