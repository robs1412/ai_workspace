# Workspaceboard AI Manager Terminal Selector - 2026-05-24

Robert asked for `/workspaceboard/ai-manager-phone.php` to stop presenting itself as a phone-specific page and to behave like a real terminal selector rather than blindly using whatever terminal fallback the page picked.

## Change

- Removed the visible bundle/version strip from the AI Manager page.
- Moved AI Manager build metadata into the shared menu footer as `AI Manager build`.
- Bumped AI Manager assets to JS `105` and CSS `42`.
- Added a `Target Terminal` selector in the Live Updates header.
- The selector is populated from live Workspaceboard overview sessions:
  - AI Manager Control first
  - Task Manager second
  - other live AI/workspace sessions after that
- Selecting a terminal updates:
  - the watched `/api/session-history?session_id=...` readback
  - the direct `/api/session-message` send target
  - the terminal identity line
  - the persisted browser terminal preference
- The old no-session fallback still exists only as a recovery path before live overview loads.

## CSS Refresh

Updated the AI Manager page CSS toward the newer Workspaceboard standard:

- lighter neutral page background
- white panels with 1px borders and subtle shadow
- 6px panel radius
- flat buttons and controls
- stable terminal selector styling
- removed old version-strip styles

## Files Updated

- `/Users/werkstatt/workspaceboard/ai-manager-phone.html`
- `/Users/werkstatt/workspaceboard/assets/ai-manager-phone.js`
- `/Users/werkstatt/workspaceboard/assets/ai-manager-phone.css`
- runtime copies under `/Users/admin/.workspaceboard-launch/runtime/app/`

## Verification

- `node --check /Users/werkstatt/workspaceboard/assets/ai-manager-phone.js`
- `node --check /Users/admin/.workspaceboard-launch/runtime/app/assets/ai-manager-phone.js`
- `php -l /Users/werkstatt/workspaceboard/ai-manager-phone.html`
- `php -l /Users/admin/.workspaceboard-launch/runtime/app/ai-manager-phone.html`
- Served runtime asset readback shows `ai-manager-phone.js?v=105`, `ai-manager-phone.css?v=42`, and `Target Terminal`.
