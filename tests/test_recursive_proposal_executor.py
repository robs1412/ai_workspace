#!/usr/local/bin/python3.13
"""Regression coverage for recursive proposal executor authorization."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXECUTOR_PATH = ROOT / "scripts" / "recursive_proposal_executor.py"


def load_executor_module():
    spec = importlib.util.spec_from_file_location("recursive_proposal_executor", EXECUTOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RecursiveProposalExecutorAuthorizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.executor = load_executor_module()

    def test_no_approval_monitor_is_authorized_without_decision(self):
        proposal = {
            "approval_required": False,
            "allowed_fix_class": "no-op-monitoring",
            "decision_state": "",
        }

        self.assertIs(self.executor.execution_authorized(proposal, "no-op-monitoring"), True)

    def test_unapproved_repair_remains_blocked(self):
        proposal = {
            "approval_required": True,
            "allowed_fix_class": "truth-drift-single-item-repair",
            "decision_state": "",
        }

        self.assertIs(self.executor.execution_authorized(proposal, "truth-drift-single-item-repair"), False)

    def test_no_approval_non_monitor_is_not_authorized(self):
        proposal = {
            "approval_required": False,
            "allowed_fix_class": "registry-metadata-fix",
            "decision_state": "",
        }

        self.assertIs(self.executor.execution_authorized(proposal, "registry-metadata-fix"), False)

    def test_no_approval_proof_classification_is_authorized(self):
        proposal = {
            "approval_required": False,
            "allowed_fix_class": "proof-closeout-classification",
            "decision_state": "",
        }

        self.assertIs(self.executor.execution_authorized(proposal, "proof-closeout-classification"), True)

    def test_approved_repair_is_authorized_before_live_mutation_gate(self):
        proposal = {
            "approval_required": True,
            "allowed_fix_class": "source-runtime-parity-fix",
            "decision_state": "approved",
        }

        self.assertIs(self.executor.execution_authorized(proposal, "source-runtime-parity-fix"), True)

    def test_verified_retry_state_requires_keep_ratchet(self):
        self.assertIs(
            self.executor.verified_retry_state(
                {"execution_state": "verified", "ratchet_result": "keep"}
            ),
            True,
        )
        self.assertIs(
            self.executor.verified_retry_state(
                {"execution_state": "verified", "ratchet_result": "revert_required"}
            ),
            False,
        )


if __name__ == "__main__":
    unittest.main()
