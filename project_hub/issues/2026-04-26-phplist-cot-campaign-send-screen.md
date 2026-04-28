# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260426-PHPLIST-COT-SEND-SCREEN-01`
- Date Opened: 2026-04-26
- Date Completed: 2026-04-26
- Owner: Codex / Robert
- Priority: High
- Status: Completed

## Scope

Restore the phpList admin send/test screen for draft campaign `552` (`COT shifts are moving to OPS`) without queueing or sending the campaign.

## Symptoms

Robert reported that `/lists/admin/?page=send&id=552` showed a white page after trying to send a test message.

## Root Cause

Campaign `552` was created directly for the COT migration draft and did not have the complete phpList send-screen metadata that normal UI-created campaigns carry. The row had a COT listmessage link, but `phplist_message.template` was `0`, `owner` was `NULL`, and `phplist_messagedata` was missing keys such as `targetlist`, `template`, `sendformat`, `textmessage`, and scheduling metadata.

After that metadata was normalized, the remaining send/test fatal was traced to the COT phpList list itself: list `73` had `owner=NULL`. phpList's mail cache path assumed a numeric list owner and generated invalid SQL while resolving list-owner attributes.

## Repo Logs

### lists

- Repo Log ID: live DB normalization only
- Commit SHA: `c9373b2` local commit; GitHub push blocked by macOS credential helper error `-25308`
- Commit Date: 2026-04-26
- Change Summary: Normalized live phpList campaign `552` metadata for list `73`, template `70`, owner `1`, HTML send format, text body, footer, target list, and draft scheduling keys. Set owner `1` on internal lists `72` and `73`. Added a defensive `sendemaillib.php` fallback for ownerless lists; deployed the one-file live patch over SSH after preserving a live backup because GitHub push was blocked.

## Verification Notes

- Verified live `phplist_message` for `552` now has `status=draft`, `template=70`, `owner=1`, `sendformat=HTML`, `userselection=NULL`, and a non-empty footer.
- Verified `phplist_messagedata` has exactly one each of `targetlist`, `template`, `sendformat`, `textmessage`, `footer`, `embargo`, `finishsending`, and `requeueuntil`.
- Verified `phplist_listmessage` still links message `552` to list `73`.
- Verified live `admin/send.php` and `admin/send_core.php` lint cleanly.
- Verified live `admin/sendemaillib.php` lint cleanly after the ownerless-list guard.
- Sent one phpList test for campaign `552` to Robert's requested address; `sendEmail()` returned success and the draft test metadata was updated.
- Verified `precacheMessage(552, 0)` returns success after the list-owner fix.
- Added Dmytro's sendable phpList subscriber to list `95` (`Management Group incl Dmytro`) and verified the list has `4` sendable joined subscribers afterward.
- Verified Workspaceboard's Lists TODO surface reports `open_count=0` and empty append queue after closeout.

## Rollback Plan

Restore campaign `552` metadata from the pre-change database state if the UI shows a new regression, or recreate the campaign through phpList UI using the same subject/body/list and abandon draft `552`. The live file backup is `admin/sendemaillib.php.bak-codex-20260426-ownerless-list`.

## Follow-Ups

- Future phpList draft creation should use phpList's own campaign creation path or populate the full send-screen metadata contract when direct DB creation is unavoidable.
