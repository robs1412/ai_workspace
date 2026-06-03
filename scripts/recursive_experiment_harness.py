#!/usr/local/bin/python3.13
"""Bounded recursive experiment harness.

This script manages one approved mutable surface and one immutable evaluator
per run. It records compact attempt/proof state under project_hub/recursive-runs
and intentionally does not mutate daemons, credentials, OPS/Portal, mailbox
state, or shared git history.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


WORKSPACE_ROOT = Path("/Users/werkstatt/ai_workspace")
ALLOWED_ROOT = Path("/Users/werkstatt")
RUNS_ROOT = WORKSPACE_ROOT / "project_hub" / "recursive-runs"
ATTEMPT_FIELDS = ["attempt_id", "hypothesis", "surface", "metric", "status", "proof", "reason"]


@dataclass(frozen=True)
class Evaluator:
    run_id: str
    surface: str
    evaluator: str
    metric: str
    created_at: str


def now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def safe_slug(value: str) -> str:
    allowed = []
    for char in value.strip():
        if char.isalnum() or char in {"-", "_", "."}:
            allowed.append(char)
        elif char.isspace():
            allowed.append("-")
    slug = "".join(allowed).strip("-._")
    if not slug:
        raise ValueError("run-id or attempt-id must contain at least one safe character")
    if slug in {".", ".."} or "/" in slug:
        raise ValueError(f"unsafe id: {value}")
    return slug


def run_dir(run_id: str) -> Path:
    return RUNS_ROOT / safe_slug(run_id)


def evaluator_path(run_id: str) -> Path:
    return run_dir(run_id) / "evaluator.json"


def attempts_path(run_id: str) -> Path:
    return run_dir(run_id) / "attempts.tsv"


def proof_dir(run_id: str) -> Path:
    return run_dir(run_id) / "proofs"


def report_path(run_id: str) -> Path:
    return run_dir(run_id) / "run-report.md"


def worktree_path(run_id: str) -> Path:
    return run_dir(run_id) / "worktree"


def normalize_surface(surface: str) -> str:
    raw = Path(surface)
    if raw.is_absolute():
        resolved = raw.resolve()
    else:
        resolved = (WORKSPACE_ROOT / raw).resolve()
    try:
        resolved.relative_to(ALLOWED_ROOT)
    except ValueError as exc:
        raise ValueError(f"surface must stay under {ALLOWED_ROOT}: {surface}") from exc
    try:
        return str(resolved.relative_to(WORKSPACE_ROOT))
    except ValueError as exc:
        raise ValueError(f"surface must stay in the ai_workspace tree: {surface}") from exc


def load_evaluator(run_id: str) -> Evaluator:
    path = evaluator_path(run_id)
    if not path.exists():
        raise FileNotFoundError(f"run is not initialized: {run_id}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return Evaluator(
        run_id=str(data["run_id"]),
        surface=str(data["surface"]),
        evaluator=str(data["evaluator"]),
        metric=str(data["metric"]),
        created_at=str(data.get("created_at", "")),
    )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_attempts_file(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ATTEMPT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()


def read_attempts(run_id: str) -> list[dict[str, str]]:
    path = attempts_path(run_id)
    ensure_attempts_file(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle, delimiter="\t")]


def write_attempts(run_id: str, rows: list[dict[str, str]]) -> None:
    path = attempts_path(run_id)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ATTEMPT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in ATTEMPT_FIELDS})


def find_attempt(rows: list[dict[str, str]], attempt_id: str) -> dict[str, str]:
    for row in rows:
        if row.get("attempt_id") == attempt_id:
            return row
    raise ValueError(f"attempt not found: {attempt_id}")


def git_output(args: list[str], cwd: Path = WORKSPACE_ROOT) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout).strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def git_output_bytes(args: list[str], cwd: Path = WORKSPACE_ROOT) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).decode("utf-8", errors="replace").strip()
        raise RuntimeError(detail or f"git {' '.join(args)} failed")
    return completed.stdout


def is_empty_dir(path: Path) -> bool:
    return path.is_dir() and not any(path.iterdir())


def owned_worktree_ok(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        top = Path(git_output(["rev-parse", "--show-toplevel"], cwd=path)).resolve()
    except RuntimeError:
        return False
    return top == path.resolve() and (path / ".git").exists()


def ensure_owned_worktree(run_id: str) -> Path:
    path = worktree_path(run_id)
    if owned_worktree_ok(path):
        return path
    if path.exists():
        if is_empty_dir(path):
            path.rmdir()
        else:
            raise ValueError(f"worktree path exists but is not an owned Git worktree: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    branch = f"recursive/{run_id}"
    existing_branches = git_output(["branch", "--format=%(refname:short)"]).splitlines()
    command = ["worktree", "add"]
    if branch in existing_branches:
        command.extend([str(path), branch])
    else:
        command.extend(["-b", branch, str(path), "HEAD"])
    git_output(command)
    if not owned_worktree_ok(path):
        raise RuntimeError(f"failed to create owned Git worktree at {path}")
    return path


def git_output_or_empty(args: list[str], cwd: Path) -> str:
    try:
        return git_output(args, cwd=cwd)
    except RuntimeError:
        return ""


def worktree_summary(path: Path) -> dict[str, Any]:
    if not owned_worktree_ok(path):
        return {
            "state": "missing_or_unowned",
            "path": str(path),
            "branch": "",
            "head": "",
            "dirty_files": [],
        }
    status = git_output_or_empty(["status", "--short"], cwd=path)
    return {
        "state": "owned_git_worktree",
        "path": str(path),
        "branch": git_output_or_empty(["branch", "--show-current"], cwd=path),
        "head": git_output_or_empty(["rev-parse", "--short", "HEAD"], cwd=path),
        "dirty_files": [line for line in status.splitlines() if line.strip()],
    }


def promotion_proof_summaries(run_id: str, limit: int) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for path in sorted(proof_dir(run_id).glob("*-promote.json"), key=lambda item: item.stat().st_mtime):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        apply_check = data.get("apply_check")
        summaries.append(
            {
                "proof": str(path.relative_to(run_dir(run_id))),
                "attempt_id": data.get("attempt_id", ""),
                "ok": data.get("ok"),
                "promotion_status": data.get("promotion_status", ""),
                "patch_sha256": data.get("patch_sha256", ""),
                "dry_run": data.get("dry_run"),
                "apply_check_returncode": apply_check.get("returncode") if isinstance(apply_check, dict) else None,
            }
        )
    return summaries[-max(0, limit) :]


def latest_promotion_proof(run_id: str) -> dict[str, Any] | None:
    summaries = promotion_proof_summaries(run_id, 1)
    return summaries[-1] if summaries else None


def retire_worktree_decision(run_id: str) -> dict[str, Any]:
    worktree = worktree_path(run_id)
    summary = worktree_summary(worktree)
    latest_proof = latest_promotion_proof(run_id)
    blockers: list[str] = []
    if summary["state"] != "owned_git_worktree":
        blockers.append("worktree_missing_or_unowned")
    if summary["dirty_files"]:
        blockers.append("worktree_dirty")
    if not latest_proof:
        blockers.append("missing_promotion_proof")
    elif latest_proof.get("promotion_status") not in {"applied", "apply_check_failed"}:
        blockers.append(f"unsupported_promotion_status:{latest_proof.get('promotion_status')}")
    return {
        "run_id": run_id,
        "worktree": summary,
        "latest_promotion_proof": latest_proof,
        "can_retire": not blockers,
        "blockers": blockers,
    }


def update_run_report(run_id: str) -> None:
    evaluator = load_evaluator(run_id)
    rows = read_attempts(run_id)
    worktree = worktree_path(run_id)
    summary = worktree_summary(worktree)
    lines = [
        f"# Recursive Run {run_id}",
        "",
        f"- updated_at: `{now_local()}`",
        f"- surface: `{evaluator.surface}`",
        f"- metric: `{evaluator.metric}`",
        f"- evaluator: `{evaluator.evaluator}`",
        f"- worktree: `{worktree.relative_to(run_dir(run_id))}`",
        f"- worktree_state: `{summary['state']}`",
        f"- worktree_branch: `{summary['branch']}`",
        f"- worktree_head: `{summary['head']}`",
        f"- worktree_dirty_files: `{len(summary['dirty_files'])}`",
        "",
        "## Attempts",
        "",
        "| attempt | status | metric | proof | reason |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("attempt_id", ""),
                    row.get("status", ""),
                    row.get("metric", ""),
                    row.get("proof", ""),
                    row.get("reason", ""),
                ]
            )
            + " |"
        )
    report_path(run_id).write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_status(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    evaluator = load_evaluator(run_id)
    attempts = read_attempts(run_id)
    worktree = worktree_path(run_id)
    summary = {
        "ok": True,
        "run_id": run_id,
        "run_dir": str(run_dir(run_id)),
        "surface": evaluator.surface,
        "metric": evaluator.metric,
        "evaluator": evaluator.evaluator,
        "created_at": evaluator.created_at,
        "worktree": worktree_summary(worktree),
        "attempt_count": len(attempts),
        "attempts": attempts[-max(0, int(args.limit)) :],
        "promotion_proofs": promotion_proof_summaries(run_id, int(args.limit)),
        "report": str(report_path(run_id)),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def cmd_retire_worktree(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    decision = retire_worktree_decision(run_id)
    decision["dry_run"] = not args.apply
    decision["retired"] = False
    if args.apply:
        if not decision["can_retire"]:
            raise ValueError("worktree is not retireable: " + ", ".join(decision["blockers"]))
        completed = subprocess.run(
            ["git", "worktree", "remove", str(worktree_path(run_id))],
            cwd=str(WORKSPACE_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        decision["remove"] = {
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        if completed.returncode != 0:
            raise RuntimeError((completed.stderr or completed.stdout).strip() or "git worktree remove failed")
        decision["retired"] = True
    print(json.dumps({"ok": decision["can_retire"] or not args.apply, **decision}, indent=2, sort_keys=True))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    surface = normalize_surface(args.surface)
    evaluator = Evaluator(
        run_id=run_id,
        surface=surface,
        evaluator=args.evaluator,
        metric=args.metric,
        created_at=now_local(),
    )
    directory = run_dir(run_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "proofs").mkdir(exist_ok=True)

    existing_path = evaluator_path(run_id)
    if existing_path.exists():
        existing = load_evaluator(run_id)
        if (
            existing.surface != evaluator.surface
            or existing.evaluator != evaluator.evaluator
            or existing.metric != evaluator.metric
        ):
            raise ValueError("run already has an immutable evaluator; create a new run for changes")
    else:
        write_json(existing_path, evaluator.__dict__)

    program_path = directory / "program.md"
    if not program_path.exists():
        program_path.write_text(
            "\n".join(
                [
                    f"# Recursive Program {run_id}",
                    "",
                    f"- created_at: `{evaluator.created_at}`",
                    f"- mutable_surface: `{surface}`",
                    f"- immutable_evaluator: `{args.evaluator}`",
                    f"- metric: `{args.metric}`",
                    "",
                    "## Boundary",
                    "",
                    "One mutable surface, one immutable proof command, compact ledger only.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
    ensure_attempts_file(attempts_path(run_id))
    owned_worktree = ensure_owned_worktree(run_id)
    update_run_report(run_id)
    print(json.dumps({"ok": True, "run_dir": str(directory), "surface": surface, "worktree": str(owned_worktree)}, indent=2))
    return 0


def cmd_record_attempt(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    attempt_id = safe_slug(args.attempt_id or datetime.now().astimezone().strftime("%Y%m%d%H%M%S"))
    evaluator = load_evaluator(run_id)
    if normalize_surface(args.surface) != evaluator.surface:
        raise ValueError(f"attempt surface must match run surface: {evaluator.surface}")
    rows = read_attempts(run_id)
    if any(row.get("attempt_id") == attempt_id for row in rows):
        raise ValueError(f"attempt already exists: {attempt_id}")
    rows.append(
        {
            "attempt_id": attempt_id,
            "hypothesis": args.hypothesis,
            "surface": evaluator.surface,
            "metric": "",
            "status": "recorded",
            "proof": "",
            "reason": "",
        }
    )
    write_attempts(run_id, rows)
    update_run_report(run_id)
    print(json.dumps({"ok": True, "attempt_id": attempt_id}, indent=2))
    return 0


def parse_metric(metric_name: str, stdout: str, result: dict[str, Any]) -> str:
    parsed: Any = None
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        if metric_name in parsed:
            return str(parsed[metric_name])
        if metric_name == "proof_status" and "status" in parsed:
            return str(parsed["status"])
        if metric_name == "drift_count":
            if isinstance(parsed.get("drifts"), list):
                return str(len(parsed["drifts"]))
            if isinstance(parsed.get("items"), list):
                return str(len(parsed["items"]))
    for line in stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip() == metric_name:
            return value.strip()
    return str(result["returncode"])


def cmd_verify(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    attempt_id = safe_slug(args.attempt_id)
    evaluator = load_evaluator(run_id)
    evaluator_cwd = ensure_owned_worktree(run_id)
    rows = read_attempts(run_id)
    row = find_attempt(rows, attempt_id)

    started_at = now_local()
    completed = subprocess.run(
        shlex.split(evaluator.evaluator),
        cwd=str(evaluator_cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(1, int(args.timeout_seconds)),
        check=False,
    )
    finished_at = now_local()

    proof_base = proof_dir(run_id) / attempt_id
    stdout_path = proof_base.with_suffix(".stdout.txt")
    stderr_path = proof_base.with_suffix(".stderr.txt")
    result_path = proof_base.with_suffix(".json")
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    result = {
        "attempt_id": attempt_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "returncode": completed.returncode,
        "evaluator": evaluator.evaluator,
        "evaluator_cwd": str(evaluator_cwd),
        "stdout": str(stdout_path.relative_to(run_dir(run_id))),
        "stderr": str(stderr_path.relative_to(run_dir(run_id))),
    }
    result["metric"] = parse_metric(evaluator.metric, completed.stdout, result)
    write_json(result_path, result)

    row["metric"] = result["metric"]
    row["status"] = "verified" if completed.returncode == 0 else "crash"
    row["proof"] = str(result_path.relative_to(run_dir(run_id)))
    row["reason"] = "" if completed.returncode == 0 else "evaluator returned non-zero"
    write_attempts(run_id, rows)
    update_run_report(run_id)
    print(json.dumps({"ok": completed.returncode == 0, **result}, indent=2))
    return completed.returncode


def cmd_decide(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    status = args.status
    rows = read_attempts(run_id)
    row = find_attempt(rows, safe_slug(args.attempt_id))
    row["status"] = status
    row["reason"] = args.reason
    write_attempts(run_id, rows)
    update_run_report(run_id)
    print(json.dumps({"ok": True, "attempt_id": row["attempt_id"], "status": status}, indent=2))
    return 0


def run_evaluator(run_id: str, evaluator: Evaluator, timeout_seconds: int) -> dict[str, Any]:
    evaluator_cwd = ensure_owned_worktree(run_id)
    started_at = now_local()
    completed = subprocess.run(
        shlex.split(evaluator.evaluator),
        cwd=str(evaluator_cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(1, int(timeout_seconds)),
        check=False,
    )
    finished_at = now_local()
    result = {
        "started_at": started_at,
        "finished_at": finished_at,
        "returncode": completed.returncode,
        "evaluator": evaluator.evaluator,
        "evaluator_cwd": str(evaluator_cwd),
        "metric": parse_metric(evaluator.metric, completed.stdout, {"returncode": completed.returncode}),
        "stdout_text": completed.stdout,
        "stderr_text": completed.stderr,
    }
    return result


def write_promotion_proof(
    run_id: str,
    attempt_id: str,
    evaluator_result: dict[str, Any],
    patch_bytes: bytes,
    dry_run: bool,
) -> dict[str, str]:
    proof_base = proof_dir(run_id) / f"{attempt_id}-promote"
    patch_path = proof_base.with_suffix(".patch")
    stdout_path = proof_base.with_suffix(".stdout.txt")
    stderr_path = proof_base.with_suffix(".stderr.txt")
    result_path = proof_base.with_suffix(".json")
    patch_path.write_bytes(patch_bytes)
    stdout_path.write_text(str(evaluator_result.pop("stdout_text")), encoding="utf-8")
    stderr_path.write_text(str(evaluator_result.pop("stderr_text")), encoding="utf-8")
    patch_hash = hashlib.sha256(patch_bytes).hexdigest()
    write_json(
        result_path,
        {
            **evaluator_result,
            "attempt_id": attempt_id,
            "patch": str(patch_path.relative_to(run_dir(run_id))),
            "patch_sha256": patch_hash,
            "dry_run": dry_run,
            "stdout": str(stdout_path.relative_to(run_dir(run_id))),
            "stderr": str(stderr_path.relative_to(run_dir(run_id))),
        },
    )
    return {
        "patch": str(patch_path.relative_to(run_dir(run_id))),
        "patch_sha256": patch_hash,
        "proof": str(result_path.relative_to(run_dir(run_id))),
    }


def update_promotion_proof(
    run_id: str,
    proof: dict[str, str],
    *,
    apply_check: subprocess.CompletedProcess[str],
    promotion_status: str,
    apply_result: subprocess.CompletedProcess[str] | None = None,
) -> None:
    result_path = run_dir(run_id) / proof["proof"]
    data = json.loads(result_path.read_text(encoding="utf-8"))
    data["ok"] = promotion_status in {"dry_run_ok", "applied"}
    data["promotion_status"] = promotion_status
    data["apply_check"] = {
        "returncode": apply_check.returncode,
        "stdout": apply_check.stdout,
        "stderr": apply_check.stderr,
    }
    if apply_result is not None:
        data["apply"] = {
            "returncode": apply_result.returncode,
            "stdout": apply_result.stdout,
            "stderr": apply_result.stderr,
        }
    write_json(result_path, data)


def cmd_promote(args: argparse.Namespace) -> int:
    run_id = safe_slug(args.run_id)
    attempt_id = safe_slug(args.attempt_id)
    evaluator = load_evaluator(run_id)
    rows = read_attempts(run_id)
    row = find_attempt(rows, attempt_id)
    if row.get("status") != "keep":
        raise ValueError("only attempts already decided as keep can be promoted")
    if row.get("surface") != evaluator.surface:
        raise ValueError(f"attempt surface must match run surface: {evaluator.surface}")

    worktree = ensure_owned_worktree(run_id)
    surface = evaluator.surface
    main_dirty = git_output(["status", "--porcelain", "--", surface], cwd=WORKSPACE_ROOT)
    if main_dirty:
        raise ValueError(f"main checkout has uncommitted changes on surface {surface}; refusing promotion")

    evaluator_result = run_evaluator(run_id, evaluator, args.timeout_seconds)
    if evaluator_result["returncode"] != 0:
        raise RuntimeError("immutable evaluator failed before promotion")

    patch_bytes = git_output_bytes(["diff", "--binary", "--", surface], cwd=worktree)
    if not patch_bytes.strip():
        raise ValueError(f"no worktree patch found for surface {surface}")

    proof = write_promotion_proof(run_id, attempt_id, evaluator_result, patch_bytes, args.dry_run)
    check = subprocess.run(
        ["git", "apply", "--check", str((proof_dir(run_id) / f"{attempt_id}-promote.patch").resolve())],
        cwd=str(WORKSPACE_ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check.returncode != 0:
        update_promotion_proof(run_id, proof, apply_check=check, promotion_status="apply_check_failed")
        raise RuntimeError((check.stderr or check.stdout).strip() or "git apply --check failed")
    apply_result = None
    if not args.dry_run:
        apply_result = subprocess.run(
            ["git", "apply", str((proof_dir(run_id) / f"{attempt_id}-promote.patch").resolve())],
            cwd=str(WORKSPACE_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if apply_result.returncode != 0:
            update_promotion_proof(
                run_id,
                proof,
                apply_check=check,
                promotion_status="apply_failed",
                apply_result=apply_result,
            )
            raise RuntimeError((apply_result.stderr or apply_result.stdout).strip() or "git apply failed")
    update_promotion_proof(
        run_id,
        proof,
        apply_check=check,
        promotion_status="dry_run_ok" if args.dry_run else "applied",
        apply_result=apply_result,
    )

    update_run_report(run_id)
    print(
        json.dumps(
            {
                "ok": True,
                "run_id": run_id,
                "attempt_id": attempt_id,
                "surface": surface,
                "dry_run": args.dry_run,
                **proof,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="Summarize run, worktree, and latest attempt state.")
    status.add_argument("--run-id", required=True)
    status.add_argument("--limit", type=int, default=5)
    status.set_defaults(func=cmd_status)

    init = sub.add_parser("init", help="Create or verify an immutable run.")
    init.add_argument("--run-id", required=True)
    init.add_argument("--surface", required=True)
    init.add_argument("--evaluator", required=True)
    init.add_argument("--metric", required=True)
    init.set_defaults(func=cmd_init)

    record = sub.add_parser("record-attempt", help="Record a bounded attempt.")
    record.add_argument("--run-id", required=True)
    record.add_argument("--attempt-id", default="")
    record.add_argument("--hypothesis", required=True)
    record.add_argument("--surface", required=True)
    record.set_defaults(func=cmd_record_attempt)

    verify = sub.add_parser("verify", help="Run the immutable evaluator for an attempt.")
    verify.add_argument("--run-id", required=True)
    verify.add_argument("--attempt-id", required=True)
    verify.add_argument("--timeout-seconds", type=int, default=30)
    verify.set_defaults(func=cmd_verify)

    decide = sub.add_parser("decide", help="Mark the outcome for an attempt.")
    decide.add_argument("--run-id", required=True)
    decide.add_argument("--attempt-id", required=True)
    decide.add_argument("--status", choices=["keep", "discard", "crash", "needs-approval"], required=True)
    decide.add_argument("--reason", required=True)
    decide.set_defaults(func=cmd_decide)

    promote = sub.add_parser("promote", help="Apply a kept worktree patch to the main checkout after evaluator proof.")
    promote.add_argument("--run-id", required=True)
    promote.add_argument("--attempt-id", required=True)
    promote.add_argument("--timeout-seconds", type=int, default=30)
    promote.add_argument("--dry-run", action="store_true")
    promote.set_defaults(func=cmd_promote)

    retire = sub.add_parser("retire-worktree", help="Report or remove an owned recursive worktree after promotion proof.")
    retire.add_argument("--run-id", required=True)
    retire.add_argument("--apply", action="store_true")
    retire.set_defaults(func=cmd_retire_worktree)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        return int(args.func(args))
    except (FileNotFoundError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
