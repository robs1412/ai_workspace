# Automatic terminal handoff linkage

Personal terminal launches carry WORKSPACEBOARD_SESSION_ID. Owner launchers also derive it from their exact tmux pane when an older Workspaceboard runtime does not yet supply it. This fallback makes new sessions work without a board restart. The derivation accepts only wb-personal- followed by the exact 16-character terminal ID; titles are never used.

The shared Robert adapter forwards that non-secret ID with its existing owner config and saves a private thread-to-terminal metadata map. Direct CLI launch paths carry the ID through shell_environment_policy.set. The handoff recorder fills omitted session fields from that environment or an owner-matched thread map. Explicit different session targets remain unchanged; an exact current Codex UUID is normalized when authoritative context exists. Without evidence, records remain unlinked.

Run `python3.13 scripts/install_workspaceboard_session_context.py` to install the context hooks into existing owner launchers and the optional local shared adapter. It is idempotent, validates expected source shapes before writing, and preserves unrelated launcher changes. Workspaceboard's normal installer invokes it too. The shared adapter is an existing local dependency; it is not replaced or imported wholesale into this change.

## Backfill

`php scripts/backfill_handoff_session_links.php` reads a reviewed JSON batch from stdin and previews exact links. Add `--apply` to execute. Each item requires entry_id, session_id, expected_session and evidence. A changed current value aborts the transaction. Existing correct links are skipped. Changes preserve content/state and append timestamped old/new/evidence metadata to the handoff row. No title-based or current-task-assignment guessing is permitted.

On October 23, seven source-verified entries were linked to five live Robert terminals: 5937, 5942, 5943, 5944, 5949, 5950, 5954. Two corrected Codex UUIDs mistakenly stored as terminal IDs. Other sessions without verified handoff evidence remain neutral.

## Verification

Tests cover isolated real tmux identity, all three owner launchers with/without terminal context on macOS Bash, TOML argument parsing, installer idempotence and unrecognized-source rejection, shared adapter metadata mapping, recorder precedence and owner isolation. Workspaceboard terminal tests cover launch propagation and cached handoff reads.
