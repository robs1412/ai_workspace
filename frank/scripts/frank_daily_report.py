#!/usr/bin/env python3
"""Render dry-run Frank morning and end-of-day report drafts.

This helper reads approved local Frank notes only. It does not send email,
connect to mailboxes, change LaunchAgents, file mail, or read credentials.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_TO = "robert@kovaldistillery.com"
REPORT_PREFIX = "Frank"
ACTIVE_SECTIONS = {"In Progress", "Waiting for Next Step", "Backlog"}
DONE_SECTION = "Done"
STALE_DONE_RE = re.compile(
    r"\b(done|completed|closed|filed|sent|verified|no longer tracks|superseded)\b",
    re.IGNORECASE,
)
USEFUL_WORK_RE = re.compile(
    r"\b("
    r"monitor|check|review|audit|finish|define|approve|create|draft|add|"
    r"expand|introduce|route|reconcile|implement|build|document|transfer"
    r")\b",
    re.IGNORECASE,
)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
PAPERS_HOST_RE = re.compile(r"^https?://papers\.koval(?:\.lan)?/", re.IGNORECASE)


@dataclass
class TodoItem:
    section: str
    text: str
    details: list[str]
    line: int
    score: int


@dataclass
class DoneItem:
    text: str
    details: list[str]
    line: int


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def slugify(value: str, limit: int = 72) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    slug = re.sub(r"-{2,}", "-", slug)
    return (slug or "frank-report")[:limit]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_markdown_sections(text: str) -> dict[str, list[tuple[int, str]]]:
    sections: dict[str, list[tuple[int, str]]] = {}
    current = ""
    for idx, line in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append((idx, line))
    return sections


def parse_bullet_items(lines: list[tuple[int, str]]) -> list[tuple[int, str, list[str]]]:
    items: list[tuple[int, str, list[str]]] = []
    current: tuple[int, str, list[str]] | None = None
    for line_no, raw in lines:
        if raw.startswith("- "):
            if current:
                items.append(current)
            current = (line_no, raw[2:].strip(), [])
        elif current and (raw.startswith("  - ") or raw.startswith("    - ")):
            current[2].append(raw.strip()[2:].strip() if raw.strip().startswith("- ") else raw.strip())
        elif current and raw.strip():
            current[2].append(raw.strip())
    if current:
        items.append(current)
    return items


def score_active_item(section: str, text: str, details: list[str], target: date) -> int:
    combined = " ".join([text] + details)
    if not text or text.startswith("_"):
        return -100
    if STALE_DONE_RE.search(text):
        return -80

    score = 0
    if section == "In Progress":
        score += 70
    elif section == "Waiting for Next Step":
        score += 60
    elif section == "Backlog":
        score += 25

    if re.search(r"\b(blocker|decision needed|approval gate|due)\b", combined, re.IGNORECASE):
        score += 18
    if re.search(r"\bOPS/Portal task ID|Local Frank task id|Source:", combined):
        score += 12
    if USEFUL_WORK_RE.search(combined):
        score += 10

    for match in DATE_RE.findall(combined):
        try:
            item_date = date.fromisoformat(match)
        except ValueError:
            continue
        if item_date <= target:
            score += 10
        elif (item_date - target).days <= 3:
            score += 6

    if re.search(r"\b(current state|source email was captured|no external)\b", combined, re.IGNORECASE):
        score -= 8

    return score


def collect_active_items(todo_text: str, target: date, limit: int) -> list[TodoItem]:
    sections = parse_markdown_sections(todo_text)
    items: list[TodoItem] = []
    for section in ACTIVE_SECTIONS:
        for line, text, details in parse_bullet_items(sections.get(section, [])):
            score = score_active_item(section, text, details, target)
            if score > 0:
                items.append(TodoItem(section, text, details, line, score))
    items.sort(key=lambda item: (-item.score, item.section != "In Progress", item.line))
    return items[:limit]


def collect_done_items(todo_text: str, target: date, limit: int) -> list[DoneItem]:
    sections = parse_markdown_sections(todo_text)
    done: list[DoneItem] = []
    target_prefix = target.isoformat()
    for line, text, details in parse_bullet_items(sections.get(DONE_SECTION, [])):
        combined = " ".join([text] + details)
        headline_dates = DATE_RE.findall(text)
        if (headline_dates and headline_dates[0] == target_prefix) or (
            not headline_dates and target_prefix in combined
        ):
            done.append(DoneItem(text=text, details=details, line=line))
    return done[:limit]


def load_papers_links(path: Path | None) -> list[tuple[str, str]]:
    if not path:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: list[Any]
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("links") or data.get("papers_links") or []
    else:
        rows = []

    links: list[tuple[str, str]] = []
    for row in rows:
        if isinstance(row, str):
            title, url = "Papers record", row
        elif isinstance(row, dict):
            title = str(row.get("title") or row.get("label") or "Papers record").strip()
            url = str(row.get("url") or row.get("href") or "").strip()
        else:
            continue
        if PAPERS_HOST_RE.match(url):
            links.append((title, url))
    return links


def format_ref(item: TodoItem | DoneItem) -> str:
    return f"Frank TODO line {item.line}"


def render_morning(items: list[TodoItem], target: date) -> str:
    lines = [
        f"To: {DEFAULT_TO}",
        f"Subject: {REPORT_PREFIX} morning priorities: {target.isoformat()}",
        "",
        "Robert,",
        "",
        "Useful pending work for this morning:",
        "",
    ]
    if not items:
        lines.append("- No active Frank TODO item passed the pending-work selector.")
    for item in items:
        lines.append(f"- {item.text} ({item.section}; {format_ref(item)})")
    lines.extend(
        [
            "",
            "Selection rule:",
            "- Uses only In Progress, Waiting for Next Step, and Backlog.",
            "- Excludes Done/completed/closed/filed/superseded items.",
            "- Prefers active tasks, blockers, due/dated items, OPS/Portal ids, and clear action verbs.",
            "",
            "[DRY RUN ONLY - not sent]",
            "",
        ]
    )
    return "\n".join(lines)


def render_eod(done: list[DoneItem], target: date, papers_links: list[tuple[str, str]]) -> str:
    lines = [
        f"To: {DEFAULT_TO}",
        f"Subject: {REPORT_PREFIX} end-of-day completed work: {target.isoformat()}",
        "",
        "Robert,",
        "",
        "Completed Frank work recorded today:",
        "",
    ]
    if not done:
        lines.append("- No completed Frank TODO entries were recorded for this date in approved local notes.")
    for item in done:
        lines.append(f"- {item.text} ({format_ref(item)})")

    if papers_links:
        lines.extend(["", "Papers:"])
        for title, url in papers_links:
            lines.append(f"- {title}: {url}")

    lines.extend(
        [
            "",
            "Source:",
            "- Frank TODO.md Done section and optional approved Papers metadata only.",
            "",
            "[DRY RUN ONLY - not sent]",
            "",
        ]
    )
    return "\n".join(lines)


def write_output(body: str, output: Path | None, report_type: str, target: date) -> Path | None:
    if output:
        path = output
    else:
        path = workspace_root() / "drafts" / f"{report_type}-{target.isoformat()}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render dry-run Frank morning-priority or end-of-day completed-work reports."
    )
    parser.add_argument("--type", choices=["morning", "eod"], required=True)
    parser.add_argument("--date", default=date.today().isoformat(), help="Report date YYYY-MM-DD.")
    parser.add_argument("--todo", default=str(workspace_root() / "TODO.md"))
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--papers-metadata-file", default="", help="Optional approved JSON metadata.")
    parser.add_argument("--output", default="", help="Optional output draft path.")
    parser.add_argument("--preview-only", action="store_true", help="Print without writing a draft.")
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        target = date.fromisoformat(args.date)
    except ValueError:
        print("Error: --date must be YYYY-MM-DD.", file=sys.stderr)
        return 2

    todo_path = Path(args.todo).expanduser()
    todo_text = read_text(todo_path)
    if not todo_text:
        print(f"Error: could not read TODO file: {todo_path}", file=sys.stderr)
        return 2

    output_path = Path(args.output).expanduser() if args.output else None
    papers_path = Path(args.papers_metadata_file).expanduser() if args.papers_metadata_file else None
    report_type = args.type
    selected: list[dict[str, Any]]

    if report_type == "morning":
        items = collect_active_items(todo_text, target, args.limit)
        body = render_morning(items, target)
        selected = [
            {"line": item.line, "section": item.section, "score": item.score, "text": item.text}
            for item in items
        ]
    else:
        done = collect_done_items(todo_text, target, args.limit)
        papers_links = load_papers_links(papers_path)
        body = render_eod(done, target, papers_links)
        selected = [{"line": item.line, "text": item.text} for item in done]

    written = None if args.preview_only else write_output(body, output_path, report_type, target)
    summary = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": report_type,
        "date": target.isoformat(),
        "todo": str(todo_path),
        "selected_count": len(selected),
        "selected": selected,
        "output": str(written) if written else "",
        "sent": False,
        "mailbox_mutated": False,
        "launchagent_changed": False,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(body)
        if written:
            print(f"Draft written: {written}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
