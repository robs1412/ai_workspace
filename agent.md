# Agent Memory Bridge

This workspace uses `AGENTS.md` and `HANDOFF.md` as the primary startup surfaces.

Recurring AI Manager work should use durable tools, not chat history alone:

- use skills for repeatable how-to workflows
- record AI Manager prompts and durable decisions through `scripts/ai_manager_chat_entry_adapter.php`
- mirror the prompt into `ai_manager_inputs` and the daily-input trail
- write to Papers only when the item is durable institutional memory, a reusable policy, or a long-lived assessment

Recurring workflows covered by the current bridge:

- Google Drive / AI Cloud document and folder access
- Portal sample requests
- Portal account, contact, project, and activity updates
- OPS outreach events, including Darla / WineStyles style reschedules
- AI Manager prompt recording and proof

If a prompt or decision keeps reappearing, record the rule once here and route future turns through the adapter instead of rebuilding the path from scratch.

Claude's reply on the Frank lane matched the intended split:

- do the work directly for one-off, context-specific items
- turn repeated patterns into skills
- write to Papers only for durable assessments, policy, or long-lived institutional memory
- mirror AI Manager control-lane prompts through the chat-entry adapter so the recorder and daily-input trail stay in sync

My assessment: that is the right operating boundary. It keeps the fast path fast, promotes repeatable workflows into skills, and reserves Papers for durable judgment instead of every transient task.
