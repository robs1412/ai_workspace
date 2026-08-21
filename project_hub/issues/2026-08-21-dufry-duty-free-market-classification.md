# Dufry Duty-Free Market Classification

- Master Incident ID: `AI-INC-20260821-DUFRY-DUTY-FREE-MARKET-01`
- Date Opened: 2026-08-21
- Date Completed: 2026-08-21
- Owner: Robert
- Priority: High
- Status: Completed

## Scope

Correct Dufry T5 account `70251` so shared billing-state-based sales reports classify its sales as `Duty Free` instead of Illinois, without changing its physical Illinois shipping address.

## Symptoms

The August 2026 WH Invoices Sales by Market report showed Illinois at `$6,599.64` / `5.17%`. The entire row came from Dufry T5 WH invoices `8284` (`$1,693.68`) and `8285` (`$4,905.96`).

## Root Cause

Salesreport and Portal sales reports commonly use `vtiger_accountbillads.bill_state` as the reporting market. Dufry T5 stored `Illinois` there even though account `70251` is the established Avolta/Dufry duty-free account and is explicitly exempt from Cook County and Chicago gallonage tax in DIST.

## Repo Logs

### Shared CRM data

- Repo Log ID: `DUFRY-MARKET-STATE-20260821`
- Commit SHA: Not applicable; guarded live CRM data correction only
- Commit Date: 2026-08-21
- Change Summary: Changed only Dufry T5 account `70251` billing state from `Illinois` to `Duty Free`; retained shipping state `Illinois` and all street, city, ZIP, and country values.

## Verification Notes

- Exact preflight found no open Dufry incoming orders or picklists.
- Live account readback: billing city `Chicago`, billing state `Duty Free`, billing ZIP `60666`; shipping city `Elk Grove Village`, shipping state `Illinois`, shipping ZIP `60007`.
- The live August WH market query now returns `Duty Free` at `$6,599.64` / `5.17%`.
- The Illinois billing-state filter matches zero Dufry T5 rows; the Duty Free filter matches account `70251`.
- No invoices, QBO records, shipping addresses, tax rows, email, or money movement were changed.

## Rollback Plan

Guardedly restore `vtiger_accountbillads.bill_state='Illinois'` only for account `70251` if Robert reverses the classification, then read back both billing and shipping state and rerun the exact August market query.

## Follow-Ups

None.
