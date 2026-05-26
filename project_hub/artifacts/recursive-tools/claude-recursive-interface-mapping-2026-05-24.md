# Claude Recursive Interface Mapping

Date checked: 2026-05-24 14:09 CDT

## Source

- Mailbox: Frank
- Location: Gmail All Mail, labels `Handled` and `Important`; not currently in `INBOX`
- From: `claude@kovaldistillery.com`
- To: `frank.cannoli@kovaldistillery.com`
- Cc: `robert@kovaldistillery.com`, `dmytro.klymentiev@kovaldistillery.com`
- Subject: `Re: Recursive improvement loop comparison`
- Date: `Sun, 24 May 2026 14:02:31 -0500`
- Message-ID: `<01200656101f1aa370267e977718c3c7.claude@kovaldistillery.com>`
- In-Reply-To: `<177964923221.16079.8878460685095716018@kovaldistillery.com>`

## Useful Mapping

Claude confirmed the proposal/state-machine direction is compatible, but his side does not store proof as a dedicated proposal field today.

Relevant Claude-side structures:

- Task-flow gates are represented by task status and tag combinations, including `blocked:approval`.
- Verification evidence lives in task comments, including image verification comments authored by the system.
- Work delivery requires `worklog_guid` before delivery notification.
- Closure depends on verification evidence in task comments before task closure.
- The PM assessment loop writes acceptance criteria as a comment plus a linked Papers document, `plan_guid`; the approval email references that Papers link.

Best current proof mapping:

- Codex `execution_proof` maps closest to Claude `worklog_guid` plus the final specialist/task comment combination.
- Codex `approval_state` maps to Claude approval tag/status state plus approval email/Papers plan reference.
- Codex `verifier_result` maps to Claude task-comment evidence and verification comments.

## Requested From Claude

Ask Claude for a concrete, non-secret task-chain/comment schema that includes:

- task id and parent/child relationship fields
- status values and approval/blocker tags
- `plan_guid` / Papers plan reference field or comment shape
- `worklog_guid` shape
- final specialist comment shape
- verification comment shape
- closure condition and delivery-notification trigger
- which fields/comments are stable enough for Codex to consume as proof references

## Follow-Up Acknowledgement

Claude replied again:

- Message-ID: `<b2f371c5770442e1f75b37ccca257a2b.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 14:07:59 -0500`
- Location at check time: Frank `INBOX` plus All Mail, label `Important`

Useful content:

- Claude agrees the interface skeleton is solid as a shared contract: recommendation -> proposal -> decision -> execution -> verifier proof -> keep/revert.
- Claude specifically called out separate execution events and the allowlist-by-class / `--allow-live-mutation` gate as the right guard against unintended mutation.
- Claude also noted the remaining gap: proposal-specific mutators for truth-drift.

## Planner Schema Packet

Claude sent the concrete non-secret Planner schema:

- Message-ID: `<62e95dd42623af2de8449e4c56816ac2.claude@kovaldistillery.com>`
- Date: `Sun, 24 May 2026 14:13:14 -0500`
- Location at check time: Frank Gmail All Mail
- Local mapping note: `project_hub/artifacts/recursive-tools/claude-planner-recursive-schema-2026-05-24.md`

Useful implementation details:

- Task ids use `tasks.id`; direct chains use `parent_task_id`; separate blockers use `blocker_task_id`.
- Planner has only three base statuses: `queued`, `active`, and `done`; blocked/review states are represented by `task_tags`.
- Approval waits are represented as `status='queued'` plus tag `blocked:approval`.
- PM assessment proof anchors on `tasks.plan_guid`, a Papers UUID written by `pm-agent`.
- Execution proof anchors on `tasks.worklog_guid` plus the final specialist comment.
- Verifier proof anchors on `task_comments.author='tester-agent'` and `comment_type='verification'`; image tasks may also have `IMAGE VERIFICATION` system comments.
- Delivery proof is a secretary comment containing `Delivery notification sent`.
- `task_comments.id` is monotonically increasing and comments are permanent, so latest proof comments can be selected with `ORDER BY id DESC`.
- Do not rely on `tasks.previous_status`, `tasks.session_id`, or `tasks.context_summary`.

Updated Codex mapping:

- Codex `approval_state` -> Claude status/tag combo, especially `blocked:approval`.
- Codex `execution_proof` -> Claude `worklog_guid` plus final specialist comment.
- Codex `verifier_result` -> Claude tester verification comment.
- Codex `ratchet_result=keep` -> Claude `done` + worklog + verifier proof + delivery proof when applicable.
- Codex `ratchet_result=revert_required` -> Claude failed verifier, `error:incident`, `error:crash`, or generated incident follow-up tasks.
