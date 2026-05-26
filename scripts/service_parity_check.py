#!/usr/local/bin/python3.13
"""Check source/runtime/deployment parity for local AI service surfaces."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from recursive_registry_core import load_json as load_registry_json
from recursive_registry_core import validate_service_parity_config


DEFAULT_CONFIG_PATH = Path("/Users/werkstatt/ai_workspace/scripts/service_parity_surfaces.json")

CheckStatus = Literal["ok", "drift", "missing-optional", "fixed", "fix-failed"]


@dataclass(frozen=True)
class Check:
    group: str
    label: str
    expected: str
    mode: str
    note: str
    path: str | None = None
    command: tuple[str, ...] | None = None
    optional: bool = False
    fix_id: str | None = None


@dataclass
class Result:
    group: str
    label: str
    status: CheckStatus
    expected: str
    observed: str
    note: str
    path: str | None
    command: list[str] | None
    fix_id: str | None


def load_json(path: Path) -> dict[str, Any]:
    return load_registry_json(path)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    return validate_service_parity_config(config)


def expand_template(template: str, config: dict[str, Any]) -> str:
    return template.format(python_313=config["python_313"])


def build_checks(config: dict[str, Any], mode: str) -> tuple[Check, ...]:
    raw_checks = config["checks"][mode]
    built: list[Check] = []
    for item in raw_checks:
        expected = item.get("expected")
        if expected is None:
            expected = expand_template(str(item["expected_template"]), config)
        built.append(
            Check(
                group=str(item["group"]),
                label=str(item["label"]),
                expected=str(expected),
                mode=str(item["mode"]),
                note=str(item["note"]),
                path=str(item["path"]) if item.get("path") else None,
                command=tuple(str(part) for part in item["command"]) if item.get("command") else None,
                optional=bool(item.get("optional", False)),
                fix_id=str(item["fix_id"]) if item.get("fix_id") else None,
            )
        )
    return tuple(built)


def installed_script_roots(config: dict[str, Any]) -> tuple[Path, ...]:
    return tuple(Path(item) for item in config["scan_roots"]["installed_scripts"])


def koval_plist_roots(config: dict[str, Any]) -> tuple[Path, ...]:
    return tuple(Path(item) for item in config["scan_roots"]["koval_plists"])


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def first_line(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.readline().strip()


def run_command(command: tuple[str, ...]) -> tuple[int, str]:
    proc = subprocess.run(command, capture_output=True, text=True, check=False)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def result_for(check: Check, status: CheckStatus, observed: str) -> Result:
    return Result(
        group=check.group,
        label=check.label,
        status=status,
        expected=check.expected,
        observed=observed,
        note=check.note,
        path=check.path,
        command=list(check.command) if check.command else None,
        fix_id=check.fix_id,
    )


def observe(check: Check) -> Result:
    if check.mode == "command-contains":
        if check.command is None:
            return result_for(check, "drift", "missing command")
        code, output = run_command(check.command)
        if code != 0:
            return result_for(
                check,
                "missing-optional" if check.optional else "drift",
                f"command-exit-{code}",
            )
        return result_for(
            check,
            "ok" if check.expected in output else "drift",
            check.expected if check.expected in output else "expected text not present",
        )

    if check.path is None:
        return result_for(check, "drift", "missing path")

    path = Path(check.path)
    if check.mode == "exists":
        exists = path.exists()
        return result_for(
            check,
            "ok" if exists else ("missing-optional" if check.optional else "drift"),
            "exists" if exists else "missing",
        )

    if not path.exists():
        return result_for(
            check,
            "missing-optional" if check.optional else "drift",
            "missing",
        )

    if check.mode == "line1":
        observed = first_line(path)
        return result_for(check, "ok" if observed == check.expected else "drift", observed)

    if check.mode == "contains":
        body = read_text(path)
        return result_for(
            check,
            "ok" if check.expected in body else "drift",
            check.expected if check.expected in body else "expected text not present",
        )

    return result_for(check, "drift", f"unknown mode {check.mode}")


def synthetic_result(
    *,
    group: str,
    label: str,
    status: CheckStatus,
    expected: str,
    observed: str,
    note: str,
    path: Path | None = None,
) -> Result:
    return Result(
        group=group,
        label=label,
        status=status,
        expected=expected,
        observed=observed,
        note=note,
        path=str(path) if path is not None else None,
        command=None,
        fix_id=None,
    )


def classify_python_runtime(path: Path, python_313: str) -> Result:
    line = first_line(path) if path.exists() else ""
    body = read_text(path)
    if re.search(r'(["\'])python3\1', body) or "/usr/bin/python3" in body:
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed Python script {path.name}",
            status="drift",
            expected=f"#!{python_313} and no internal bare python3 subprocess calls",
            observed="internal python3 call",
            note="Python runtime script still contains an internal drift-prone interpreter call.",
            path=path,
        )
    executable = os.access(path, os.X_OK)
    if line == f"#!{python_313}":
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed Python script {path.name}",
            status="ok",
            expected=f"#!{python_313}",
            observed=line,
            note="Executable Python runtime script is pinned to Python 3.13.",
            path=path,
        )
    if line.startswith("#!") and ("python3" in line or "python " in line):
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed Python script {path.name}",
            status="drift",
            expected=f"#!{python_313}",
            observed=line,
            note="Executable Python runtime script has a drift-prone interpreter pin.",
            path=path,
        )
    if executable:
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed Python script {path.name}",
            status="drift",
            expected=f"#!{python_313}",
            observed=line or "no shebang",
            note="Executable Python runtime script lacks the expected Python 3.13 shebang.",
            path=path,
        )
    return synthetic_result(
        group="installed-script-scan",
        label=f"Installed Python module {path.name}",
        status="ok",
        expected="non-executable module or explicit Python 3.13 shebang",
        observed=line or "no shebang",
        note="Non-executable Python file is treated as module code; caller path owns interpreter selection.",
        path=path,
    )


def classify_shell_runtime(path: Path, python_313: str) -> Result:
    body = read_text(path)
    if "/usr/bin/python3" in body:
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed shell wrapper {path.name}",
            status="drift",
            expected=python_313,
            observed="/usr/bin/python3",
            note="Shell wrapper explicitly calls system Python.",
            path=path,
        )
    if re.search(r"(^|[^\w./-])python3([^\w.-]|$)", body):
        return synthetic_result(
            group="installed-script-scan",
            label=f"Installed shell wrapper {path.name}",
            status="drift",
            expected=python_313,
            observed="bare python3",
            note="Shell wrapper calls unversioned python3.",
            path=path,
        )
    if python_313 in body:
        observed = python_313
        note = "Shell wrapper uses the pinned Python 3.13 path."
    else:
        observed = "no python call"
        note = "Shell wrapper does not directly call Python."
    return synthetic_result(
        group="installed-script-scan",
        label=f"Installed shell wrapper {path.name}",
        status="ok",
        expected=f"{python_313} or no direct Python call",
        observed=observed,
        note=note,
        path=path,
    )


def scan_installed_scripts(config: dict[str, Any]) -> list[Result]:
    results: list[Result] = []
    python_313 = str(config["python_313"])
    for root in installed_script_roots(config):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix == ".py":
                results.append(classify_python_runtime(path, python_313))
            elif path.suffix == ".sh":
                results.append(classify_shell_runtime(path, python_313))
    return results


def classify_plist(path: Path, python_313: str) -> Result:
    body = read_text(path)
    if "/usr/bin/python3" in body:
        return synthetic_result(
            group="installed-plist-scan",
            label=f"KOVAL plist {path.name}",
            status="drift",
            expected=f"{python_313} or no direct Python interpreter",
            observed="/usr/bin/python3",
            note="Launchd plist contains an explicit system Python path.",
            path=path,
        )
    if python_313 in body:
        observed = python_313
        note = "Launchd plist uses the pinned Python 3.13 path."
    else:
        observed = "no direct python interpreter"
        note = "Launchd plist does not directly invoke Python."
    return synthetic_result(
        group="installed-plist-scan",
        label=f"KOVAL plist {path.name}",
        status="ok",
        expected=f"{python_313} or no direct Python interpreter",
        observed=observed,
        note=note,
        path=path,
    )


def scan_koval_plists(config: dict[str, Any]) -> list[Result]:
    results: list[Result] = []
    python_313 = str(config["python_313"])
    for root in koval_plist_roots(config):
        if not root.exists():
            continue
        for path in sorted(root.glob("com.koval*.plist")):
            if path.is_file():
                results.append(classify_plist(path, python_313))
    return results


def fix_ai_health_plist_interpreter(config: dict[str, Any], deployment_checks: tuple[Check, ...]) -> Result:
    python_313 = str(config["python_313"])
    ai_health_plist = Path(config["fix_targets"]["ai_health_plist"])
    check = next(item for item in deployment_checks if item.fix_id == "ai-health-plist-interpreter")
    if not ai_health_plist.exists():
        return result_for(check, "fix-failed", "plist missing")
    body = read_text(ai_health_plist)
    if python_313 in body:
        return result_for(check, "fixed", "already pinned")
    if "/usr/bin/python3" not in body:
        return result_for(check, "fix-failed", "expected /usr/bin/python3 not found")
    updated = body.replace("/usr/bin/python3", python_313, 1)
    try:
        ai_health_plist.write_text(updated, encoding="utf-8")
    except OSError as error:
        return result_for(check, "fix-failed", f"{type(error).__name__}: {error}")
    return result_for(check, "fixed", f"replaced first /usr/bin/python3 with {python_313}")


def fix_python_file_interpreter(path: Path, python_313: str) -> Result:
    label = f"Installed Python script {path.name}"
    if not path.exists():
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=f"#!{python_313}",
            observed="missing",
            note="Cannot patch a missing Python runtime script.",
            path=path,
        )
    original_body = read_text(path)
    lines = original_body.splitlines(keepends=True)
    if not lines:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=f"#!{python_313}",
            observed="empty file",
            note="Cannot patch an empty Python runtime script.",
            path=path,
        )
    current = lines[0].strip()
    changed = False
    if current == f"#!{python_313}":
        changed = False
    elif current.startswith("#!") and "python" in current:
        newline = "\n" if lines[0].endswith("\n") else ""
        lines[0] = f"#!{python_313}{newline}"
        changed = True
    else:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=f"#!{python_313}",
            observed=current or "no shebang",
            note="Refusing to add a new shebang to a Python file without an existing Python shebang.",
            path=path,
        )

    updated_body = "".join(lines)
    updated_body = updated_body.replace('"/usr/bin/python3"', f'"{python_313}"')
    updated_body = updated_body.replace("'/usr/bin/python3'", f"'{python_313}'")
    updated_body = updated_body.replace('"python3"', "sys.executable")
    updated_body = updated_body.replace("'python3'", "sys.executable")
    if "sys.executable" in updated_body and not re.search(r"^import sys$", updated_body, re.M):
        updated_body = re.sub(r"(^import .*$)", r"\1\nimport sys", updated_body, count=1, flags=re.M)
    changed = changed or updated_body != original_body

    if not changed:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fixed",
            expected=f"#!{python_313} and no internal bare python3 calls",
            observed="already pinned",
            note="Python runtime script already uses the pinned interpreter and has no internal bare python3 calls.",
            path=path,
        )
    try:
        path.write_text(updated_body, encoding="utf-8")
    except OSError as error:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=f"#!{python_313}",
            observed=f"{type(error).__name__}: {error}",
            note="File permissions blocked the interpreter patch.",
            path=path,
        )
    return synthetic_result(
        group="installed-script-fix",
        label=label,
        status="fixed",
        expected=f"#!{python_313}",
        observed=f"{current} -> #!{python_313}; internal calls pinned when present",
        note="Patched installed Python runtime script shebang and internal Python calls.",
        path=path,
    )


def fix_shell_file_interpreter(path: Path, python_313: str) -> Result:
    label = f"Installed shell wrapper {path.name}"
    if not path.exists():
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=python_313,
            observed="missing",
            note="Cannot patch a missing shell wrapper.",
            path=path,
        )
    body = read_text(path)
    updated = body.replace("/usr/bin/python3", python_313)
    updated = re.sub(r"(?<![/\w.-])python3(?![\w.-])", python_313, updated)
    if updated == body:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fixed",
            expected=python_313,
            observed="no drift-prone python call found",
            note="Shell wrapper did not need a Python interpreter patch.",
            path=path,
        )
    try:
        path.write_text(updated, encoding="utf-8")
    except OSError as error:
        return synthetic_result(
            group="installed-script-fix",
            label=label,
            status="fix-failed",
            expected=python_313,
            observed=f"{type(error).__name__}: {error}",
            note="File permissions blocked the shell wrapper patch.",
            path=path,
        )
    return synthetic_result(
        group="installed-script-fix",
        label=label,
        status="fixed",
        expected=python_313,
        observed="patched drift-prone python call",
        note="Patched installed shell wrapper Python interpreter calls.",
        path=path,
    )


def fix_installed_script_interpreters(config: dict[str, Any]) -> list[Result]:
    fixes: list[Result] = []
    python_313 = str(config["python_313"])
    for root in installed_script_roots(config):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix == ".py":
                result = classify_python_runtime(path, python_313)
                if result.status == "drift":
                    fixes.append(fix_python_file_interpreter(path, python_313))
            elif path.suffix == ".sh":
                result = classify_shell_runtime(path, python_313)
                if result.status == "drift":
                    fixes.append(fix_shell_file_interpreter(path, python_313))
    return fixes


def selected_checks(mode: str, config: dict[str, Any]) -> tuple[Check, ...]:
    if mode == "parity":
        return build_checks(config, "parity")
    if mode == "deployment":
        return build_checks(config, "deployment")
    return build_checks(config, "parity") + build_checks(config, "deployment")


def selected_scan_results(mode: str, config: dict[str, Any]) -> list[Result]:
    if mode == "installed":
        return scan_installed_scripts(config) + scan_koval_plists(config)
    if mode == "all":
        return scan_installed_scripts(config) + scan_koval_plists(config)
    return []


def build_report(results: list[Result], *, mode: str, fixed: list[Result]) -> str:
    status_counts: dict[str, int] = {}
    for result in results:
        status_counts[result.status] = status_counts.get(result.status, 0) + 1

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# Service Parity Check",
        "",
        f"- Recorded: {now}",
        f"- Mode: `{mode}`",
        "- Scope: source/runtime parity and installed deployment-state checks for local AI service surfaces",
        "",
        "## Totals",
        "",
        f"- Surfaces checked: {len(results)}",
    ]
    for status in ("ok", "drift", "missing-optional", "fixed", "fix-failed"):
        if status_counts.get(status, 0):
            lines.append(f"- {status}: {status_counts[status]}")

    if fixed:
        lines.extend(["", "## Fix Attempts", ""])
        for result in fixed:
            lines.extend(
                [
                    f"- {result.label}: `{result.status}`",
                    f"  - Observed: `{result.observed}`",
                ]
            )

    lines.extend(["", "## Results", ""])
    for result in results:
        lines.extend(
            [
                f"- {result.label}: `{result.status}`",
                f"  - Group: `{result.group}`",
                f"  - Expectation: `{result.expected}`",
                f"  - Observed: `{result.observed}`",
                f"  - Note: {result.note}",
            ]
        )
        if result.path:
            lines.append(f"  - Path: `{result.path}`")
        if result.command:
            lines.append(f"  - Command: `{' '.join(result.command)}`")
        if result.fix_id:
            lines.append(f"  - Fix id: `{result.fix_id}`")

    drift = [result for result in results if result.status == "drift"]
    fix_failed = [result for result in fixed if result.status == "fix-failed"]
    lines.extend(["", "## Recommendation", ""])
    if fix_failed:
        lines.append(
            "- One or more fix attempts failed. Treat the first `fix-failed` result as the exact blocker."
        )
    elif drift:
        lines.append(
            "- Drift remains. Apply only the named, narrow reconcile action for each drifted surface."
        )
    else:
        lines.append(
            "- Checked service surfaces are in parity. Next recursive work should broaden coverage or add a scheduled read-only check."
        )

    return "\n".join(lines) + "\n"


def write_outputs(
    results: list[Result],
    *,
    mode: str,
    fixed: list[Result],
    report_path: Path,
    json_path: Path | None,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(results, mode=mode, fixed=fixed), encoding="utf-8")
    if json_path is not None:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "mode": mode,
            "results": [asdict(result) for result in results],
            "fix_attempts": [asdict(result) for result in fixed],
        }
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Registry-owned service parity surface config.",
    )
    parser.add_argument(
        "--mode",
        choices=("all", "parity", "deployment", "installed"),
        default="all",
        help="Which check set to run.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Markdown report path.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="JSON report path. Pass an empty string to disable.",
    )
    parser.add_argument(
        "--fix-ai-health-interpreter",
        action="store_true",
        help="Replace only the first /usr/bin/python3 in the AI Health system plist with /usr/local/bin/python3.13 when permissions allow.",
    )
    parser.add_argument(
        "--fix-installed-interpreters",
        action="store_true",
        help="Patch writable installed runtime Python shebangs and shell wrapper Python calls to /usr/local/bin/python3.13. Does not edit plists.",
    )
    parser.add_argument(
        "--fail-on-drift",
        action="store_true",
        help="Exit nonzero when drift remains after optional fixes.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = validate_config(load_json(args.config))
    report_path = args.report or Path(config["report"]["default_markdown"])
    json_path = None if args.json == "" else (args.json or Path(config["report"]["default_json"]))
    deployment_checks = build_checks(config, "deployment")
    fixed: list[Result] = []
    if args.fix_ai_health_interpreter:
        fixed.append(fix_ai_health_plist_interpreter(config, deployment_checks))
    if args.fix_installed_interpreters:
        fixed.extend(fix_installed_script_interpreters(config))

    checks = selected_checks(args.mode, config) if args.mode != "installed" else ()
    results = [observe(check) for check in checks]
    results.extend(selected_scan_results(args.mode, config))
    write_outputs(results, mode=args.mode, fixed=fixed, report_path=report_path, json_path=json_path)

    drift_count = sum(1 for result in results if result.status == "drift")
    fix_failed_count = sum(1 for result in fixed if result.status == "fix-failed")
    print(f"report={report_path}")
    if json_path is not None:
        print(f"json={json_path}")
    print(f"surfaces_checked={len(results)}")
    print(f"drift={drift_count}")
    print(f"fix_failed={fix_failed_count}")
    if fix_failed_count:
        return 2
    if args.fail_on_drift and drift_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
