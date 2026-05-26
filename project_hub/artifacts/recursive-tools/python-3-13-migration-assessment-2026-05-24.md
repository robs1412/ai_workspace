# Python 3.13 Migration Assessment For Recursive Tooling And Local Automation

- Recorded: 2026-05-24 08:52 CDT
- Scope: non-secret assessment of whether to move local `python3`-driven tooling to Python 3.13, with specific focus on `ai_workspace`, `workspaceboard`, and the new recursive tooling pilot

## Executive Read

Python 3.13 should be adopted for new tooling and for the recursive-improve lane now, but it should not replace the default unversioned `python3` on this machine yet.

That is not a theoretical caution. The current local stack already has many `#!/usr/bin/env python3` entrypoints and some explicit `/usr/bin/python3` calls across `ai_workspace` and `workspaceboard`. Repointing `python3` globally would change future behavior for a broad set of automations in one move, without lane-by-lane readback.

The right order is:

1. use explicit Python 3.13 for new toolchains
2. inventory and classify existing Python entrypoints
3. migrate selected low-risk lanes intentionally
4. consider changing the machine-wide `python3` default only after the important lanes are already off the old assumption

## Current Machine Readback

- Default shell `python3` still resolves to `/usr/bin/python3`
- Current default version is `Python 3.9.6`
- Homebrew Python 3.13 is already installed and available at `/usr/local/bin/python3.13`
- There is no `/usr/local/bin/python3` symlink taking over the unversioned command in this environment

This split is currently useful:

- old automation remains stable on the interpreter it already expects
- new agent tooling can target Python 3.13 explicitly

## Why Not Relink Globally Now

### 1. The blast radius is real

`ai_workspace` and `workspaceboard` contain a meaningful number of Python entrypoints used for:

- AI Health
- Task Flow due routing
- mailbox helpers and mail-cycle work
- backup helpers
- recorder and projection utilities
- one-off reporting and export scripts

Some of these use `#!/usr/bin/env python3`; others are invoked from shell wrappers with `python3`; a few explicitly use `/usr/bin/python3`. A global relink would create a mixed state where some scripts move to 3.13 and others remain on 3.9, which is harder to reason about than the current explicit split.

### 2. We do not yet have dependency parity proof

The key question is not whether the source code parses under 3.13. It is whether:

- the runtime dependencies exist for each lane
- the libraries behave the same way
- the local auth/token/SMTP/IMAP/Google integrations still work
- machine-local venvs and runtime launch surfaces resolve the expected interpreter

Until those are checked per lane, changing the global default is a system-wide gamble.

### 3. The recursive-improve need is already solved

The immediate blocker that triggered this question was `recursive-improve`, which declares `requires-python >=3.12`. That blocker is already resolved cleanly by using an explicit Python 3.13 venv:

- sandbox root: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve`
- preferred venv: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve/.venv313`
- preferred pilot target: `/Users/werkstatt/ai_workspace/sandboxes/recursive-improve-pilot-target-313`

There is no technical need to flip the whole machine just to satisfy that tool.

## What We Verified In This Pass

### Recursive-improve on 3.13

- `python3.13` exists and reports `Python 3.13.13`
- a dedicated venv was created at `sandboxes/recursive-improve/.venv313`
- `recursive-improve` installed cleanly into that venv
- `recursive-improve init` succeeded in `sandboxes/recursive-improve-pilot-target-313`
- `recursive-improve ratchet status --config program.md --eval-dir eval` returned a clean zero-iteration object
- `recursive-improve benchmark -o eval list` returned `No benchmarks stored yet.`

### Existing automation did not move

- `python3` still resolves to `/usr/bin/python3`
- current key AI Workspace and Workspaceboard scripts still compile under the existing default interpreter:
  - `ai_workspace/scripts/ai_health_check.py`
  - `ai_workspace/scripts/task_flow_due_runner.py`
  - `workspaceboard/scripts/health/ai_health_check.py`
  - `workspaceboard/scripts/planner/task_flow_due_runner.py`

This is enough to say the explicit 3.13 path works and the default path was not disturbed.

## Recommended Migration Model

### Lane A: New tooling, effective immediately

Use Python 3.13 now for:

- `recursive-improve`
- future recursive tooling sandboxes
- new repo-local analysis helpers that are not already tied to production-facing automation

Rule:

- use explicit venv interpreter paths
- do not depend on the unversioned `python3` command

### Lane B: Existing automation, migrate intentionally

For `ai_workspace` and `workspaceboard`, migrate by lane:

1. inventory each script entrypoint
2. identify how it is invoked:
   - shebang
   - shell wrapper
   - LaunchAgent/LaunchDaemon
   - board/runtime callout
3. identify dependencies and environment assumptions
4. test under explicit 3.13
5. move only the approved/stable lane

This keeps the migration source-first and reversible.

### Lane C: Global `python3`, defer for now

Only consider relinking the unversioned `python3` command after:

- the important automation lanes have explicit 3.13 success proof
- the runtime ownership of each lane is documented
- there is no hidden dependence on the old interpreter in launch surfaces or wrappers

## Risks If We Relink Too Early

- silent runtime drift in mail/backup/health/task-flow automation
- package mismatch between old venvs and new interpreter
- partial migration where `python3` changes but explicit `/usr/bin/python3` calls do not
- harder debugging because behavior changes depend on how a given script is launched

## Practical Plan

### Today

Create one migration-inventory task:

- collect the Python entrypoints in `ai_workspace` and `workspaceboard`
- classify them by invocation method and risk
- identify which lanes should stay on the current interpreter for now and which are candidates for explicit 3.13

### Tomorrow

Create one first real migration task:

- choose one low-risk lane and move it to an explicit Python 3.13 execution path
- verify the runtime and write back exact proof or one exact blocker

The right first low-risk candidate is not the entire stack. It is a bounded helper or a non-critical analysis/reporting path.

## Bottom Line

Python 3.13 should be the forward path for new Codex tooling.

It should not become the machine-wide unversioned default until the current automation stack is migrated deliberately. The recursive-improve need is already unblocked without taking that system-wide risk.
