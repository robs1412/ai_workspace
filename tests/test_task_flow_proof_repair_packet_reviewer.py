#!/usr/local/bin/python3.13
"""Regression coverage for Task Flow proof-repair packet review decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "task_flow_proof_repair_packet_reviewer.py"


def load_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("task_flow_proof_repair_packet_reviewer", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def packet_payload() -> dict:
    return {
        "dedupe_key": "taskflow-example",
        "proof_kind": "failed_approved_send_artifact",
        "status": "needs_approval",
        "subject": "Example",
        "proposed_action": "review_failed_send_artifact_then_retry_or_block",
        "approval": {
            "required": True,
            "external_send_allowed": False,
            "production_mutation_allowed": False,
        },
        "verification": {
            "required_after_action": [
                "sent Message-ID or explicit no-send blocker proof",
                "Task Flow row readback showing truthful state",
            ],
        },
    }


class TaskFlowProofRepairPacketReviewerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.reviewer = load_module()

    def test_approved_packet_records_contract_without_executing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_dir.mkdir()
            decision_log = Path(temp_dir) / "decisions.jsonl"
            packet_path = packet_dir / "taskflow-example.failed_approved_send_artifact.json"
            packet_path.write_text(json.dumps(packet_payload()), encoding="utf-8")

            rc = self.reviewer.main(
                [
                    "--packet-dir",
                    str(packet_dir),
                    "--decision-log",
                    str(decision_log),
                    "record",
                    "--packet",
                    "taskflow-example",
                    "--decision",
                    "approved",
                    "--approved-by",
                    "Robert",
                    "--source-ref",
                    "task-mode-chat",
                    "--external-send-allowed",
                    "--allowed-sender-path",
                    "nationaloutreach-approved-sender",
                ]
            )

            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            events = [json.loads(line) for line in decision_log.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(rc, 0)
        self.assertEqual(packet["status"], "approved")
        self.assertEqual(packet["approval_contract"]["approved_by"], "Robert")
        self.assertTrue(packet["approval_contract"]["external_send_allowed"])
        self.assertFalse(packet["approval_contract"]["production_mutation_allowed"])
        self.assertEqual(packet["approval_contract"]["allowed_mutation_surface"], "none")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["decision"], "approved")

    def test_external_send_approval_requires_allowed_sender_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_dir.mkdir()
            packet_path = packet_dir / "taskflow-example.failed_approved_send_artifact.json"
            packet_path.write_text(json.dumps(packet_payload()), encoding="utf-8")

            with self.assertRaises(SystemExit) as cm:
                self.reviewer.main(
                    [
                        "--packet-dir",
                        str(packet_dir),
                        "record",
                        "--packet",
                        "taskflow-example",
                        "--decision",
                        "approved",
                        "--approved-by",
                        "Robert",
                        "--external-send-allowed",
                    ]
                )

        self.assertIn("--allowed-sender-path", str(cm.exception))

    def test_blocked_decision_requires_notes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_dir.mkdir()
            packet_path = packet_dir / "taskflow-example.failed_approved_send_artifact.json"
            packet_path.write_text(json.dumps(packet_payload()), encoding="utf-8")

            with self.assertRaises(SystemExit) as cm:
                self.reviewer.main(
                    [
                        "--packet-dir",
                        str(packet_dir),
                        "record",
                        "--packet",
                        "taskflow-example",
                        "--decision",
                        "blocked",
                    ]
                )

        self.assertIn("--notes is required", str(cm.exception))

    def test_verify_marks_packet_unresolved_when_candidate_still_matches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_dir.mkdir()
            decision_log = Path(temp_dir) / "decisions.jsonl"
            candidate_json = Path(temp_dir) / "candidates.json"
            packet_path = packet_dir / "taskflow-example.failed_approved_send_artifact.json"
            packet_path.write_text(json.dumps(packet_payload()), encoding="utf-8")
            candidate_json.write_text(
                json.dumps(
                    {
                        "generated_at": "2026-06-09 09:30:00 CDT",
                        "candidate_count": 1,
                        "candidates": [
                            {
                                "dedupe_key": "taskflow-example",
                                "proof_kind": "failed_approved_send_artifact",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            rc = self.reviewer.main(
                [
                    "--packet-dir",
                    str(packet_dir),
                    "--decision-log",
                    str(decision_log),
                    "verify",
                    "--packet",
                    "taskflow-example",
                    "--candidate-json",
                    str(candidate_json),
                    "--no-refresh-candidates",
                ]
            )

            packet = json.loads(packet_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(packet["post_action_verification"]["state"], "unresolved")
        self.assertFalse(packet["post_action_verification"]["required_readback_met"])

    def test_verify_marks_packet_resolved_when_candidate_no_longer_matches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_dir.mkdir()
            decision_log = Path(temp_dir) / "decisions.jsonl"
            candidate_json = Path(temp_dir) / "candidates.json"
            packet_path = packet_dir / "taskflow-example.failed_approved_send_artifact.json"
            packet_path.write_text(json.dumps(packet_payload()), encoding="utf-8")
            candidate_json.write_text(
                json.dumps({"generated_at": "2026-06-09 09:30:00 CDT", "candidate_count": 0, "candidates": []}),
                encoding="utf-8",
            )

            rc = self.reviewer.main(
                [
                    "--packet-dir",
                    str(packet_dir),
                    "--decision-log",
                    str(decision_log),
                    "verify",
                    "--packet",
                    "taskflow-example",
                    "--candidate-json",
                    str(candidate_json),
                    "--no-refresh-candidates",
                ]
            )

            packet = json.loads(packet_path.read_text(encoding="utf-8"))

        self.assertEqual(rc, 0)
        self.assertEqual(packet["post_action_verification"]["state"], "resolved")
        self.assertTrue(packet["post_action_verification"]["required_readback_met"])


if __name__ == "__main__":
    unittest.main()
