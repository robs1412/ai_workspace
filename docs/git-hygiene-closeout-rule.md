# Git Hygiene Closeout Rule

Status: active directive, 2026-06-12.

When work changes a git-backed workspace, the expected closeout is:

1. Inspect `git status --short` for the touched repo.
2. Keep unrelated user or worker changes intact.
3. Commit only coherent, completed work groups.
4. Push committed work to origin when the repo has a remote and the branch is appropriate.
5. Record the exact blocker when work cannot be committed or pushed.

The auto runner must not hide or discard code. It may detect dirty repos, produce repo-specific closeout packets, and route work to Code/Git Manager. It must not run broad `git clean`, destructive reset, unattended stash/drop, force-push, or commit unrelated mixed changes.

For dirty repos left by workers, the safe reconciliation path is:

- run `scripts/git_hygiene_inventory.py --root /Users/werkstatt --plan`;
- inspect the relevant repo/group packet before touching files;
- run syntax/tests appropriate to the changed group;
- commit/push the selected coherent group after approval or recorded lane authority;
- leave active or unrelated groups dirty with a durable reason and owner.

Live deploy/pull is separate from commit/push. Follow each repo's live policy; `bid` and `portal` are push-only unless Robert changes that rule.
