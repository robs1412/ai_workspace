#!/usr/local/bin/python3.13
"""Regression coverage for recursive daily run gating."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "recursive_daily_run.py"


def load_module():
    spec = importlib.util.spec_from_file_location("recursive_daily_run", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RecursiveDailyRunGatingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runner = load_module()

    def test_monitor_proposal_auto_executes(self):
        proposal = {
            "recommended_action": "monitor-recursive-lane",
            "approval_required": False,
            "allowed_fix_class": "no-op-monitoring",
        }

        self.assertIs(self.runner.should_auto_execute(proposal), True)

    def test_source_backed_candidate_does_not_auto_execute(self):
        proposal = {
            "recommended_action": "review-source-backed-proof-repair-candidates",
            "approval_required": True,
            "allowed_fix_class": "source-backed-proof-repair-candidate",
        }

        self.assertIs(self.runner.should_auto_execute(proposal), False)

    def test_no_approval_non_monitor_does_not_auto_execute(self):
        proposal = {
            "recommended_action": "classify-proof-closeout-issues",
            "approval_required": False,
            "allowed_fix_class": "proof-closeout-classification",
        }

        self.assertIs(self.runner.should_auto_execute(proposal), False)

    def test_bare_json_flag_uses_default_artifact_path(self):
        args = self.runner.parse_args(["--json"])

        self.assertEqual(args.json, self.runner.DEFAULT_JSON)
        self.assertIs(args.print_json, False)

    def test_json_flag_still_accepts_custom_artifact_path(self):
        custom_path = ROOT / "tmp" / "recursive-daily-run-test.json"

        args = self.runner.parse_args(["--json", str(custom_path)])

        self.assertEqual(args.json, custom_path)


if __name__ == "__main__":
    unittest.main()
