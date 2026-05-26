# Shared OPS/Portal Record Confirmation Links

Status: active non-secret operating note
Created: 2026-05-23
Source: Robert instruction in task mode

## Rule

When a worker creates or updates a live OPS or Portal record that another human needs to know about, completion must not stop at "record created."

The worker must do one of these:

- use the product's normal notification route for that record type when that route exists and is the approved normal path
- send a confirmation email through the correct email worker when no reliable built-in notification route is available or when the completion path used did not send the expected notice

## Link Requirement

Any confirmation email for an OPS or Portal record must include a live application URL to the created or updated record, or the closest truthful live page that exposes that record.

Use live host links such as `https://ops.koval-distillery.com/...` or `https://portal.koval-distillery.com/...` when available.

Do not send `/werkstatt` paths, repo-local paths, or localhost URLs as the owner-facing record link.

## Applies To

This shared mechanic covers live OPS/Portal record work such as:

- projects
- tasks
- activities
- contacts
- accounts
- sample requests

Use the narrowest truthful live link available for the specific record type.

## Known Strong Cases

- Portal sample requests: prefer the normal Portal notification path when it exists; otherwise the fallback confirmation email must include the live Portal sample-request page or record link.
- OPS tasks: if the normal task notification path is not used or is intentionally silent, the fallback confirmation email must include the live OPS task page or closest truthful task view.

## Completion Expectation

Closeout should state:

- which record was created or updated
- which notification path was used
- the live link included for owner readback
- any notification gap or remaining blocker
