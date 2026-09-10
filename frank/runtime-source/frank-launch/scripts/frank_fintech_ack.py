"""Match submission receipts to locally recorded, owner-approved FMS requests."""
from __future__ import annotations

import json
import re
from email.utils import parseaddr
from pathlib import Path


def approved_submission_ack(message: dict, approval_file: Path) -> dict:
    if parseaddr(str(message.get('from', '')))[1].lower() != 'activation@fintech.com':
        return {}
    if str(message.get('subject', '')).strip().lower() != 'processing relationship request submitted':
        return {}
    body = re.sub(r'\s+', ' ', str(message.get('body', ''))).casefold()
    if 'the following request to begin processing invoice payments electronically was submitted through koval, inc.' not in body:
        return {}
    if re.search(r'\b(action required|declined|failed|unauthorized|not requested|cancelled|canceled)\b', body):
        return {}
    try:
        approvals = json.loads(approval_file.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    if not isinstance(approvals, list):
        return {}
    for entry in approvals:
        if not isinstance(entry, dict) or entry.get('lane') != 'dist' or entry.get('owner_approved') is not True:
            continue
        fields = ['customer_id', 'retailer_name', 'street', 'submitted_at_text', 'proof_ref']
        if not all(isinstance(entry.get(k), str) and entry[k].strip() for k in fields):
            continue
        if not all(re.sub(r'\s+', ' ', entry[k]).casefold() in body for k in fields[:-1]):
            continue
        return {
            'summary': f"Fintech acknowledged the approved {entry['customer_id']} connection request; retailer approval remains tracked separately.",
            'handled_reason': 'Matched approved FMS submission receipt; no new owner decision and no activation or payment inferred.',
            'verification_readback': entry['proof_ref'],
            'ops_portal_or_domain_task': entry['proof_ref'],
        }
    return {}
