#!/usr/local/bin/python3.13
"""Validate recursive checker registry files without touching live surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from recursive_registry_core import load_json
from recursive_registry_core import validate_recursive_checker_coverage
from recursive_registry_core import validate_service_parity_config
from recursive_registry_core import validate_task_flow_truth_config


BASE = Path(__file__).resolve().parent
DEFAULT_TASK_FLOW_CONFIG = BASE / "task_flow_truth_surfaces.json"
DEFAULT_SERVICE_PARITY_CONFIG = BASE / "service_parity_surfaces.json"
DEFAULT_COVERAGE_CONFIG = BASE / "recursive_checker_coverage.json"
def lint_task_flow(config_path: Path) -> dict:
    config = validate_task_flow_truth_config(load_json(config_path))
    return {
        "name": "task_flow_truth_surfaces",
        "path": str(config_path),
        "status": "ok",
        "version": config.get("version"),
        "checks": {
            "board_url": config["board"]["status_url"],
            "workspaceboard_report_cmd": config["task_flow"]["workspaceboard_report_cmd"],
            "proof_report_cmd": config["task_flow"]["proof_report_cmd"],
        },
    }


def lint_service_parity(config_path: Path) -> dict:
    config = validate_service_parity_config(load_json(config_path))
    return {
        "name": "service_parity_surfaces",
        "path": str(config_path),
        "status": "ok",
        "version": config.get("version"),
        "checks": {
            "python_313": config["python_313"],
            "parity_checks": len(config["checks"]["parity"]),
            "deployment_checks": len(config["checks"]["deployment"]),
            "installed_roots": len(config["scan_roots"]["installed_scripts"]),
            "plist_roots": len(config["scan_roots"]["koval_plists"]),
        },
    }


def lint_coverage(config_path: Path) -> dict:
    config = validate_recursive_checker_coverage(load_json(config_path))
    return {
        "name": "recursive_checker_coverage",
        "path": str(config_path),
        "status": "ok",
        "version": config.get("version"),
        "checks": {
            "checker_count": len(config["checkers"]),
            "checker_names": [checker["name"] for checker in config["checkers"]],
        },
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-flow-config", type=Path, default=DEFAULT_TASK_FLOW_CONFIG)
    parser.add_argument("--service-parity-config", type=Path, default=DEFAULT_SERVICE_PARITY_CONFIG)
    parser.add_argument("--coverage-config", type=Path, default=DEFAULT_COVERAGE_CONFIG)
    parser.add_argument("--json", action="store_true", help="emit JSON instead of plain text")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    results = [
        lint_task_flow(args.task_flow_config),
        lint_service_parity(args.service_parity_config),
        lint_coverage(args.coverage_config),
    ]
    if args.json:
        print(json.dumps({"ok": True, "results": results}, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"{result['name']}: ok")
            print(f"  path={result['path']}")
        print("recursive_registry_lint: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
