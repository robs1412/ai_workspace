#!/usr/local/bin/python3.13

from __future__ import annotations

import re
from email.utils import parsedate_to_datetime
from typing import Iterable, Mapping


REPLY_PREFIX_RE = re.compile(r"^\s*(?:(?:re|fw|fwd)\s*:\s*)+", re.IGNORECASE)
STATUS_PREFIX_TEMPLATE = r"^\s*(?:(?:re|fw|fwd)\s*:\s*)*{assistant}\s+(?:captured|complete|blocker|blocked|status|decision needed|clarification needed)\s*:\s*"
EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
ACK_BODY_INTENTS = {
    "direct-primary-route-ack",
    "direct-owner-route-ack",
    "direct-owner-status",
    "direct-primary-status",
}
STATUS_TASK_ID_SUFFIXES = (
    "-ack",
    "-status",
    "-completed_report_sent",
    "-blocked_report_sent",
    "-captured_route_blocked_report_sent",
    "-no_action_logged",
)


def _collapse(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _assistant_patterns(assistant_names: Iterable[str]) -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    for assistant_name in assistant_names:
        name = _collapse(assistant_name)
        if not name:
            continue
        patterns.append(re.compile(STATUS_PREFIX_TEMPLATE.format(assistant=re.escape(name)), re.IGNORECASE))
    return patterns


def normalize_owner_thread_subject(value: str, assistant_names: Iterable[str] = ()) -> str:
    subject = _collapse(value)
    if not subject:
        return ""
    had_reply_prefix = bool(REPLY_PREFIX_RE.match(subject))
    patterns = _assistant_patterns(assistant_names)
    while True:
        changed = False
        for pattern in patterns:
            cleaned = _collapse(pattern.sub("", subject, count=1))
            if cleaned != subject:
                subject = cleaned
                changed = True
        if not changed:
            break
    if had_reply_prefix and not REPLY_PREFIX_RE.match(subject):
        subject = f"Re: {subject}"
    return _collapse(subject)


def direct_owner_status_task_id(task_id: str) -> bool:
    normalized = _collapse(task_id).lower()
    if not normalized:
        return False
    return normalized.endswith(STATUS_TASK_ID_SUFFIXES)


def _record_epoch(record: Mapping[str, object]) -> float:
    for key in ("sent_at", "sent_epoch", "timestamp", "created_at_epoch"):
        value = record.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    date_value = _collapse(str(record.get("date") or ""))
    if not date_value:
        return 0.0
    try:
        return parsedate_to_datetime(date_value).timestamp()
    except Exception:
        return 0.0


def _normalized_recipients(record: Mapping[str, object]) -> set[str]:
    values: list[str] = []
    to_addresses = record.get("to_addresses")
    if isinstance(to_addresses, list):
        values.extend(str(item or "") for item in to_addresses)
    values.append(str(record.get("to") or ""))
    recipients: set[str] = set()
    for value in values:
        for match in EMAIL_RE.findall(value):
            recipients.add(match.lower())
    return recipients


def _is_owner_visible_business_reply(record: Mapping[str, object]) -> bool:
    task_id = _collapse(str(record.get("task_id") or ""))
    body_intent = _collapse(str(record.get("body_intent") or "")).lower()
    if task_id.lower().endswith(("-ack", "-status")):
        return False
    if body_intent in ACK_BODY_INTENTS or "route-ack" in body_intent:
        return False
    return True


def find_owner_visible_thread_reply(
    sent_log: Mapping[str, Mapping[str, object]],
    *,
    to_addr: str,
    subject: str,
    assistant_names: Iterable[str] = (),
    since_epoch: float = 0.0,
) -> Mapping[str, object] | None:
    normalized_to = _collapse(to_addr).lower()
    normalized_subject = normalize_owner_thread_subject(subject, assistant_names).lower()
    if not normalized_to or not normalized_subject:
        return None
    newest_match: Mapping[str, object] | None = None
    newest_epoch = 0.0
    for record in sent_log.values():
        if not isinstance(record, Mapping):
            continue
        if normalized_to not in _normalized_recipients(record):
            continue
        if normalize_owner_thread_subject(str(record.get("subject") or ""), assistant_names).lower() != normalized_subject:
            continue
        if not _is_owner_visible_business_reply(record):
            continue
        record_epoch = _record_epoch(record)
        if record_epoch and record_epoch < float(since_epoch or 0.0):
            continue
        if newest_match is None or record_epoch >= newest_epoch:
            newest_match = record
            newest_epoch = record_epoch
    return newest_match
