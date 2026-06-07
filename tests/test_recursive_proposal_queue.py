#!/usr/local/bin/python3.13
"""Regression coverage for recursive proposal queue action selection."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "scripts" / "recursive_proposal_queue.py"


def load_queue_module():
    spec = importlib.util.spec_from_file_location("recursive_proposal_queue", QUEUE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RecursiveProposalQueueActionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.queue = load_queue_module()

    def clean_snapshot(self) -> dict:
        return {
            "registry_ok": True,
            "coverage_ok": True,
            "service_parity_drift": 0,
            "truth_drift_count": 0,
            "proof_issue_count": 0,
            "proof_repair_candidate_count": 0,
            "historical_clean_success": 1,
        }

    def test_source_backed_proof_candidates_are_approval_gated_before_generic_classification(self):
        snapshot = self.clean_snapshot()
        snapshot.update(
            {
                "proof_issue_count": 2,
                "proof_repair_candidate_count": 1,
                "proof_repair_candidates": [
                    {
                        "dedupe_key": "taskflow-example",
                        "proof_kind": "failed_approved_send_artifact",
                    }
                ],
            }
        )

        action, approval_required, risk_class, fix_class, why_now = self.queue.choose_action(snapshot)

        self.assertEqual(action, "review-source-backed-proof-repair-candidates")
        self.assertIs(approval_required, True)
        self.assertEqual(risk_class, "low")
        self.assertEqual(fix_class, "source-backed-proof-repair-candidate")
        self.assertIn("1 source-backed", why_now)

    def test_clean_snapshot_remains_monitor_mode(self):
        action, approval_required, risk_class, fix_class, _ = self.queue.choose_action(self.clean_snapshot())

        self.assertEqual(action, "monitor-recursive-lane")
        self.assertIs(approval_required, False)
        self.assertEqual(risk_class, "low")
        self.assertEqual(fix_class, "no-op-monitoring")

    def test_explicit_zero_proof_issue_count_does_not_fall_back_to_raw_closeout_count(self):
        truth = {
            "proof_issue_count": 0,
            "proof_closeout_issues": 5,
        }

        self.assertEqual(
            self.queue.explicit_int(truth, "proof_issue_count", "proof_closeout_issues"),
            0,
        )


if __name__ == "__main__":
    unittest.main()
