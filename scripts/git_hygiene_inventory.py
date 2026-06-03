#!/usr/local/bin/python3.13
"""Read-only git hygiene inventory for local workspaces.

The script discovers Git repositories under a root, then reports compact status
metadata. It does not fetch, clean, reset, stash, commit, push, or delete.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("/Users/werkstatt")
DEFAULT_SKIP_DIRS = {
    ".cache",
    ".private",
    "__pycache__",
    "node_modules",
    "vendor",
    "worktree",
}


@dataclass(frozen=True)
class GitResult:
    returncode: int
    stdout: str
    stderr: str


def run_git(repo: Path, args: list[str], timeout: int = 8) -> GitResult:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    return GitResult(completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def discover_repos(root: Path, include_worktrees: bool) -> list[Path]:
    repos: list[Path] = []
    skip_dirs = set(DEFAULT_SKIP_DIRS)
    if include_worktrees:
        skip_dirs.discard("worktree")
    for path, dirnames, filenames in root.walk(top_down=True):
        if ".git" in dirnames or ".git" in filenames:
            repos.append(path)
        if ".git" in dirnames:
            dirnames.remove(".git")
        dirnames[:] = [name for name in dirnames if name not in skip_dirs]
    return sorted(set(repos))


def parse_ahead_behind(status_line: str) -> str:
    if "[" not in status_line or "]" not in status_line:
        return ""
    return status_line[status_line.find("[") + 1 : status_line.find("]")]


def recommended_action(repo: Path, tracked_dirty: int, untracked: int, remote: str) -> str:
    repo_text = str(repo)
    if tracked_dirty == 0 and untracked == 0:
        if "/_removed_repos_" in repo_text:
            return "archived-clean-no-action"
        if not remote:
            return "clean-local-no-remote"
        return "clean-no-action"
    if repo.name in {"ai_workspace", "bid"} or repo_text.endswith("/ai_workspace") or repo_text.endswith("/bid"):
        return "review-active-work-before-commit"
    if untracked and not tracked_dirty:
        return "review-untracked-before-cleaning"
    return "review-dirty-worktree"


def inventory_repo(repo: Path, sample_limit: int) -> dict[str, Any]:
    branch = run_git(repo, ["branch", "--show-current"]).stdout
    head = run_git(repo, ["rev-parse", "--short", "HEAD"]).stdout
    remote_result = run_git(repo, ["remote", "get-url", "origin"])
    remote = remote_result.stdout if remote_result.returncode == 0 else ""
    status_sb = run_git(repo, ["status", "-sb", "--porcelain=v1"]).stdout
    status = run_git(repo, ["status", "--porcelain=v1"]).stdout
    status_lines = [line for line in status.splitlines() if line]
    tracked = [line for line in status_lines if not line.startswith("??")]
    untracked = [line for line in status_lines if line.startswith("??")]
    first_status_line = status_sb.splitlines()[0] if status_sb else ""
    worktrees_result = run_git(repo, ["worktree", "list", "--porcelain"])
    worktree_count = 0
    if worktrees_result.returncode == 0:
        worktree_count = sum(1 for line in worktrees_result.stdout.splitlines() if line.startswith("worktree "))

    return {
        "repo": str(repo),
        "branch": branch,
        "head": head,
        "remote": remote,
        "ahead_behind": parse_ahead_behind(first_status_line),
        "tracked_dirty": len(tracked),
        "untracked": len(untracked),
        "sample_tracked": tracked[:sample_limit],
        "sample_untracked": untracked[:sample_limit],
        "worktrees": worktree_count,
        "status_line": first_status_line,
        "recommended_action": recommended_action(repo, len(tracked), len(untracked), remote),
    }


def render_markdown(rows: list[dict[str, Any]], dirty_only: bool) -> str:
    selected = [row for row in rows if not dirty_only or row["tracked_dirty"] or row["untracked"]]
    lines = [
        "# Git Hygiene Inventory",
        "",
        "- mode: read-only",
        "- mutations: none; no fetch, clean, reset, stash, commit, push, or delete",
        f"- repos_scanned: `{len(rows)}`",
        f"- dirty_repos: `{sum(1 for row in rows if row['tracked_dirty'] or row['untracked'])}`",
        "",
        "| repo | branch | head | dirty | untracked | worktrees | action |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in selected:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["repo"],
                    row["branch"] or "(detached)",
                    row["head"],
                    str(row["tracked_dirty"]),
                    str(row["untracked"]),
                    str(row["worktrees"]),
                    row["recommended_action"],
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def plan_bucket(row: dict[str, Any]) -> str:
    if row["tracked_dirty"] == 0 and row["untracked"] == 0:
        return "clean"
    if row["repo"].endswith("/ai_workspace"):
        return "active-lane-work"
    if row["repo"].endswith("/bid"):
        return "finance-lane-review"
    if row["tracked_dirty"] == 0 and row["untracked"] > 0:
        return "untracked-review"
    if "/recursive-runs/" in row["repo"]:
        return "recursive-worktree-review"
    return "dirty-review"


def plan_next_step(bucket: str) -> str:
    steps = {
        "active-lane-work": "Review by lane and commit only coherent completed groups.",
        "finance-lane-review": "Review BID import/source artifacts before any commit or cleanup.",
        "untracked-review": "Identify whether untracked files are generated residue or real work.",
        "recursive-worktree-review": "Use recursive harness worktree-diff and retire-worktree proof gates.",
        "dirty-review": "Inspect tracked diff before deciding commit, split, or leave active.",
        "clean": "No action.",
    }
    return steps[bucket]


def build_plan(rows: list[dict[str, Any]]) -> dict[str, Any]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        bucket = plan_bucket(row)
        if bucket == "clean":
            continue
        buckets.setdefault(bucket, []).append(
            {
                "repo": row["repo"],
                "tracked_dirty": row["tracked_dirty"],
                "untracked": row["untracked"],
                "sample_tracked": row["sample_tracked"],
                "sample_untracked": row["sample_untracked"],
                "next_step": plan_next_step(bucket),
            }
        )
    return {
        "mode": "read-only-plan",
        "mutations": [],
        "repo_count": len(rows),
        "dirty_repo_count": sum(1 for row in rows if row["tracked_dirty"] or row["untracked"]),
        "buckets": buckets,
    }


def build_repo_packet(row: dict[str, Any]) -> dict[str, Any]:
    bucket = plan_bucket(row)
    return {
        "mode": "read-only-repo-detail",
        "mutations": [],
        "repo": row["repo"],
        "branch": row["branch"],
        "head": row["head"],
        "remote": row["remote"],
        "ahead_behind": row["ahead_behind"],
        "tracked_dirty": row["tracked_dirty"],
        "untracked": row["untracked"],
        "worktrees": row["worktrees"],
        "bucket": bucket,
        "next_step": plan_next_step(bucket),
        "sample_tracked": row["sample_tracked"],
        "sample_untracked": row["sample_untracked"],
    }


def repo_packet_for_arg(repo_arg: str, root: Path, sample_limit: int) -> dict[str, Any]:
    requested = Path(repo_arg)
    if not requested.is_absolute():
        requested = root / requested
    requested = requested.resolve()
    git_marker = requested / ".git"
    if not git_marker.exists():
        raise ValueError(f"repo is not a git checkout: {requested}")
    return build_repo_packet(inventory_repo(requested, sample_limit))


def render_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Git Hygiene Plan",
        "",
        "- mode: read-only-plan",
        "- mutations: none; no fetch, clean, reset, stash, commit, push, or delete",
        f"- repos_scanned: `{plan['repo_count']}`",
        f"- dirty_repos: `{plan['dirty_repo_count']}`",
        "",
    ]
    for bucket, items in plan["buckets"].items():
        lines.extend([f"## {bucket}", "", "| repo | dirty | untracked | next_step |", "| --- | ---: | ---: | --- |"])
        for item in items:
            lines.append(
                "| "
                + " | ".join(
                    [
                        item["repo"],
                        str(item["tracked_dirty"]),
                        str(item["untracked"]),
                        item["next_step"],
                    ]
                )
                + " |"
            )
        lines.append("")
    if not plan["buckets"]:
        lines.append("No dirty repositories found.\n")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--dirty-only", action="store_true", help="Only show repos with tracked or untracked changes.")
    parser.add_argument("--include-worktrees", action="store_true", help="Include nested Git worktrees in recursive run folders.")
    parser.add_argument("--plan", action="store_true", help="Group dirty repositories into read-only next-action buckets.")
    parser.add_argument("--repo", default="", help="Emit one read-only action packet for a single repository.")
    parser.add_argument("--sample-limit", type=int, default=8, help="Maximum sample paths per dirty category.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if args.repo:
        packet = repo_packet_for_arg(args.repo, root, max(0, args.sample_limit))
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0

    repos = discover_repos(root, args.include_worktrees)
    rows = [inventory_repo(repo, max(0, args.sample_limit)) for repo in repos]
    if args.plan:
        plan = build_plan(rows)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            print(render_plan_markdown(plan), end="")
    elif args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print(render_markdown(rows, args.dirty_only), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
