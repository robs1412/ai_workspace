#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


BUNDLE_DIR = Path(__file__).resolve().parent
AI_ROOT = Path("/Users/werkstatt/ai_workspace")
DEFAULT_ALLOWLIST = BUNDLE_DIR / "chat-readback-allowlist.json"
DEFAULT_STATE = AI_ROOT / "nationaloutreach/runtime/google-chat-watch-state.json"
DEFAULT_EVENTS = AI_ROOT / "nationaloutreach/runtime/google-chat-watch-events.jsonl"
CLIENT_FILE = Path(os.environ["GOOGLE_DRIVE_CLIENT_FILE"])
TOKEN_FILE = Path(os.environ["GOOGLE_CHAT_LOCAL_TOKEN_FILE"])
CHAT_SCOPES = [
    "https://www.googleapis.com/auth/chat.messages.readonly",
    "https://www.googleapis.com/auth/chat.spaces.readonly",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Adaptive poller for approved National Outreach Google Chat targets.")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST))
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--events", default=str(DEFAULT_EVENTS))
    parser.add_argument("--target", action="append", help="Allowed label, email, or space id. Defaults to all allowed targets.")
    parser.add_argument("--idle-seconds", type=int, default=60)
    parser.add_argument("--active-seconds", type=int, default=15)
    parser.add_argument("--active-window-seconds", type=int, default=240)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--emit-existing", action="store_true", help="Emit current messages on first target seed.")
    parser.add_argument("--ignore-sender", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_json(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def load_client() -> dict:
    payload = load_json(CLIENT_FILE)
    return payload.get("installed") or payload.get("web") or payload


def credentials() -> Credentials:
    client = load_client()
    token = load_json(TOKEN_FILE)
    creds = Credentials(
        token=token.get("access_token"),
        refresh_token=token.get("refresh_token"),
        token_uri=client["token_uri"],
        client_id=client["client_id"],
        client_secret=client["client_secret"],
        scopes=CHAT_SCOPES,
    )
    creds.refresh(Request())
    return creds


def allowed_targets(allowlist: dict) -> dict[str, dict]:
    targets: dict[str, dict] = {}
    for email, item in (allowlist.get("direct_messages") or {}).items():
        label = item.get("label") or email
        record = {"kind": "direct_message", "key": email, "label": label, "space": item["space"]}
        targets[email.lower()] = record
        targets[label.lower()] = record
        targets[item["space"].lower()] = record
    for label, item in (allowlist.get("spaces") or {}).items():
        record = {"kind": "space", "key": label, "label": label, "space": item["space"]}
        targets[label.lower()] = record
        targets[item["space"].lower()] = record
    return targets


def visible_targets(targets: dict[str, dict]) -> list[dict]:
    return sorted({item["space"]: item for item in targets.values()}.values(), key=lambda item: (item["kind"], item["label"]))


def select_targets(all_targets: dict[str, dict], requested: list[str] | None) -> list[dict]:
    if not requested:
        return visible_targets(all_targets)
    selected = []
    for item in requested:
        key = item.strip().lower()
        if key not in all_targets:
            raise ValueError(f"target_not_allowed:{item}")
        selected.append(all_targets[key])
    return visible_targets({item["space"]: item for item in selected})


def request_json(creds: Credentials, path: str, params: dict[str, object] | None = None) -> dict:
    url = "https://chat.googleapis.com/v1/" + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {creds.token}"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def read_messages(creds: Credentials, target: dict, page_size: int) -> list[dict]:
    payload = request_json(
        creds,
        f"{target['space']}/messages",
        {"pageSize": max(1, min(page_size, 20)), "orderBy": "createTime desc"},
    )
    messages = []
    for message in payload.get("messages") or []:
        sender = message.get("sender") or {}
        messages.append(
            {
                "name": message.get("name", ""),
                "createTime": message.get("createTime", ""),
                "senderType": sender.get("type", ""),
                "senderName": sender.get("name", ""),
                "text": (message.get("text") or "").strip(),
            }
        )
    return messages


def should_emit(message: dict, ignore_senders: set[str]) -> bool:
    sender = str(message.get("senderName") or "")
    return sender not in ignore_senders


def poll_once(args: argparse.Namespace, creds: Credentials, targets: list[dict], state: dict) -> tuple[dict, list[dict]]:
    now = utc_now()
    now_text = iso(now)
    target_state = state.setdefault("targets", {})
    ignored = {item.strip() for item in args.ignore_sender if item.strip()}
    new_events: list[dict] = []

    for target in targets:
        messages = read_messages(creds, target, args.page_size)
        space_state = target_state.setdefault(target["space"], {})
        seen = set(space_state.get("seen_message_names") or [])
        first_seed = not seen and not space_state.get("seeded_at")
        current_names = [message["name"] for message in messages if message.get("name")]

        if first_seed and not args.emit_existing:
            space_state["seeded_at"] = now_text
            space_state["last_seen_message_name"] = current_names[0] if current_names else ""
            space_state["last_seen_create_time"] = messages[0]["createTime"] if messages else ""
            space_state["seen_message_names"] = current_names[:200]
            continue

        fresh = [message for message in reversed(messages) if message.get("name") and message["name"] not in seen]
        for message in fresh:
            seen.add(message["name"])
            if should_emit(message, ignored):
                new_events.append(
                    {
                        "detected_at": now_text,
                        "target_label": target["label"],
                        "target_kind": target["kind"],
                        "space": target["space"],
                        **message,
                    }
                )

        merged_seen = list(dict.fromkeys(current_names + list(seen)))[:500]
        space_state["seeded_at"] = space_state.get("seeded_at") or now_text
        space_state["last_poll_at"] = now_text
        space_state["last_seen_message_name"] = current_names[0] if current_names else space_state.get("last_seen_message_name", "")
        space_state["last_seen_create_time"] = messages[0]["createTime"] if messages else space_state.get("last_seen_create_time", "")
        space_state["seen_message_names"] = merged_seen

    if new_events:
        active_until = now.timestamp() + max(1, args.active_window_seconds)
        state["last_activity_at"] = now_text
        state["active_until"] = iso(datetime.fromtimestamp(active_until, tz=timezone.utc))

    state["last_poll_at"] = now_text
    active_until_text = state.get("active_until") or ""
    active = bool(active_until_text and parse_time(active_until_text) > now)
    state["mode"] = "active" if active else "idle"
    state["next_interval_seconds"] = max(1, args.active_seconds if active else args.idle_seconds)
    state["allowed_target_count"] = len(targets)
    return state, new_events


def render(state: dict, events: list[dict], as_json: bool) -> None:
    payload = {
        "ok": True,
        "mode": state.get("mode", "idle"),
        "next_interval_seconds": state.get("next_interval_seconds"),
        "event_count": len(events),
        "events": events,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(json.dumps(payload, sort_keys=True))


def main() -> int:
    args = parse_args()
    all_targets = allowed_targets(load_json(Path(args.allowlist)))
    targets = select_targets(all_targets, args.target)
    state_path = Path(args.state)
    events_path = Path(args.events)
    state = load_json(state_path, {"targets": {}})
    creds = credentials()

    while True:
        state, events = poll_once(args, creds, targets, state)
        append_jsonl(events_path, events)
        write_json(state_path, state)
        render(state, events, args.json)
        if args.once:
            return 0
        time.sleep(int(state.get("next_interval_seconds") or args.idle_seconds))


if __name__ == "__main__":
    raise SystemExit(main())
