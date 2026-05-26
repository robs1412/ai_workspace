# Python 3.13 Entrypoint Inventory Update

- Recorded: 2026-05-24 14:27 CDT
- OPS task: 370198
- Scope: `/Users/werkstatt/ai_workspace` and `/Users/werkstatt/workspaceboard`
- Exclusions: `.git`, `node_modules`, `.venv*`, `sandboxes`, `.private`, `__pycache__`

## Summary

The current safe position is still explicit Python 3.13 by lane, not a global unversioned `python3` relink.

Readback from the corrected bounded scan:

- Total relevant Python/shell/plist entrypoints scanned: 114
- Low risk: 57
- Medium risk: 57
- High risk: 0 found in this bounded scan

Invocation breakdown:

- `py-shebang-3.13`: 45
- `py-env-python3`: 26
- `wrapper-pinned-3.13`: 4
- `wrapper-pinned-system-python3`: 2
- `wrapper-unversioned-python3`: 3
- `no-python-call`: 34

## Current Migration State

Already on explicit Python 3.13:

- AI Health scripts
- Task Flow due runner scripts
- National Outreach mail cycle
- AI box backup wrapper
- Several email trace, Gmail export, and reporting helpers

Still medium risk and not automatically migrated:

- Frank and Avignon runtime-source scripts with `#!/usr/bin/env python3`
- Frank daily/completion helper scripts with `#!/usr/bin/env python3`
- Google Drive metadata bundle helper scripts using unversioned `python3`
- temporary legal/Jacob packet scripts using `#!/usr/bin/env python3`
- temporary Frank/Avignon registration plist copies still pinned to `/usr/bin/python3`
- temporary SSH `.205` config summary helper using unversioned `python3`

## Decision

Do not change the machine-wide `python3` default now.

Use `/usr/local/bin/python3.13` explicitly for new or already-verified lanes. Migrate the remaining medium-risk lanes only after each lane has:

- launch surface identified
- dependencies checked under 3.13
- compile/runtime smoke test completed
- rollback path documented

## Next Candidate

The next low-risk migration slice is not a live mailbox worker. Prefer a bounded helper/reporting lane first, such as a Google Drive metadata helper or temporary report script, then move toward Frank/Avignon runtime-source scripts after dependency parity is proven.
