# Order Assistance Email Worker

Status: mailbox verified; readout imports inbound mail for internal tracking only.

This workspace is for `sales@orderkoval.com`.

## How It Works

- Poller: `../scripts/order_assistance_mailbox_sync.py`
- Private runtime state: `/Users/admin/.orderassistance-launch/state`
- Customer thread UI: `https://www.koval-distillery.com/order/customer-messages.php`
- AI readout: `../scripts/order_assistance_mailbox_readout.py`

The poller reads inbound mailbox messages and imports them into the Order app thread tables. It does not delete mail and does not send replies. The AI readout helper summarizes the private mailbox log and body cache for manual review.

Attachments are stored only in the private worker state folder. The readout shows filenames and sizes by default; pass `--show-private-paths` only when a local operator needs the exact private file location.
