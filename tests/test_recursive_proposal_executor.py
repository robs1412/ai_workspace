#!/usr/local/bin/python3.13
"""Regression coverage for recursive proposal executor authorization."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import datetime, timedelta
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

    def approval_contract(self, **overrides):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        expires_at = (datetime.now().astimezone() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S %Z")
        contract = {
            "proposal_id": "recursive-proposal-example",
            "allowed_fix_class": "source-backed-proof-repair-candidate",
            "approved_by": "Robert",
            "approved_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
            "expires_at": expires_at,
            "allowed_action": "review-source-backed-proof-repair-candidates",
            "mutation_surface": "none",
            "external_send_allowed": False,
            "production_mutation_allowed": False,
            "verifier_command": policy.verifier,
            "required_readback": ["candidate detector output"],
        }
        contract.update(overrides)
        return contract

    def approved_contract_proposal(self, contract):
        return {
            "approval_required": True,
            "allowed_fix_class": "source-backed-proof-repair-candidate",
            "decision_state": "approved",
            "approval_contract": contract,
        }

    def test_approval_contract_valid_for_verify_only_candidate_review(self):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        proposal = self.approved_contract_proposal(self.approval_contract())

        result = self.executor.approval_contract_status(
            "recursive-proposal-example",
            proposal,
            policy,
            verify_only=True,
        )

        self.assertTrue(result["ok"])

    def test_approval_contract_missing_blocks_approved_proposal(self):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        proposal = {
            "approval_required": True,
            "allowed_fix_class": "source-backed-proof-repair-candidate",
            "decision_state": "approved",
        }

        result = self.executor.approval_contract_status("recursive-proposal-example", proposal, policy)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "missing_approval_contract")

    def test_approval_contract_expired_blocks_execution(self):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        expired = (datetime.now().astimezone() - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S %Z")
        proposal = self.approved_contract_proposal(self.approval_contract(expires_at=expired))

        result = self.executor.approval_contract_status("recursive-proposal-example", proposal, policy)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "approval_contract_expired")

    def test_approval_contract_verifier_mismatch_blocks_execution(self):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        proposal = self.approved_contract_proposal(self.approval_contract(verifier_command=["/bin/false"]))

        result = self.executor.approval_contract_status("recursive-proposal-example", proposal, policy)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "approval_contract_verifier_mismatch")

    def test_approval_contract_external_send_is_overbroad_for_recursive_executor(self):
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        proposal = self.approved_contract_proposal(self.approval_contract(external_send_allowed=True))

        result = self.executor.approval_contract_status("recursive-proposal-example", proposal, policy)

        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "approval_contract_external_send_overbroad")

    def test_source_backed_proof_candidate_requires_approval_and_has_no_auto_mutator(self):
        proposal = {
            "approval_required": True,
            "allowed_fix_class": "source-backed-proof-repair-candidate",
            "decision_state": "",
        }

        self.assertIs(
            self.executor.execution_authorized(proposal, "source-backed-proof-repair-candidate"),
            False,
        )
        policy = self.executor.FIX_POLICIES["source-backed-proof-repair-candidate"]
        self.assertIs(policy.mutates_live_state, True)
        self.assertIsNone(policy.auto_mutator)
        self.assertIs(self.executor.verifier_only_safe(policy), True)

    def test_status_exposes_verifier_only_metadata(self):
        status = self.executor.execution_statuses()
        source_backed = [
            item
            for item in status["proposals"]
            if item["allowed_fix_class"] == "source-backed-proof-repair-candidate"
        ]

        self.assertTrue(source_backed)
        self.assertIs(source_backed[-1]["requires_approval"], True)
        self.assertIs(source_backed[-1]["verifier_available"], True)
        self.assertIs(source_backed[-1]["verifier_only_safe"], True)

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
