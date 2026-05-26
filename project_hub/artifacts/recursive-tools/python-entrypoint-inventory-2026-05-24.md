# Python Entrypoint Inventory

- Recorded: 2026-05-24 08:55 CDT
- Scope: ai_workspace/scripts and workspaceboard/scripts

## Totals

- Total scanned script files: 53
- ai_workspace files: 37
- workspaceboard files: 16
- Python files: 37
- Shell files: 16

## Invocation Breakdown

- no-python-call: 13
- pinned-python3.13: 37
- shell-calls-python3.13: 3

## Risk Breakdown

- low: 53

## Readback

- Global python3 relink would affect every `env-python3` script and every shell wrapper that calls unversioned `python3`.
- The current highest-risk surfaces are shell wrappers that call `python3` without pinning the interpreter.
- The current medium-risk surfaces are Python entrypoints with `#!/usr/bin/env python3` and wrappers pinned to `/usr/bin/python3`.
- The lowest-risk migration pattern is a helper that can move to an explicit 3.13 venv path without changing shared wrappers first.

## High-Risk Candidates

- None found in this bounded scan.

## Medium-Risk Python Candidates

- None found in this bounded scan.

## Next Low-Risk Lane Recommendation

- No low-risk candidate was selected automatically.
