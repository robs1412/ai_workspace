# MCP Runtime Secret Loading

Approved shape:

- Prefer Infisical for durable runtime loading.
- Use local owner-only storage only as a bridge while the Infisical contract is missing.
- Never print, email, commit, or paste `KOVAL_TOKEN`, `SCREENBOX_API_KEY`, or derived session values.

Loader:

```bash
cd /Users/werkstatt/ai_workspace
scripts/mcp_runtime_env.py status
```

Infisical mode is active when either of these is configured:

- `INFISICAL_EXPORT_COMMAND`: reviewed command that prints dotenv content to stdout.
- `INFISICAL_PROJECT_ID`, `INFISICAL_ENV`, and `INFISICAL_PATH`: used with `infisical export --format=dotenv`.

Local fallback:

```bash
cd /Users/werkstatt/ai_workspace
scripts/mcp_runtime_env.py init-local
```

This creates:

`/Users/werkstatt/ai_workspace/.private/mcp-runtime/mcp.env`

The file is chmod `600`, ignored by git, and should contain only:

```dotenv
KOVAL_TOKEN=
SCREENBOX_API_KEY=
```

Run a command with loaded env:

```bash
scripts/mcp_runtime_env.py exec -- env
```

The status command reports only source/key presence and whether `KOVAL_TOKEN` looks JWT-shaped. It does not print secret values.
