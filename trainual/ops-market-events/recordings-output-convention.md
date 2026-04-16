# OPS Market Events Recordings Output Convention

Status: planning-only draft
Canonical local output root for future approved media: `/Users/werkstatt/ai_workspace/recordings/`

## Directory Convention

Future approved outputs for this module should use:

```text
recordings/trainual/ops-market-events/YYYY-MM-DD/
```

Example:

```text
recordings/trainual/ops-market-events/2026-05-01/
```

## File Naming

Use names that make the module, take, and review state clear:

```text
ops-market-events-walkthrough-take01.mp4
ops-market-events-walkthrough-take01-notes.md
ops-market-events-walkthrough-take01-manifest.md
ops-market-events-walkthrough-approved.mp4
```

Do not use customer names, employee names, account IDs, tokens, secret calendar identifiers, or private URLs in filenames.

## Manifest Fields

Each future recording should have a small text manifest:

```markdown
# Recording: OPS Market Events Walkthrough

- Owner/workspace: ops / ai_workspace planning
- Storage class: local-artifact
- Location:
- Size:
- SHA-256:
- Created:
- Recorded by:
- Review status: draft | approved | rejected | published
- Environment: demo | staging | seeded local | live read-only | approved live demo
- Demo-data status:
- Save action performed: no | yes, approved
- Share scope: local review | Trainual | internal only | other approved scope
- Related planning pack: trainual/ops-market-events/
- Notes:
```

## Storage And Git Rule

- Keep large media files out of git.
- Commit only small text planning files or manifests when approved.
- If a video must be retained, treat it as `local-artifact` unless Robert approves another storage class.
- If a take accidentally contains private data or secrets, quarantine it, do not share it, and escalate for review without reprinting sensitive content.

## Review Status

- `draft`: raw or first-pass output for internal review only.
- `approved`: reviewed and accepted for the intended internal training use.
- `rejected`: do not publish; retain only if needed for audit or delete after approved cleanup.
- `published`: uploaded to Trainual or another approved destination after explicit approval.
