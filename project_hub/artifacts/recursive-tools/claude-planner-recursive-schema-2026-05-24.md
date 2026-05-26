# Claude Planner Recursive Schema Mapping

Recorded: 2026-05-24 14:31 CDT

Papers: https://papers.koval.lan/1e7119d3-e2cc-4ff0-900f-d1251eaa5f0a

Proof export update Papers: https://papers.koval.lan/9b30d986-1191-4629-9d17-0c84e0ae1bea

## Source

- Mailbox: Frank Gmail All Mail
- From: `claude@kovaldistillery.com`
- To: `frank.cannoli@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`
- Subject: `Re: Recursive improvement loop comparison`
- Date: `Sun, 24 May 2026 14:13:14 -0500`
- Message-ID: `<62e95dd42623af2de8449e4c56816ac2.claude@kovaldistillery.com>`
- In-Reply-To: `<177964981391.19315.962153949238447022@kovaldistillery.com>`

## Practical Mapping

Claude's KOVAL Planner schema is compatible with the Codex recursive proposal state machine, but the proof surface is comment/Papers based rather than one dedicated proof column.

Codex should map fields this way:

- `proposal_id`: store in a stable comment or external packet reference; Claude's native task id is `tasks.id`.
- `proposal_parent`: map to `tasks.parent_task_id` for direct task chains.
- `proposal_blocker`: map to `tasks.blocker_task_id` when a separate blocking task exists.
- `approval_state`: map to `tasks.status='queued'` plus `task_tags.tag='blocked:approval'`, with the approval email/Papers plan reference as context.
- `blocked_state`: map to stable tags such as `blocked:dependency`, `blocked:error`, `blocked:escalation`, or `blocked:manual`.
- `needs_review`: map to `task_tags.tag='needs-review'`.
- `proposal_plan`: map to `tasks.plan_guid`, which is a stable Papers UUID written by `pm-agent` and not overwritten.
- `execution_proof`: map to `tasks.worklog_guid` plus the final specialist comment.
- `verifier_result`: map to `task_comments.author='tester-agent'` and `task_comments.comment_type='verification'`, or image verification comments authored by `system`.
- `owner_visible_delivery`: map to a secretary comment containing `Delivery notification sent`.
- `ratchet_keep`: map to `status='done'`, non-null `worklog_guid`, verifier evidence present, and delivery notification sent when required.
- `ratchet_revert_required`: map to failed verifier comments, `error:incident`, `error:crash`, or follow-up tasks titled `Fix: incident on task #...` / `Post-mortem: why did task # pass verification?`.

## Stable References

Claude identified these fields as stable enough for Codex proof references:

- `tasks.id`
- `tasks.status`
- `tasks.parent_task_id`
- `tasks.blocker_task_id`
- `tasks.plan_guid`
- `tasks.worklog_guid`
- `tasks.flow_id`
- `tasks.requester`
- `tasks.assignee`
- `tasks.completed_at`
- `tasks.approved_at`
- `tasks.assessed_at`

Stable tags:

- `blocked:approval`
- `needs-review`
- `needs:dispatch`
- `blocked:dependency`
- `blocked:error`
- `error:incident`
- `error:crash`

Stable comment patterns:

- secretary source comment starts with `Source: Email from`
- secretary approval request contains `Approval request sent`
- PM assessment contains `## PM Assessment`
- tester verification uses `author=tester-agent`, `comment_type=verification`
- delivery confirmation contains `Delivery notification sent`
- incident follow-up uses `author=secretary`, `comment_type=incident_followup`

Stable routing prefixes:

- `task-simple`, `task-moderate`, `task-complex`
- `code-bugfix`, `code-feature`
- `server-fix`
- `website-change`
- `social-content-facebook`, `social-content-instagram-photo`, `product-image`
- `research-deep`

## Do Not Rely On

Claude explicitly flagged these as unstable:

- `tasks.previous_status`
- `tasks.session_id`
- `tasks.context_summary`

## Closure Logic

Claude's closure state is:

- `tasks.status='done'`
- `tasks.completed_at` set
- delivery notification sent only when:
  - the assignee is not `pm-agent` or `secretary`
  - at least one task comment contains an email-origin `[ref:N]`
  - `worklog_guid` is not null
  - no previous delivery-notification comment exists

## Codex Use

Use this mapping for future Claude/Codex recursive bridge checks:

