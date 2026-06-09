#!/usr/local/bin/python3.13
"""Read-only git hygiene inventory for local workspaces.

The script discovers Git repositories under a root, then reports compact status
metadata. It does not fetch, clean, reset, stash, commit, push, or delete.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
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

LIVE_CHECKOUT_POLICIES = {
    "ai_workspace": {
        "kind": "coordination_repo",
        "known_live_checkout": "",
        "live_update_policy": "no_live_pull",
        "notes": "Coordination repo; commit/push only after explicit owner approval.",
    },
    "workspaceboard": {
        "kind": "local_runtime_copy",
        "known_live_checkout": "/Users/admin/.workspaceboard-launch/runtime/app",
        "live_update_policy": "runtime_copy_restart",
        "notes": "Runtime copy/restart path is outside /Users/werkstatt and is not inspected by this read-only inventory.",
    },
    "salesreport": {
        "kind": "web_module",
        "known_live_checkout": "/home/koval/public_html/salesreport",
        "live_update_policy": "live_pull",
        "notes": "Live pull requires explicit approval plus clean live checkout readback before mutation.",
    },
    "bid": {
        "kind": "web_module",
        "known_live_checkout": "",
        "live_update_policy": "push_only_no_live_pull",
        "notes": "BID is push-only; do not plan a live pull unless the owner supplies a newer module rule.",
    },
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


def ahead_behind_counts(ahead_behind: str) -> dict[str, int]:
    counts = {"ahead": 0, "behind": 0}
    for chunk in ahead_behind.split(","):
        parts = chunk.strip().split()
        if len(parts) == 2 and parts[0] in counts:
            try:
                counts[parts[0]] = int(parts[1])
            except ValueError:
                counts[parts[0]] = 0
    return counts


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


def status_path(status_line: str) -> str:
    if status_line.startswith("?? "):
        return status_line[3:]
    value = status_line[2:] if len(status_line) > 2 else status_line
    if " -> " in value:
        value = value.split(" -> ", 1)[1]
    return value.strip()


def top_level_group(path: str) -> str:
    cleaned = path.strip().lstrip("/")
    if not cleaned:
        return "."
    return cleaned.split("/", 1)[0]


def group_status_lines(lines: list[str], sample_limit: int) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for line in lines:
        path = status_path(line)
        group = top_level_group(path)
        item = groups.setdefault(group, {"group": group, "count": 0, "samples": []})
        item["count"] += 1
        if len(item["samples"]) < sample_limit:
            item["samples"].append(line)
    return sorted(groups.values(), key=lambda item: (-item["count"], item["group"]))


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
        "tracked_groups": group_status_lines(tracked, sample_limit),
        "untracked_groups": group_status_lines(untracked, sample_limit),
        "worktrees": worktree_count,
        "status_line": first_status_line,
        "recommended_action": recommended_action(repo, len(tracked), len(untracked), remote),
    }


def live_checkout_policy(repo: str) -> dict[str, Any]:
    name = Path(repo).name
    policy = LIVE_CHECKOUT_POLICIES.get(
        name,
        {
            "kind": "unknown",
            "known_live_checkout": "",
            "live_update_policy": "unknown",
            "notes": "No live checkout policy is registered for this repo.",
        },
    )
    known_live_checkout = policy["known_live_checkout"]
    live_state = "not_applicable"
    live_dirty_state = "not_applicable"
    if known_live_checkout:
        live_path = Path(known_live_checkout)
        if not str(live_path).startswith("/Users/werkstatt/"):
            live_state = "not_checked_outside_workspace"
            live_dirty_state = "unknown_not_checked"
        elif not live_path.exists():
            live_state = "missing"
            live_dirty_state = "unknown_missing"
        elif not (live_path / ".git").exists() and not (live_path / ".git").is_file():
            live_state = "not_git_checkout"
            live_dirty_state = "unknown_not_git"
        else:
            status = run_git(live_path, ["status", "--porcelain=v1"])
            live_state = "checked" if status.returncode == 0 else "status_failed"
            live_dirty_state = "dirty" if status.stdout.strip() else "clean"
    return {
        **policy,
        "live_state": live_state,
        "live_dirty_state": live_dirty_state,
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
                "tracked_groups": row["tracked_groups"],
                "untracked_groups": row["untracked_groups"],
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


def action_gate(
    operation: str,
    row: dict[str, Any],
    selected_repos: set[str],
    approval_ref: str,
    live_policy: dict[str, Any],
) -> dict[str, Any]:
    repo = row["repo"]
    selected = repo in selected_repos or Path(repo).name in selected_repos
    dirty = bool(row["tracked_dirty"] or row["untracked"])
    remote = bool(row["remote"])
    counts = ahead_behind_counts(row["ahead_behind"])
    blockers: list[str] = []
    exclusions: list[str] = []

    if operation == "commit":
        if not dirty:
            exclusions.append("repo_clean")
        if not selected:
            blockers.append("repo_not_selected")
    elif operation == "push":
        if not remote:
            blockers.append("missing_origin_remote")
        if not selected:
            blockers.append("repo_not_selected")
        if counts["ahead"] == 0:
            exclusions.append("no_local_commits_ahead")
    elif operation == "pull_live":
        if live_policy["live_update_policy"] != "live_pull":
            exclusions.append(f"live_policy_{live_policy['live_update_policy']}")
        if not selected:
            blockers.append("repo_not_selected")
        if live_policy["live_dirty_state"] != "clean":
            blockers.append(f"live_dirty_state_{live_policy['live_dirty_state']}")

    if not approval_ref:
        blockers.append("missing_explicit_approval_ref")

    return {
        "operation": operation,
        "selected": selected,
        "approval_ref": approval_ref,
        "allowed_to_execute": False,
        "would_require_approval": True,
        "blockers": blockers,
        "exclusions": exclusions,
        "next_step": "Record explicit owner approval and rerun a preflight verifier before executing this operation.",
    }


def build_action_plan(rows: list[dict[str, Any]], selected_repos: set[str], approval_ref: str) -> dict[str, Any]:
    repos = []
    for row in rows:
        if row["tracked_dirty"] == 0 and row["untracked"] == 0 and row["ahead_behind"] == "":
            continue
        live_policy = live_checkout_policy(row["repo"])
        repos.append(
            {
                "repo": row["repo"],
                "branch": row["branch"],
                "head": row["head"],
                "remote": row["remote"],
                "ahead_behind": row["ahead_behind"],
                "ahead_behind_counts": ahead_behind_counts(row["ahead_behind"]),
                "tracked_dirty": row["tracked_dirty"],
                "untracked": row["untracked"],
                "dirty_files_sample": row["sample_tracked"] + row["sample_untracked"],
                "tracked_groups": row["tracked_groups"],
                "untracked_groups": row["untracked_groups"],
                "bucket": plan_bucket(row),
                "known_live_checkout": live_policy["known_live_checkout"],
                "live_update_policy": live_policy["live_update_policy"],
                "live_state": live_policy["live_state"],
                "live_dirty_state": live_policy["live_dirty_state"],
                "live_policy_notes": live_policy["notes"],
                "operations": [
                    action_gate("commit", row, selected_repos, approval_ref, live_policy),
                    action_gate("push", row, selected_repos, approval_ref, live_policy),
                    action_gate("pull_live", row, selected_repos, approval_ref, live_policy),
                ],
            }
        )
    return {
        "mode": "read-only-approved-action-plan",
        "mutations": [],
        "approval_required": True,
        "approval_ref": approval_ref,
        "selected_repos": sorted(selected_repos),
        "repo_count": len(rows),
        "planned_repo_count": len(repos),
        "dirty_repo_count": sum(1 for row in rows if row["tracked_dirty"] or row["untracked"]),
        "boundary": "No commit, push, pull, clean, reset, stash, or delete is performed by this generator.",
        "repos": repos,
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
        "tracked_groups": row["tracked_groups"],
        "untracked_groups": row["untracked_groups"],
    }


def group_detail_packet(row: dict[str, Any], group: str, tracked_lines: list[str], untracked_lines: list[str]) -> dict[str, Any]:
    tracked = [line for line in tracked_lines if top_level_group(status_path(line)) == group]
    untracked = [line for line in untracked_lines if top_level_group(status_path(line)) == group]
    tracked_count = next((item["count"] for item in row["tracked_groups"] if item["group"] == group), 0)
    untracked_count = next((item["count"] for item in row["untracked_groups"] if item["group"] == group), 0)
    return {
        "mode": "read-only-group-detail",
        "mutations": [],
        "repo": row["repo"],
        "group": group,
        "tracked_count": tracked_count,
        "untracked_count": untracked_count,
        "tracked": tracked,
        "untracked": untracked,
        "next_step": "Review this group as one coherent lane before commit, cleanup, or leave-active decisions.",
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


def group_packet_for_arg(repo_arg: str, group: str, root: Path, sample_limit: int) -> dict[str, Any]:
    requested = Path(repo_arg)
    if not requested.is_absolute():
        requested = root / requested
    requested = requested.resolve()
    git_marker = requested / ".git"
    if not git_marker.exists():
        raise ValueError(f"repo is not a git checkout: {requested}")
    row = inventory_repo(requested, sample_limit)
    status = run_git(requested, ["status", "--porcelain=v1"]).stdout
    status_lines = [line for line in status.splitlines() if line]
    tracked = [line for line in status_lines if not line.startswith("??")]
    untracked = [line for line in status_lines if line.startswith("??")]
    packet = group_detail_packet(row, group, tracked, untracked)
    if packet["tracked_count"] == 0 and packet["untracked_count"] == 0:
        raise ValueError(f"group not dirty in repo: {group}")
    return packet


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


def render_action_plan_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Git Hygiene Approved Action Plan",
        "",
        "- mode: read-only-approved-action-plan",
        "- mutations: none; no commit, push, pull, clean, reset, stash, or delete",
        f"- approval_ref: `{plan['approval_ref']}`",
        f"- selected_repos: `{json.dumps(plan['selected_repos'])}`",
        f"- repos_scanned: `{plan['repo_count']}`",
        f"- planned_repos: `{plan['planned_repo_count']}`",
        f"- dirty_repos: `{plan['dirty_repo_count']}`",
        "",
        "| repo | branch | head | dirty | untracked | ahead/behind | live_policy | live_dirty | blocked_ops |",
        "| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for repo in plan["repos"]:
        blocked_ops = [
            op["operation"]
            for op in repo["operations"]
            if op["blockers"]
        ]
        lines.append(
            "| "
            + " | ".join(
                [
                    repo["repo"],
                    repo["branch"] or "(detached)",
                    repo["head"],
                    str(repo["tracked_dirty"]),
                    str(repo["untracked"]),
                    repo["ahead_behind"],
                    repo["live_update_policy"],
                    repo["live_dirty_state"],
                    ", ".join(blocked_ops) or "none",
                ]
            )
            + " |"
        )
    if not plan["repos"]:
        lines.append("")
        lines.append("No dirty or ahead/behind repositories found.")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="Root directory to scan.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--dirty-only", action="store_true", help="Only show repos with tracked or untracked changes.")
    parser.add_argument("--include-worktrees", action="store_true", help="Include nested Git worktrees in recursive run folders.")
    parser.add_argument("--plan", action="store_true", help="Group dirty repositories into read-only next-action buckets.")
    parser.add_argument("--action-plan", action="store_true", help="Emit read-only commit/push/live-pull action gates.")
    parser.add_argument("--selected-repo", action="append", default=[], help="Repo path or basename selected for approved action planning.")
    parser.add_argument("--approval-ref", default="", help="Human approval reference for selected repo action gates.")
    parser.add_argument("--repo", default="", help="Emit one read-only action packet for a single repository.")
    parser.add_argument("--group", default="", help="With --repo, emit one top-level dirty group packet.")
    parser.add_argument("--sample-limit", type=int, default=8, help="Maximum sample paths per dirty category.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if args.group and not args.repo:
        raise ValueError("--group requires --repo")
    if args.repo:
        if args.group:
            packet = group_packet_for_arg(args.repo, args.group, root, max(0, args.sample_limit))
        else:
            packet = repo_packet_for_arg(args.repo, root, max(0, args.sample_limit))
        print(json.dumps(packet, indent=2, sort_keys=True))
        return 0

    repos = discover_repos(root, args.include_worktrees)
    rows = [inventory_repo(repo, max(0, args.sample_limit)) for repo in repos]
    if args.action_plan:
        plan = build_action_plan(rows, set(args.selected_repo), args.approval_ref)
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            print(render_action_plan_markdown(plan), end="")
    elif args.plan:
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


def cli() -> int:
    try:
        return main()
    except (ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"ok": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(cli())
