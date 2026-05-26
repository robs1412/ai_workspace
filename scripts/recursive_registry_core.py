#!/usr/local/bin/python3.13
"""Shared registry loading and structural validation for recursive checkers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_task_flow_truth_config(config: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(config, dict), "config must be an object")
    require(config.get("version") == 1, "config.version must be 1")

    board = config.get("board")
    require(isinstance(board, dict), "config.board must be an object")
    require(isinstance(board.get("status_url"), str) and board["status_url"], "board.status_url is required")
    require(
        isinstance(board.get("managed_sessions_key"), str) and board["managed_sessions_key"],
        "board.managed_sessions_key is required",
    )
    active_runtime_statuses = board.get("active_runtime_statuses")
    require(
        isinstance(active_runtime_statuses, list) and active_runtime_statuses,
        "board.active_runtime_statuses must be a non-empty list",
    )

    task_flow = config.get("task_flow")
    require(isinstance(task_flow, dict), "config.task_flow must be an object")
    for field in ("workspaceboard_report_cmd", "proof_report_cmd", "active_statuses", "closed_statuses"):
        require(field in task_flow, f"task_flow.{field} is required")
    require(
        isinstance(task_flow.get("workspaceboard_report_cmd"), list) and task_flow["workspaceboard_report_cmd"],
        "task_flow.workspaceboard_report_cmd must be a non-empty list",
    )
    require(
        isinstance(task_flow.get("proof_report_cmd"), list) and task_flow["proof_report_cmd"],
        "task_flow.proof_report_cmd must be a non-empty list",
    )
    require(
        isinstance(task_flow.get("workspaceboard_report_payload"), dict),
        "task_flow.workspaceboard_report_payload must be an object",
    )
    require(isinstance(task_flow.get("active_statuses"), list), "task_flow.active_statuses must be a list")
    require(isinstance(task_flow.get("closed_statuses"), list), "task_flow.closed_statuses must be a list")

    rules = config.get("rules")
    require(isinstance(rules, dict), "config.rules must be an object")
    for key in (
        "flag_scheduler_violations",
        "flag_scheduler_route_candidates",
        "flag_closed_without_closeout_proof",
        "flag_email_report_without_sent_proof",
        "flag_active_missing_board_session",
        "flag_closed_with_live_board_session",
        "flag_proof_report_closeout_issues",
    ):
        require(isinstance(rules.get(key), bool), f"rules.{key} must be boolean")

    return config


def validate_service_parity_config(config: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(config, dict), "config must be an object")
    require(config.get("version") == 1, "config.version must be 1")
    require(isinstance(config.get("python_313"), str) and config["python_313"], "config.python_313 is required")

    report = config.get("report")
    require(isinstance(report, dict), "config.report must be an object")
    require(
        isinstance(report.get("default_markdown"), str) and report["default_markdown"],
        "report.default_markdown is required",
    )
    require(
        isinstance(report.get("default_json"), str) and report["default_json"],
        "report.default_json is required",
    )

    fix_targets = config.get("fix_targets")
    require(isinstance(fix_targets, dict), "config.fix_targets must be an object")
    require(
        isinstance(fix_targets.get("ai_health_plist"), str) and fix_targets["ai_health_plist"],
        "fix_targets.ai_health_plist is required",
    )

    checks = config.get("checks")
    require(isinstance(checks, dict), "config.checks must be an object")
    for mode in ("parity", "deployment"):
        require(isinstance(checks.get(mode), list) and checks[mode], f"checks.{mode} must be a non-empty list")
        for index, item in enumerate(checks[mode]):
            require(isinstance(item, dict), f"checks.{mode}[{index}] must be an object")
            for field in ("group", "label", "mode", "note"):
                require(
                    isinstance(item.get(field), str) and item[field],
                    f"checks.{mode}[{index}].{field} is required",
                )
            require(
                item.get("path") or item.get("command"),
                f"checks.{mode}[{index}] must define path or command",
            )
            require(
                item.get("expected") is not None or item.get("expected_template") is not None,
                f"checks.{mode}[{index}] must define expected or expected_template",
            )
            if item.get("command") is not None:
                require(
                    isinstance(item["command"], list) and item["command"],
                    f"checks.{mode}[{index}].command must be a non-empty list",
                )

    scan_roots = config.get("scan_roots")
    require(isinstance(scan_roots, dict), "config.scan_roots must be an object")
    for field in ("installed_scripts", "koval_plists"):
        require(
            isinstance(scan_roots.get(field), list) and scan_roots[field],
            f"scan_roots.{field} must be a non-empty list",
        )

    return config


def validate_recursive_checker_coverage(config: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(config, dict), "config must be an object")
    require(config.get("version") == 1, "config.version must be 1")
    checkers = config.get("checkers")
    require(isinstance(checkers, list) and checkers, "config.checkers must be a non-empty list")
    for index, checker in enumerate(checkers):
        require(isinstance(checker, dict), f"checkers[{index}] must be an object")
        for field in ("name", "script", "registry", "mode"):
            require(
                isinstance(checker.get(field), str) and checker[field],
                f"checkers[{index}].{field} is required",
            )
        for field in ("covers", "out_of_scope", "verification_commands"):
            values = checker.get(field)
            require(isinstance(values, list) and values, f"checkers[{index}].{field} must be a non-empty list")
            for item_index, value in enumerate(values):
                require(
                    isinstance(value, str) and value.strip(),
                    f"checkers[{index}].{field}[{item_index}] must be a non-empty string",
                )

    return config
