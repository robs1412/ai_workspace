# Dufry Duty-Free Market Classification

- Master Incident ID: `AI-INC-20260821-DUFRY-DUTY-FREE-MARKET-01`
- Date Opened: 2026-08-21
- Date Completed: Pending report-consumer update
- Owner: Robert
- Priority: High
- Status: Open

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
- Change Summary: The initial billing-state change was rolled back after downstream review showed operational consumers use that field. Billing and shipping states remain `Illinois`; dedicated `account_preferences.reporting_state` is now `Duty Free` for report-only use.

## Verification Notes

- Exact preflight found no open Dufry incoming orders or picklists.
- Corrected live account readback: billing state `Illinois`, shipping state `Illinois`, dedicated reporting state `Duty Free`.
- Downstream review found billing state feeds Portal territory routing, Illinois compliance scans, geographic permissions, and future DIST/QBO billing-address payloads, so it must remain physical-address truth.
- No invoices, QBO records, shipping addresses, tax rows, email, or money movement were changed.

## Rollback Plan

Guardedly restore `vtiger_accountbillads.bill_state='Illinois'` only for account `70251` if Robert reverses the classification, then read back both billing and shipping state and rerun the exact August market query.

## Follow-Ups

Update sales/market report consumers to read `koval_crm.vw_account_reporting_address`, which already applies the dedicated reporting-location override, while tax, compliance, fulfillment, and billing-address consumers continue using physical addresses.
