# Shared Email-Worker Customization Boundary

Status: active non-secret operating note
Created: 2026-04-22
Source Message-ID: `<CAAtX44YeivxNcoG3cOeCQZ9zHC+F+t1D267geCGaJOVdevOjag@mail.gmail.com>`
Automatic-enforcement approval source: `<CAAtX44b_He9L7Y0UNdKWVernC+M+B7C3J0EvvnjBs_zfW-9Arg@mail.gmail.com>`
Visible route: `3b50c350` / `Frank direct Robert: Re: Frank captured: Fwd: Morning Summary: Wednesday, April 22`

## Rule

Frank and Avignon share mechanics, not persona. Robert approved automatic enforcement on 2026-04-22.

Shared mechanics belong in this directory or in shared AI Workspace policy: direct-owner intake, visible worker routing, source/dedupe tracking, prompt-delivery verification, completion/blocker reports, duplicate protection, handled-mail filing, inbox-zero behavior, and approval gates.

Worker customization belongs in each assistant's own workspace:

- Frank customization lives in `frank/PERSONA.md`, `frank/AGENTS.md`, `frank/WHAT_TO_DO.md`, and Frank-specific report/draft rules.
- Avignon customization lives in `avignon/PERSONA.md`, `avignon/EMAIL_PERSONA.md`, `avignon/JOB_DESCRIPTION.md`, `avignon/AGENTS.md`, and Avignon-specific report/draft rules.

## Avignon SOP Handling

Sonat's Avignon SOP/persona input is represented by the Avignon-specific files above. The private source file named in Avignon docs may be used only for verification when needed, and its body must not be pasted into shared docs, owner-facing summaries, chat, TODOs, handoffs, or git-visible broad notes.

When a shared Frank improvement is mirrored to Avignon, the implementation must be reviewed through Avignon's job/persona files before it affects Sonat-facing wording or behavior. Likewise, Avignon improvements may inform Frank mechanics, but Sonat's voice and market-specific style do not become Frank's voice.

## Automatic Enforcement

Before changing email-worker guidance, prompts, reports, or runtime source, label the change:

- `shared mechanic`: can apply to both workers after non-secret shared-doc review.
- `Frank customization`: Robert-facing only.
- `Avignon customization`: Sonat-facing only and checked against Avignon SOP/persona references.
- `runtime change`: requires the normal Code/Git plus Security Guard route when it changes installed mailbox automation, send behavior, filing behavior, LaunchAgents, credentials, OAuth/auth, or production-facing systems.

This label is not optional. If a proposed edit mixes categories, split it into separate implementation slices and use the strictest approval route for each slice. Shared mechanics may inform both workers, but they must not carry Frank's Robert-facing phrasing into Avignon or Avignon's Sonat-facing/private SOP phrasing into Frank.

Completion reports should state which category was changed so Robert and Sonat can tell whether a change is shared behavior or assistant-specific customization.
