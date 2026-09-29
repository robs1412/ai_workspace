# Robert OPS terminal launch identity and task names

Owner request: AI Manager input 6300. OPS Work in Terminal must launch as Robert/admin with the task name as the terminal title.

Implemented:
- OPS keeps its authenticated user-ID-1 restriction and includes the displayed task.name in the terminal URL.
- Workspaceboard helper uses the fixed robertcodex executable for native OPS task launches, both local and SSH. Task titles are bounded, control-character checked and shell quoted. Session attach and Sonat paths are unchanged.
- ai_workspace/scripts/robertcodex sets owner ID 1 / Robert and preserves supplied arguments. cli_owner_shell.sh exposes robertcodex for shells using the existing owner shim.
- Task name becomes the command-file name, terminal OSC title and first prompt line. Direct Terminal launches also set the custom title. Old links use OPS task #ID.

Verification: 26 helper tests passed, including hostile task-name quoting and terminal escape rejection; PHP, Bash and Node syntax checks passed; stubbed Codex execution verified owner ID 1, label Robert and exact task argument forwarding. localhost/ops/tasks.php returns the login redirect, so authenticated browser-to-Terminal visual verification remains pending.

OPS commit da104ed. Live OPS pull requires explicit confirmation under ops/AGENTS.md. Helper source is updated here; other client machines need the updated helper checkout before receiving title-bearing URLs. No permission grants or daemon reinstalls were attempted.

OPS 378183 vendor-payment review is separate and incomplete. Read-only QBO on September29: 34 open bills $99013.37; 11 overdue $75600.20; none due today. Vinocopia $2230.23 disputed and Chase $259.90 residual remain do-not-pay holds. Smithereen120280, Fuyuko120164 and FGMK120271/120274 balances zero. No payment or money movement. Resume the finance review after this launcher change if requested; do not close the financial task based on launcher completion.
