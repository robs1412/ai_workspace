# AI Manager Durability Assessment

Date: 2026-05-20

## Working Split

Claude's Frank-lane reply matches the working split we want:

- do one-off, context-specific work directly
- turn repeated workflows into skills
- write durable assessments, policy boundaries, and long-lived institutional memory to Papers
- mirror AI Manager control-lane prompts through the chat-entry adapter so the DB recorder and daily-input trail stay in sync

## Assessment

That split is the right operating boundary.

It keeps the fast path fast for small, unique tasks, while promoting repeated patterns into reusable skills instead of forcing the same explanation again and again. Papers should be reserved for durable judgment, policy, and institutional memory that future sessions should not have to rediscover from chat history.

The new `scripts/ai_manager_chat_entry_adapter.php` bridge is the missing transport hook for the AI Manager control lane. It should be the default capture path whenever a prompt, correction, or durable decision matters beyond the current turn.

## Practical Rule

If the item is one-off: do it.

If the item repeats: make a skill.

If the item is durable policy or assessment: write it to Papers.

If the item is an AI Manager prompt or decision that should survive: mirror it through the chat-entry adapter into `ai_manager_inputs` and the daily-input trail.
