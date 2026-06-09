#!/usr/local/bin/python3.13
"""Record review decisions for dirty Git repositories.

This command is intentionally non-destructive. It records whether a dirty repo
has been reviewed for the current git status signature, but it does not commit,
stash, reset, clean, fetch, push, pull, or delete anything.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
DEFAULT_SCAN_ROOT = Path("/Users/werkstatt")
ARTIFACT_DIR = ROOT / "project_hub/artifacts/recursive-tools"
DECISION_LOG = ARTIFACT_DIR / "git-dirty-repo-decisions.jsonl"

DECISIONS = {
    "in_scope_active",
    "external_active",
    "generated_artifacts_kept",
    "leave_uncommitted",
    "needs_owner_review",
    "blocked",
}


def now_text() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def safe_text(value: object, limit: int = 500) -> str:
    return " ".join(str(value or "").split())[:limit]


def run_command(command: list[str], cwd: Path, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_json_command(command: list[str], cwd: Path, timeout: int = 240) -> dict[str, Any]:
    proc = run_command(command, cwd, timeout=timeout)
    if proc.returncode != 0:
        raise SystemExit(f"command failed: {command}: {safe_text(proc.stderr or proc.stdout)}")
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"command returned invalid JSON: {command}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"command returned non-object JSON: {command}")
    return parsed


def git_output(repo: Path, args: list[str], timeout: int = 20) -> str:
    proc = run_command(["git", *args], repo, timeout=timeout)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed in {repo}: {safe_text(proc.stderr or proc.stdout)}")
    return proc.stdout.strip()


def status_lines(repo: Path) -> list[str]:
    raw = git_output(repo, ["status", "--porcelain=v1"])
    return [line for line in raw.splitlines() if line]


def repo_signature(repo: Path) -> dict[str, Any]:
    lines = status_lines(repo)
    tracked = [line for line in lines if not line.startswith("??")]
    untracked = [line for line in lines if line.startswith("??")]
    head = git_output(repo, ["rev-parse", "--short", "HEAD"])
    branch = git_output(repo, ["branch", "--show-current"])
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:16]
    return {
        "repo": str(repo),
        "branch": branch,
        "head": head,
        "tracked_dirty": len(tracked),
        "untracked": len(untracked),
        "status_hash": digest,
        "state_signature": f"{head}:{len(tracked)}:{len(untracked)}:{digest}",
    }


def read_decisions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def dirty_repos(scan_root: Path) -> list[dict[str, Any]]:
    plan = run_json_command(
        [
            "/usr/local/bin/python3.13",
            "scripts/git_hygiene_inventory.py",
            "--root",
            str(scan_root),
            "--plan",
            "--json",
        ],
        ROOT,
        timeout=240,
    )
    repos: list[dict[str, Any]] = []
    for rows in (plan.get("buckets") or {}).values():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if isinstance(row, dict) and row.get("repo"):
                repos.append(row)
    return sorted(repos, key=lambda item: str(item.get("repo")))


def latest_decision_by_signature(decisions: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in decisions:
        repo = str(row.get("repo") or "")
        signature = str(row.get("state_signature") or "")
        if repo and signature:
            latest[(repo, signature)] = row
    return latest


def collect_status(args: argparse.Namespace) -> dict[str, Any]:
    decisions = read_decisions(args.decision_log)
    latest = latest_decision_by_signature(decisions)
    repos = []
    pending = 0
    blocked = 0
    for row in dirty_repos(args.scan_root):
        repo = Path(str(row["repo"]))
        signature = repo_signature(repo)
        decision = latest.get((str(repo), signature["state_signature"]))
        decision_name = str((decision or {}).get("decision") or "")
        review_status = "reviewed" if decision else "pending_review"
        if decision_name in {"blocked", "needs_owner_review"}:
            blocked += 1
        if not decision:
            pending += 1
        repos.append(
            {
                **signature,
                "bucket": row.get("next_step", ""),
                "review_status": review_status,
                "decision": decision_name,
                "reviewed_at": (decision or {}).get("reviewed_at", ""),
                "notes": (decision or {}).get("notes", ""),
                "sample_tracked": row.get("sample_tracked") or [],
                "sample_untracked": row.get("sample_untracked") or [],
            }
        )
    return {
        "ok": True,
        "checked_at": now_text(),
        "repo_count": len(repos),
        "pending_review_count": pending,
        "blocked_review_count": blocked,
        "reviewed_count": len(repos) - pending,
        "repos": repos,
    }


def record_decision(args: argparse.Namespace) -> int:
    repo = Path(args.repo).expanduser().resolve()
    if not (repo / ".git").exists() and not (repo / ".git").is_file():
        raise SystemExit(f"not a git repo: {repo}")
    if args.decision in {"blocked", "needs_owner_review"} and not args.notes:
        raise SystemExit(f"--notes is required for decision {args.decision}")
    signature = repo_signature(repo)
    event = {
        "event": "git_dirty_repo_reviewed",
        "reviewed_at": now_text(),
        "reviewed_by": args.reviewed_by,
        "repo": str(repo),
        "decision": args.decision,
        "source_ref": args.source_ref,
        "notes": args.notes,
        **signature,
    }
    append_jsonl(args.decision_log, event)
    if args.json:
        print(json.dumps(event, indent=2, sort_keys=True))
    else:
        print(f"repo={repo}")
        print(f"decision={args.decision}")
        print(f"state_signature={signature['state_signature']}")
        print(f"decision_log={args.decision_log}")
    return 0


def status(args: argparse.Namespace) -> int:
    data = collect_status(args)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(f"repo_count={data['repo_count']}")
        print(f"pending_review_count={data['pending_review_count']}")
        print(f"blocked_review_count={data['blocked_review_count']}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-root", type=Path, default=DEFAULT_SCAN_ROOT)
    parser.add_argument("--decision-log", type=Path, default=DECISION_LOG)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--json", action="store_true")
    status_parser.set_defaults(func=status)

    record_parser = subparsers.add_parser("record")
    record_parser.add_argument("--repo", required=True)
    record_parser.add_argument("--decision", required=True, choices=sorted(DECISIONS))
    record_parser.add_argument("--reviewed-by", default="Codex")
    record_parser.add_argument("--source-ref", default="")
    record_parser.add_argument("--notes", default="")
    record_parser.add_argument("--json", action="store_true")
    record_parser.set_defaults(func=record_decision)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
