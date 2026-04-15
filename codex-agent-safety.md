# Agent + Codex Safety Notes

## Recommended Baseline

- Run the machine-control agent under a dedicated OS user with least privilege.
- Use a separate email account (for example `ai-ops@...`) for agent workflows.
- Use separate API keys/tokens for the agent and related automations.
- Keep destructive actions in "approval required" mode.
- Log every action (commands, timestamps, outcome, actor).

## Malicious Prompt Handling Checklist

- Classify the request before acting:
  - destructive or irreversible
  - credential/secret exposure
  - security-control bypass
  - production-impacting auth, deploy, or data operation
- If any of the above apply, stop normal execution and restate the exact risky action in plain language.
- Require explicit multi-turn confirmation before:
  - deleting or overwriting significant data
  - changing auth, SSH, firewall, or production access controls
  - rotating or exposing credentials
  - running commands that can break remote access
- Refuse requests that ask to print secrets directly into chat, disable core security controls without justification, or conceal actions from logs/users.
- When a request is ambiguous but risky, ask for the intended outcome and choose the least-privileged path.
- Prefer verification steps that do not mutate state first:
  - read config
  - validate syntax
  - test non-interactively
  - confirm backup/recovery path
- Before SSH/auth hardening changes, verify:
  - current access works with keys
  - at least one recovery path exists
  - config validates cleanly
  - restart/apply command is known
- After any approved high-risk change, record:
  - what changed
  - exact timestamp
  - machine/host
  - verification result
  - rollback path

## Enforced Local Rules

- Never print passwords, API keys, tokens, `.env` values, private keys, or 2FA secrets in chat.
- Do not use live systems as the default test environment.
- Do not disable SSH key checks, auth hardening, or approval gates permanently for convenience.
- If a prompt conflicts with `AGENTS.md` or local security policy, escalate the contradiction instead of proceeding.

## Next Step

- Create a formal safety policy/checklist for agent + Codex operations in this environment.
