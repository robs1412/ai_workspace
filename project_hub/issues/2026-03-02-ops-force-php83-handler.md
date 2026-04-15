# Incident / Project Slice Log

- Master Incident ID: AI-INC-20260302-OPS-PHP-HANDLER-01
- Date Opened: 2026-03-02
- Date Completed: 2026-03-02
- Owner: Codex
- Priority: P1
- Status: Completed

## Scope

Identify why OPS executes under PHP 7.4 and enforce PHP 8.3 at OPS path.

## Symptoms

- Runtime behavior inconsistent with expected PHP 8.
- 7.4-only compatibility fatals observed on OPS auth path.

## Root Cause

- Apache system default handler is `application/x-httpd-ea-php74`.
- OPS (`/home/koval/public_html/ops`) had no local AddHandler override.
- Therefore OPS inherited server default PHP 7.4 handler.

## Repo Logs

### ops

- Repo Log ID: OPS-2026-03-02-PHP83-HANDLER
- Commit SHA: 27e73cc
- Commit Date: 2026-03-02
- Change Summary:
  - Added explicit PHP 8.3 handler override in `ops/.htaccess`:
    - `AddHandler application/x-httpd-ea-php83 .php .php8 .phtml`

## Verification Notes

- Live server config references show default php handler at `/etc/apache2/conf.d/php.conf` maps `.php` to `ea-php74` unless overridden.
- OPS now has per-directory override in `.htaccess`.

## Rollback Plan

- Revert OPS `.htaccess` handler line and pull live.

## Follow-Ups

- Optionally add same explicit handler in sibling legacy apps (e.g., `login`) if they should also be pinned to PHP 8.3.