1. Treat `plan_guid` as the safest cross-system proposal/assessment anchor.
2. Treat `worklog_guid` plus final specialist comment as execution proof.
3. Treat tester verification comments as verifier proof.
4. Treat delivery-notification comments as owner-visible completion proof.
5. Treat incident/crash/error tags as `revert_required` or repair-follow-up triggers.
6. Never use Claude `session_id`, `previous_status`, or `context_summary` as durable proof.

## Open Follow-Up

Ask Claude whether he can add or expose a non-secret read-only export keyed by `tasks.id` or `plan_guid` that returns only stable fields, stable tags, and proof comments. That would let Codex assert cross-system recursive proof without querying broad Planner state or relying on private operational fields.

## Read-Only Export Follow-Up

Claude replied with the current and planned Planner export shape.

First follow-up:

- Date: `Sun, 24 May 2026 14:37:11 -0500`
- Message-ID: `<533fe40a6a4bed94322d08f301ef647c.claude@kovaldistillery.com>`

Current export surface:

- Base URL: `https://planner.koval.lan`
- `GET /api/tasks/{id}`
  - currently returns task stable basics, including `id`, `title`, `status`, `assignee`, `priority`, `project_slug`, and `tags[]`
- `GET /api/tasks/{id}/chain`
  - returns task basics plus `comments[]` ordered by `created_at ASC`
  - comments include `id`, `author`, `content`, `comment_type`, and `created_at`
- `GET /api/tasks/search?q=&limit=`
- `GET /api/tasks?status=&assignee=&project=&limit=&offset=`
- `POST /mcp/` with tools `planner_get_task`, `planner_list_tasks`, `planner_get_chain`, and `planner_search`

Current caveats:

- Existing reads are keyed by `tasks.id`, not `plan_guid`.
- Existing reads are not proof-filtered.
- Existing reads may include volatile fields, so Codex must not treat `previous_status`, `session_id`, or `context_summary` as proof anchors.
- Live probe from this workstation on 2026-05-24 timed out for both `GET /api/tasks/1725` and `GET /api/tasks/1725/chain`; treat that as a local connectivity/readback blocker, not as proof that the endpoint does not exist.

Planned proof endpoint:

- Claude created Planner task `#1725`.
- Target routes:
  - `GET /api/tasks/{id}/proof`
  - `GET /api/proof?plan_guid={guid}`
- Target response: stable fields only plus proof comments.
- Explicit omissions: `previous_status`, `session_id`, `context_summary`.

Second follow-up:

- Date: `Sun, 24 May 2026 14:41:57 -0500`
- Message-ID: `<3a64693314bf9406f597391c35582baf.claude@kovaldistillery.com>`

Availability map:

- Available now through `GET /api/tasks/{id}`:
  - task by `tasks.id`
  - stable tags
  - parent/blocker linkage
- Planned in `/proof`:
  - task lookup by `plan_guid`
  - verification comments only
  - delivery-notification comments only
  - `worklog_guid`
- There is no `include=` parameter; `/proof` is intended to be the single clean proof shape.
- Task `#1725` is active with `developer-agent`, and Claude added the Codex constraint list to that task.

Codex operating rule until `/proof` is available:

1. Use `/api/tasks/{id}` or `/api/tasks/{id}/chain` only for exploratory/read-only context.
2. Treat volatile fields as non-proof.
3. Do not claim cross-system recursive proof from Planner until the `/proof` endpoint exists and can be read back.
4. Once `/proof` is available, add a Codex-side verifier keyed by either `tasks.id` or `plan_guid`.

## Codex Verifier Wired

Timestamp: 2026-05-24 15:25 CDT.

The Codex-side verifier requested in the follow-up is now wired:

- standalone verifier: `scripts/claude_planner_proof_check.py`
- AI Health integration: `scripts/ai_health_check.py`
- latest local verifier note: `project_hub/artifacts/recursive-tools/claude-planner-proof-verifier-wired-2026-05-24.md`
- Papers: `https://papers.koval.lan/542f8733-3aef-4cde-ad65-0da61d6b9781`
- default proof URL: `https://planner.koval.lan/api/tasks/1725/proof`
- optional plan-guid URL: `https://planner.koval.lan/api/proof?plan_guid={guid}`

Current readback:

- compile check passed for the verifier and AI Health.
- direct proof check returned `status=not-ready`, `http_status=0`, and reason `<urlopen error timed out>`.
- AI Health dry-run now emits `claude_planner_proof=not-ready`, `claude_planner_proof_forbidden_fields=0`, and includes `Claude Planner proof not-ready` in the canonical status.

Interpretation: the checker is active and durable, but Planner `/proof` is not yet proven reachable from this workstation. Continue to treat `/api/tasks/{id}` and `/chain` as context-only until `/proof` passes.
