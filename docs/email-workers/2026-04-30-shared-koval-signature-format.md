# Shared Email-Worker Signature Format

Status: active shared mechanic
Owner: AI Workspace Task Manager / Email Coordinator
Created: 2026-04-30

## Classification

This is a shared non-secret signature-format mechanic for all approved email-worker personas. It is not a Frank voice rule, not Sonat private SOP text, not Vanessa-specific, and not a runtime/send-path change by itself.

Worker-specific wording, role title, owner audience, and approval gates stay in the worker's own persona docs. Runtime templates and send helpers require a separately approved implementation slice.

## Standard Shape

Worker emails should include a blank line after `Best,`, then the worker's first name. Use this shape before the signature block:

```text
Best,

Worker First Name
```

Examples: `Best,`, blank line, then `Vanessa`; `Best,`, blank line, then `Frank`; `Best,`, blank line, then `Avignon`; `Best,`, blank line, then `Naomi`; `Best,`, blank line, then `Ezra`; `Best,`, blank line, then `Asher`; `Best,`, blank line, then `Venetia`.

Keep the full signature block when that worker normally has one. The correction is the closing line, not removal of the full block:

```text
Best,

Worker First Name

Worker Name

Role Title
KOVAL Distillery
4241 N Ravenswood Ave
Chicago, IL 60613
312 878 7988
http://www.koval-distillery.com
X | Instagram | Facebook
```

For KOVAL workers, use the KOVAL block above. For non-KOVAL workers, use the same closing rule before that worker's configured signature block:

```text
Best,

Worker First Name

Worker Full Name

Role Title
Organization
```

In KOVAL HTML email, link the social platform names on the final line:

- X -> `http://www.x.com/kovaldistillery`
- Instagram -> `https://www.instagram.com/kovaldistillery`
- Facebook -> `https://www.facebook.com/kovaldistillery`

Do not print raw social URLs next to the labels in the email body or HTML signature. Keep the phone number, website, and social-label set on separate lines.

## Current Application

- Frank: Frank-local Robert-facing guidance should use `Best,`, a blank line, then `Frank` before the Frank signature block.
- Avignon: Avignon should use the same KOVAL signature structure while keeping Avignon's Sonat-facing persona, role title, and approval boundaries in Avignon docs.
- Vanessa: Vanessa should use `Best,`, a blank line, then `Vanessa` before the Vanessa signature block.
- Naomi and Ezra: once send-enabled, use `Best,`, a blank line, then `Naomi` or `Ezra` before the appropriate KOVAL signature block.
- Asher and Venetia: use the same closing pattern before their Cultivater signature blocks, with `Asher` or `Venetia` on its own line before the full name.

## Trace

- Source Message-ID: `<CAAtX44ZbDJrTCM2Lf3NGpQBjXdCrP2jQMtSPt+7qexp=D3aVnw@mail.gmail.com>`
- Dedupe key: `frank-direct-primary-CAAtX44ZbDJrTCM2Lf3NGpQBjXdCrP2jQMtSPt-7qexp-D3aVnw-mail-gmail-com`
- Frank local task id: `frank-shared-email-worker-signature-format-2026-04-30`
- Chat correction 2026-04-30: keep the full signature block, but always use `Best,`, a blank line, then the worker first name. This applies to all email workers, not only Vanessa.
