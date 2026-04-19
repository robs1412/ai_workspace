# Screenbox Workflow Recommendations

Updated: 2026-04-17 11:11 CDT

Source thread: `Screenbox workflow recommendations`

## Status

Claude's first reply conflated Screenbox with Web Serfer. Dmytro corrected the thread, and Claude sent a corrected Screenbox-specific answer. Treat the corrected reply from Claude, Message-ID `<2232d74c8a5dbf2392552ee5b80ae25c.claude@koval-distillery.com>`, as the working guidance. Treat the earlier Web Serfer/REST-slot answer as superseded.

Frank sent a Claude-only acknowledgement/follow-up on 2026-04-17:

- Task id: `frank-2026-claude-screenbox-workflow-follow-up`
- Recipient: `claude@koval-distillery.com`
- Subject: `Re: Screenbox workflow recommendations`
- Message-ID: `<177644226569.3386.11486062060410989476@kovaldistillery.com>`
- Draft: `drafts/claude-screenbox-workflow-follow-up-2026-04-17.txt`
- Sent log: `/Users/admin/.frank-launch/state/sent-log.jsonl`

## Corrected Guidance

- Screenbox is MCP-native and gives an agent an isolated virtual desktop running a real browser. It is not the Web Serfer REST-slot browser tool.
- Use Screenbox for adaptive UI acceptance testing, visual/layout review, live observable worker testing, screenshots, page maps, page reads, console logs, and action logs.
- Keep Playwright for deterministic CI regression, network/console/DOM assertions, large-scale headless runs, and committed reproducible scripts.
- Workers should create/acquire a desktop, navigate with `desktop_chrome`, inspect with `page_map` and `page_read`, use `desktop_look` before coordinate clicks, capture JPEG evidence, and save/release/destroy the desktop when done.
- Handoffs should include the tested flow, URL, desktop id, steps executed, assertions checked, result, evidence, and notes.

## Open Detail

If Claude sends back a specific Screenbox README path or MCP config file, add it here and cite it in future worker instructions.
