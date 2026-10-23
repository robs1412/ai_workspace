#!/usr/local/bin/python3.13
"""Add non-secret terminal context to existing owner launchers without replacing them."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent

def patch_shared(source):
    if "workspaceboard_session_context.cjs" in source:
        return source
    anchor = "const OWNER = {"
    if source.count(anchor) != 1 or source.count("'shell_environment_policy.set': OWNER,") != 1:
        raise RuntimeError("Unrecognized shared launcher; no changes applied")
    source = source.replace(anchor, "const wbContext = require('./workspaceboard_session_context.cjs');\n" + anchor, 1)
    source = source.replace("'shell_environment_policy.set': OWNER,", "'shell_environment_policy.set': wbContext.environment(OWNER),", 1)
    anchor = "if (/^[0-9a-f-]{36}$/.test(id || '')) lastThreadId = id;"
    if source.count(anchor) != 1:
        raise RuntimeError("Unrecognized shared thread response; no changes applied")
    return source.replace(anchor, "if (/^[0-9a-f-]{36}$/.test(id || '')) { lastThreadId = id; wbContext.recordThread(id); }", 1)

def patch_shell(source):
    if 'source /Users/werkstatt/ai_workspace/scripts/workspaceboard_session_context.sh' not in source:
        anchor = 'cd /Users/werkstatt/ai_workspace'
        if source.count(anchor) != 1:
            raise RuntimeError('Unrecognized owner workspace; no changes applied')
        source = source.replace(anchor, anchor + '\nsource /Users/werkstatt/ai_workspace/scripts/workspaceboard_session_context.sh', 1)
    if 'WB_HANDOFF_CONTEXT_ARGS' in source:
        # Repair the earlier local draft too; Bash 3.2 rejects empty arrays
        # under nounset, and Codex requires a quoted TOML string value.
        lines = source.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.lstrip().startswith('WB_HANDOFF_CONTEXT_ARGS=(-c '):
                lines[i] = '''  WB_HANDOFF_CONTEXT_ARGS=(-c "shell_environment_policy.set.WORKSPACEBOARD_SESSION_ID='${WORKSPACEBOARD_SESSION_ID}'")\n'''
        return ''.join(lines).replace(' "${WB_HANDOFF_CONTEXT_ARGS[@]}" ', ' ${WB_HANDOFF_CONTEXT_ARGS[@]+"${WB_HANDOFF_CONTEXT_ARGS[@]}"} ')
    anchor = 'exec /usr/local/bin/codex -C /Users/werkstatt/ai_workspace '
    if source.count(anchor) != 1:
        raise RuntimeError('Unrecognized owner launcher; no changes applied')
    # This is only used on the existing direct CLI branch. Shared Robert keeps its adapter.
    setup = """WB_HANDOFF_CONTEXT_ARGS=()
if [[ "${WORKSPACEBOARD_SESSION_ID:-}" =~ ^[a-f0-9]{8}([a-f0-9]{8})?$ ]]; then
  WB_HANDOFF_CONTEXT_ARGS=(-c "shell_environment_policy.set.WORKSPACEBOARD_SESSION_ID='${WORKSPACEBOARD_SESSION_ID}'")
fi

"""
    return source.replace(anchor, setup + anchor + '${WB_HANDOFF_CONTEXT_ARGS[@]+"${WB_HANDOFF_CONTEXT_ARGS[@]}"} ', 1)

def main():
    # Build every result before writing any file; preserve all unrelated content.
    changes = []
    for name in ['robertcodex', 'sonatcodex', 'dmytrocodex']:
        p = ROOT / name; source = p.read_text(); changes.append((p, source, patch_shell(source)))
    shared = ROOT / 'robertcodex_shared.cjs'
    if shared.exists():
        source = shared.read_text(); changes.append((shared, source, patch_shared(source)))
    updated = []
    for p, old, new in changes:
        if old != new:
            p.write_text(new); updated.append(p.name)
    print(json.dumps({'ok': True, 'updated': updated}))
if __name__ == '__main__':
    main()
