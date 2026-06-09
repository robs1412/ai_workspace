#!/usr/local/bin/python3.13
"""Regression coverage for read-only Task Flow proof repair candidates."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "task_flow_proof_repair_candidates.py"


def load_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("task_flow_proof_repair_candidates", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TaskFlowProofRepairCandidatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = load_module()

    def test_failed_approved_send_artifact_candidate_uses_task_packet_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            failed_dir = Path(temp_dir)
            artifact = failed_dir / "example.failed-123.json"
            artifact.write_text(
                json.dumps(
                    {
                        "subject": "Cancellation instructions",
                        "body": "body must not be copied",
                        "task_packet": {
                            "owner_lane": "outreach-coordinator",
                            "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
                            "ops_portal_or_domain_task": "OPS Outreach event 1054",
                            "next_update": "Review failed draft.",
                        },
                    }
                ),
                encoding="utf-8",
            )
            rows = [
                {
                    "dedupe_key": "taskflow-example",
                    "intake_channel": "approved-send:nationaloutreach",
                    "status": "blocked",
                    "source_ref": "example.failed-123.json",
                    "missing_fields": ["owner_lane", "ops_portal_or_domain_task"],
                }
            ]

            candidates = self.detector.find_failed_artifact_candidates(rows, failed_dir)

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.proof_kind, "failed_approved_send_artifact")
        self.assertEqual(candidate.owner_lane, "outreach-coordinator")
        self.assertEqual(candidate.ops_portal_or_domain_task, "OPS Outreach event 1054")
        self.assertIn("no sent Message-ID", candidate.completion_or_blocker_email)
        self.assertNotIn("body must not be copied", candidate.verification_readback)

    def test_avignon_timeout_candidate_uses_matching_event_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            events = Path(temp_dir) / "task-flow-events.jsonl"
            events.write_text(
                json.dumps(
                    {
                        "logged_at": "2026-06-07T12:34:54-0500",
                        "event": "avignon_message_action",
                        "action": {
                            "dedupe_key": "avignon-direct-owner-sonat-example",
                            "classification": "direct-owner-route-local-retry",
                            "subject": "Follow up",
                            "decision": "direct-owner-route-blocked-local-no-email",
                            "current_state": "captured_route_blocked_local_retry",
                            "route_blocker": "timed out",
                            "archived": False,
                            "completion_target": "visible-worker-completion-or-blocker",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rows = [
                {
                    "dedupe_key": "avignon-direct-owner-sonat-example",
                    "source_ref": "<message@example.test>",
                    "intake_channel": "email:avignon",
                    "owner_lane": "sonat",
                    "responsible_worker_or_persona": "avignon",
                    "status": "blocked",
                    "approval_gates": "previously-logged-direct-owner-pending",
                    "verification_readback": "not-pending",
                    "source_links": "Follow up",
                    "missing_fields": ["completion_or_blocker_email", "ops_portal_or_domain_task"],
                }
            ]

            candidates = self.detector.find_avignon_timeout_candidates(rows, events)

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.proof_kind, "avignon_route_timeout_blocker")
        self.assertEqual(candidate.ops_portal_or_domain_task, "avignon-direct-owner-sonat-example")
        self.assertIn("timed out", candidate.completion_or_blocker_email)
        self.assertIn("archived False", candidate.verification_readback)

    def test_already_proven_avignon_row_is_not_reproposed(self):
        rows = [
            {
                "dedupe_key": "avignon-direct-owner-sonat-example",
                "intake_channel": "email:avignon",
                "owner_lane": "sonat",
                "responsible_worker_or_persona": "avignon",
                "ops_portal_or_domain_task": "avignon-direct-owner-sonat-example",
                "status": "blocked",
                "approval_gates": "previously-logged-direct-owner-pending",
                "verification_readback": "not-pending",
                "completion_or_blocker_email": "Blocked locally: already proven.",
                "missing_fields": [],
            }
        ]

        self.assertEqual(self.detector.find_avignon_timeout_candidates(rows, Path("/missing")), [])

    def test_unreadable_failed_artifact_is_skipped(self):
        class UnreadablePath:
            def exists(self):
                raise PermissionError("permission denied")

        candidate = self.detector.build_failed_artifact_candidate({}, UnreadablePath())

        self.assertIsNone(candidate)

    def test_recorder_non_json_output_reports_bounded_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            recorder = Path(temp_dir) / "recorder.php"
            recorder.write_text(
                "<?php echo 'System is currently unavailable. FATAL: DNS failed'; ?>",
                encoding="utf-8",
            )

            with self.assertRaises(RuntimeError) as cm:
                self.detector.run_recorder_report(recorder, 1)

        self.assertIn("recorder returned non-JSON output", str(cm.exception))
        self.assertIn("System is currently unavailable", str(cm.exception))

    def test_write_repair_packets_preserves_existing_review_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            packet_dir = Path(temp_dir) / "packets"
            packet_index = Path(temp_dir) / "packet-index.json"
            packet_report = Path(temp_dir) / "packet-report.md"
            candidate = self.detector.RepairCandidate(
                dedupe_key="taskflow-example",
                intake_channel="approved-send:nationaloutreach",
                status="blocked",
                proof_kind="failed_approved_send_artifact",
                source_path="/tmp/example.failed-123.json",
                source_event="failed_send_artifact",
                source_logged_at="",
                subject="Example",
                owner_lane="outreach-coordinator",
                responsible_worker_or_persona="worker@example.test",
                ops_portal_or_domain_task="OPS Outreach event 1054",
                completion_or_blocker_email="Failed artifact exists.",
                verification_readback="metadata readback",
                next_update="Review failed draft.",
                confidence="source-backed",
            )
            packet_dir.mkdir()
            existing_path = self.detector.packet_path(packet_dir, candidate)
            existing_path.write_text(
                json.dumps(
                    {
                        "dedupe_key": "taskflow-example",
                        "proof_kind": "failed_approved_send_artifact",
                        "status": "blocked",
                        "approval": {
                            "required": True,
                            "external_send_allowed": False,
                            "production_mutation_allowed": False,
                        },
                        "review": {
                            "decision": "blocked",
                            "notes": "Need exact owner approval.",
                        },
                        "post_action_verification": {
                            "state": "unresolved",
                            "required_readback_met": False,
                        },
                    }
                ),
                encoding="utf-8",
            )

            index = self.detector.write_repair_packets([candidate], packet_dir, packet_index, packet_report)
            packet = json.loads(existing_path.read_text(encoding="utf-8"))

        self.assertEqual(packet["status"], "blocked")
        self.assertEqual(packet["review"]["decision"], "blocked")
        self.assertEqual(packet["post_action_verification"]["state"], "unresolved")
        self.assertEqual(index["packets"][0]["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
