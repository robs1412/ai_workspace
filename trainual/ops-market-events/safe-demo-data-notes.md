# OPS Market Events Safe Demo-Data Notes

Status: planning-only draft

## Preferred Demo Approach

Use a clearly labeled demo or seeded Market Event record for the first recording. The record should look realistic enough for training but must not reveal real customer, employee, credential, calendar, financial, or private operational data.

Recommended visible labels:

- Event name: `TRAINING - Market Event Walkthrough`
- Account/location: `Training Account - Do Not Use`
- Contact: `Training Contact`
- Notes: `Demo notes for training only. Do not use as live event instructions.`
- Date: use a non-operational future date or a known training date.

## Data That Is Safe To Show

- Fake account and contact names.
- Fake event notes.
- Generic event type, market, and status values.
- Non-sensitive UI labels.
- Demo shift or staffing labels if they do not identify real people.

## Data To Avoid

- Passwords, tokens, 2FA, private keys, `.env` values, auth cookies, session IDs, API keys, or secret calendar URLs.
- Real customer contact details unless Robert has explicitly approved that exact use.
- Employee personal details, phone numbers, private email addresses, HR notes, compensation, or scheduling conflicts.
- Private internal comments, complaint history, legal/compliance notes, payment details, or vendor account instructions.
- Browser autocomplete suggestions, downloads, notifications, bookmarks, or tabs that expose private material.

## Live Data Rule

Planning default: do not mutate live data.

If a future recording needs a save action, it must use seeded/demo records or an explicitly approved live-safe workflow. The recording notes must state:

- what environment was used,
- which demo records were used,
- whether any save action occurred,
- whether cleanup was needed,
- and who approved the live or seeded operation.

## Mocked Or Seeded Flow Label

If the workflow is mocked, seeded, or stopped before saving, record that plainly in the notes and Trainual description. Suggested note:

`This walkthrough uses seeded demo data and does not create or modify live Market Event records.`

If a screen differs from production because of safe demo constraints, mention that in the notes rather than editing the video with overlays.
