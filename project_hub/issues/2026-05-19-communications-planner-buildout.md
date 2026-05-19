# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260519-COMMS-PLANNER-BUILDOUT-01`
- Date Opened: 2026-05-19
- Date Completed:
- Owner: Robert / Communications Planner
- Priority: medium
- Status: in progress

## Scope

Build out the communications planner so the current newsletter, weekly-highlights, and social-posting work has a clear role split, a durable task home, and a readable execution path.

## Decision

- Do not add a separate marketing persona right now.
- Use `Marketing Manager` as the owner for weekly highlights and campaign-style sending.
- Use `Vanessa Sterling` only when the actual send path is the National Outreach/outreach route.
- Keep `Communications Manager` focused on copy, tone, and approval shaping.
- Keep `Email Coordinator` focused on send-from and durable routing.
- Google Drive / Google Docs write is an approved operational path when the workspace already has a writable API auth path; do not treat Drive/Docs as read-only just because the export helper or a scoped token is missing. Use the same live Google API route that already supports document writes in the AI Cloud / job-description workflow, and only call it blocked if the writable auth path is genuinely absent.
- The repeating task itself belongs in OPS, but the actual planner/calendar surface should live in `forge`. `lists` remains the audience/list execution surface when mailing-list mechanics are needed, while `bid` is not the right home for this planner.

## Symptoms

- The communications planner existed as an incomplete note, not a clean operating guide.
- Weekly highlights sending did not have a clearly named owner/task lane.
- The live Google Doc write path is not currently writable from the available Docs auth scope in this session.

## Root Cause

The role split was already present in the workspace, but the planner had not been reduced to a concise operating guide with a clear owner for weekly highlights and a clean marketing/outreach separation.

## Repo Logs

### ai_workspace

- Repo Log ID:
- Commit SHA:
- Commit Date:
- Change Summary: Updated local project-hub coordination notes and prepared the communications-planner role split for weekly-highlights handling.

## Verification Notes

- `worker_roles/marketing-manager.md` already defines organized campaign sends as Marketing Manager scope.
- `nationaloutreach/PERSONA.md` already defines Vanessa Sterling as the Outreach Coordinator persona and routes marketing/campaign mechanics to Marketing Manager and Forge.
- `worker_roles/internal-communicator.md` now explicitly tracks the internal newsletter / focus-topic / CRM-update / static-information lane from the 2022 internal communication planning doc.
- The extracted internal-communicator source synthesis is recorded at `project_hub/artifacts/internal-communicator/internal-communicator-source-synthesis-2026-05-19.md`.
- The live Google Doc `AI Workers JDs Guide` was updated with an `Internal Communicator` appendix sourced from the same internal communication doc.
- The workspace Drive token path in `.private/google-oauth/frank-google-drive-token.json` can read and write the live Google Doc; the earlier `gcloud`-based auth path was the one missing the right scopes.
- The durable Google integration how-to now lives at `project_hub/artifacts/google-drive-integration/google-drive-write-path-howto-2026-05-19.md`.
- OPS task `369887` now exists for the weekly-highlights repeating lane.
- OPS task `369888` now exists for the Forge calendar surface.
- OPS task `369889` now exists for the Forge social-posting surface.
- OPS task `369890` now exists for the social-posting repeating lane.
- Forge planner row `88` now exists as `Weekly Highlights` with `Marketing Manager` ownership and a weekly cadence.
- Forge planner row `89` now exists as `Social Posting` with `Marketing Manager` ownership and a weekly cadence.
- Forge planner now exposes an explicit `Channel / Source System` field for `PHPList`, `Square Direct Send`, `Social Posting`, `Forge`, and `Other`; the board still shows channel badges for legacy readability, and the calendar now keeps a rolling six-month month picker instead of stopping at the last saved month.
- The planner calendar surface was upgraded to a week/month grid in the Forge planner UI, with title-only items in each day cell and click-to-load detail behavior.
- The Planner Entry panel now exposes a direct clickable OPS task link next to the OPS Task ID field.
- Forge planner rows `88` and `89` now carry explicit `ops_task_id` links to `369887` and `369890`, and the Forge schema gained the `ops_task_id` column so the repeating work is visible to OPS runners.
- Forge live checkout `/home/koval/public_html/forge` was fast-forwarded to `f1f4b4a`.
- Remaining follow-up is mirroring the updated planner wording into the live Google Doc once the writable Docs auth path is available in this session.
- Robert plans to start a fresh AI Manager Robert terminal from home again; this is the next session handoff point.

## Rollback Plan

- If the role split needs revision, restore the planner wording so weekly highlights, campaign sends, and outreach sends are all described from the earlier planner draft.
- If the Docs write path is later enabled, sync the live planner doc from this project note and the local role docs.

## Follow-Ups

- Tighten the communications planner wording around `weekly highlights` and `campaign sends`.
- If a dedicated marketing voice becomes necessary later, add it only after a real split in audience, tone, or approval boundary exists.
- Once a writable Docs auth path is available, mirror this decision into the live Google Doc.
- Add a durable management note for Google Drive / Docs writes so future doc work starts from the writable API path first, not from the export/read-only helper.
- Keep the live Forge planner row and OPS task ids in sync as the wording evolves.
- Keep the social-posting lane in sync with the same recurring cadence and route rules as the weekly-highlights lane.
