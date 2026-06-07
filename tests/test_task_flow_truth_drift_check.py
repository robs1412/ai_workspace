#!/usr/local/bin/python3.13
"""Regression coverage for Task Flow truth-drift proof issue classification."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
CHECKER_PATH = SCRIPT_DIR / "task_flow_truth_drift_check.py"


def load_checker_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("task_flow_truth_drift_check", CHECKER_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TaskFlowTruthDriftProofIssueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_checker_module()

    def test_blocked_email_required_with_marker_is_not_missing_blocker_issue(self):
        proof_report = {
            "items": [
                {
                    "severity": "blocked",
                    "status": "blocked",
                    "effective_status": "blocked",
                    "blocked_resolution_state": "blocker_email_required",
                    "dedupe_key": "taskflow-example",
                    "completion_or_blocker_email": "<message-id@example.test>",
                }
            ]
        }

        self.assertEqual(self.checker.classify_proof_issues(proof_report), [])

    def test_blocked_email_required_without_marker_remains_issue(self):
        proof_report = {
            "items": [
                {
                    "severity": "blocked",
                    "status": "blocked",
                    "effective_status": "blocked",
                    "blocked_resolution_state": "blocker_email_required",
                    "dedupe_key": "taskflow-example",
                }
            ]
        }

        issues = self.checker.classify_proof_issues(proof_report)
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].kind, "blocked_missing_blocker_email")


if __name__ == "__main__":
    unittest.main()
