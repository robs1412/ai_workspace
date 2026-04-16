# OPS Market Events Recording Checklist

Status: planning-only draft
This checklist is for a future approved recording session. It does not authorize recording now.

## Approval Gate

- Robert approved this specific Market Events recording session.
- The recording target and audience are clear.
- Publishing destination is known, or the output is explicitly local review-only.
- The operator understands that credentials, 2FA, secrets, admin screens, private mailbox content, and live personal data must not appear.

## Preflight

- Use the approved Trainual recording standard from `AGENTS.md`.
- Confirm the screen size, browser profile, and pointer/click feedback.
- Start after login; do not record login, password entry, token use, or 2FA.
- Confirm the OPS environment: demo, staging, seeded local, or live read-only.
- Confirm demo event names and dates are clearly fake or approved for training.
- Confirm no private account/contact details are visible in list rows, notes, tooltips, browser autocomplete, downloads, notifications, or desktop background.
- Disable unrelated notifications before recording.
- Close tabs that could expose email, credentials, calendars, customer data, or internal admin pages.
- Prepare a short recording note file before starting.

## During Recording

- Move at a manual user pace.
- Keep pointer movement visible.
- Pause briefly after navigation, page loads, and opened records.
- Do not use overlays, callout boxes, generated captions, or decorative annotations unless separately approved.
- Avoid saving live records. If a save is part of an approved demo, use seeded/demo records only and state that in the notes.
- Do not open browser password managers, developer tools, environment files, logs, private notes, or admin-only settings.
- If private data appears, stop the take and discard or quarantine the recording for review.

## Post-Recording

- Save the output under the convention in `recordings-output-convention.md`.
- Create a text manifest with environment, demo-data status, recording date, operator, and share scope.
- Review the full video before sharing.
- Confirm that no secrets, 2FA, credentials, private data, unrelated tabs, or personal notifications appear.
- Confirm that all mocked or seeded flows are labeled as such.
- Do not publish externally until Robert approves the reviewed output.

## Stop Conditions

- Credential or 2FA screen appears.
- Secret calendar URL, token, password manager, `.env`, private key, or mailbox credential appears.
- Real personal/customer/contact data appears beyond what was explicitly approved for training.
- The workflow requires live mutation that was not approved.
- The operator is unsure whether a screen is safe to show.
