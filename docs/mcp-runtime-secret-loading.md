# MCP Runtime Secret Loading

Approved shape:

- Prefer Infisical for durable runtime loading.
- Use local owner-only storage only as a bridge while the Infisical contract is missing.
- Never print, email, commit, or paste `KOVAL_TOKEN`, `SCREENBOX_API_KEY`, or derived session values.

Loader:

```bash
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

An owner-only local fallback file under the workspace `.private` tree. The file
is chmod `600`, ignored by git, and should contain only:

```dotenv
KOVAL_TOKEN=
SCREENBOX_API_KEY=
```

Run a command with loaded env:

```bash
scripts/mcp_runtime_env.py exec -- env
```

Refresh:

```bash
scripts/mcp_runtime_token_refresh.py
```

The status command reports only source/key presence plus non-secret JWT expiry
metadata for `KOVAL_TOKEN`. It does not print secret values or credential
locations. `exec` refuses expired, unparseable, or near-expiry JWTs before
starting the child command. If the owner-only refresh config exists, `exec`
first attempts an automatic metadata-only refresh through the approved packet
before reporting a blocker. Papers failures therefore stop at the loader with a
clear metadata-only blocker instead of a downstream 401.

Automatic refresh is through Infisical mode. The local fallback is not a
self-renewing secret source; if Infisical is not configured, the fallback must
be paired with the owner-only refresh config or updated out-of-band with a
fresh owner-approved value before `exec` will run.
