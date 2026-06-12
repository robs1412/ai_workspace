from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path("/Users/werkstatt/ai_workspace/scripts")
MODULE_PATH = SCRIPTS_DIR / "nationaloutreach_mail_cycle.py"


def load_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    sys.modules.setdefault("shared_task_flow", types.ModuleType("shared_task_flow"))
    mailbox_helpers = sys.modules.setdefault("mailbox_imap_helpers", types.ModuleType("mailbox_imap_helpers"))
    mailbox_helpers.email_addresses_from_text = lambda value: {
        part.strip().lower()
        for part in str(value or "").replace(",", " ").split()
        if "@" in part
    }
    email_trace = sys.modules.setdefault("email_trace_recorder", types.ModuleType("email_trace_recorder"))
    email_trace.build_message_record = lambda **values: values
    email_trace.record_event = lambda *args, **kwargs: None
    spec = importlib.util.spec_from_file_location("nationaloutreach_mail_cycle_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pending_action(action_id: str = "vanessa-test-0800") -> dict:
    return {
        "id": action_id,
        "kind": "cot_day_of_event_details",
        "status": "pending",
        "due_at": "2026-06-05T08:00:00-05:00",
        "worker": "Vanessa Sterling",
        "email": {
            "from": "vanessa.sterling@kovaldistillery.com",
            "to": ["test@example.com"],
            "subject": "Your COT event details for Friday, June 5",
            "body": "Test body",
        },
    }


class ScheduledActionLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def run_process(self, state_dir: Path, now_ts: float) -> dict:
        with mock.patch.object(self.module, "scheduled_actions_db_rows", return_value=[]):
            with mock.patch.object(self.module, "scheduled_actions_db_upsert", return_value=True):
                with mock.patch.object(self.module, "mailbox_has_matching_reply", return_value=False):
                    with mock.patch.object(self.module, "shared_task_flow", None):
                        return self.module.process_scheduled_actions({}, state_dir, now_ts=now_ts)

    def test_fresh_lock_skips_without_removing_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            lock_dir = state_dir / "scheduled-actions.lock"
            lock_dir.mkdir()
            (state_dir / "scheduled-actions.jsonl").write_text(json.dumps(pending_action()) + "\n", encoding="utf-8")

            result = self.run_process(state_dir, now_ts=time.time())

            self.assertTrue(result["skipped_locked"])
            self.assertTrue(lock_dir.exists())
            self.assertEqual(read_jsonl(state_dir / "scheduled-actions.jsonl")[0]["status"], "pending")

    def test_stale_lock_recovers_queues_due_row_and_removes_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            lock_dir = state_dir / "scheduled-actions.lock"
            lock_dir.mkdir()
            stale_ts = time.time() - 3600
            os.utime(lock_dir, (stale_ts, stale_ts))
            (state_dir / "scheduled-actions.jsonl").write_text(json.dumps(pending_action()) + "\n", encoding="utf-8")

            result = self.run_process(state_dir, now_ts=time.time())

            self.assertFalse(result["skipped_locked"])
            self.assertTrue(result["stale_lock_recovered"])
            self.assertEqual(result["due"], 1)
            self.assertEqual(result["queued"], 1)
            self.assertFalse(lock_dir.exists())

            rows = read_jsonl(state_dir / "scheduled-actions.jsonl")
            self.assertEqual(rows[0]["status"], "queued")
            self.assertTrue(Path(rows[0]["queued_draft"]).exists())

            log_statuses = [row.get("status") for row in read_jsonl(state_dir / "scheduled-actions-log.jsonl")]
            self.assertIn("stale_lock_recovered", log_statuses)
            self.assertIn("queued", log_statuses)

    def test_repeated_fresh_lock_skip_is_actionable_health(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            lock_dir = state_dir / "scheduled-actions.lock"
            lock_dir.mkdir()
            now = time.time()
            os.utime(lock_dir, (now, now))
            previous = [
                {"logged_at": "2026-06-05T11:00:00-0500", "scheduled_actions_skipped_locked": True},
                {"logged_at": "2026-06-05T11:01:00-0500", "scheduled_actions_skipped_locked": True},
            ]
            (state_dir / "cycle-log.jsonl").write_text(
                "".join(json.dumps(row) + "\n" for row in previous),
                encoding="utf-8",
            )

            result = self.module.scheduled_actions_lock_health(state_dir, True, now_ts=now + 10)

            self.assertEqual(result["skip_streak"], 3)
            self.assertTrue(result["actionable"])
            log_statuses = [row.get("status") for row in read_jsonl(state_dir / "scheduled-actions-log.jsonl")]
            self.assertIn("scheduled_lock_actionable", log_statuses)

    def test_vanessa_to_self_with_real_cc_or_bcc_is_allowed(self) -> None:
        self.module.validate_approved_send_recipients(
            {},
            "vanessa.sterling@kovaldistillery.com",
            ["vanessa.sterling@kovaldistillery.com"],
            ["robert@kovaldistillery.com"],
            [],
        )
        self.module.validate_approved_send_recipients(
            {},
            "vanessa.sterling@kovaldistillery.com",
            ["vanessa.sterling@kovaldistillery.com"],
            [],
            ["team@example.com"],
        )

    def test_vanessa_true_self_only_send_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.module.validate_approved_send_recipients(
                {},
                "vanessa.sterling@kovaldistillery.com",
                ["vanessa.sterling@kovaldistillery.com"],
                [],
                [],
            )

    def test_scheduled_action_draft_gets_canonical_task_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            action = pending_action("vanessa-post-tasting-checkin-2026-06-10-2130")
            action.update(
                {
                    "source_ref": action["id"],
                    "requester": "Robert Birnecker",
                    "owner_lane": "outreach-coordinator",
                    "responsible_worker_or_persona": "Vanessa Sterling",
                    "ops_task_id": 368770,
                    "approval_gates": "Internal scheduled reminder only; no external send beyond Vanessa/Robert.",
                    "verification_readback": "Generated from live staffed Outreach event data.",
                }
            )
            action["email"] = {
                "from": "vanessa.sterling@kovaldistillery.com",
                "to": ["vanessa.sterling@kovaldistillery.com"],
                "cc": ["robert@kovaldistillery.com"],
                "subject": "9:30 PM post-tasting check-in",
                "body": "Check in tonight.",
            }
            canonical_packet = {
                "source_ref": action["id"],
                "dedupe_key": "taskflow-canonical",
                "intake_channel": "scheduled-action:nationaloutreach",
                "owner_lane": "outreach-coordinator",
                "responsible_worker_or_persona": "Vanessa Sterling",
                "ops_portal_or_domain_task": "368770",
                "status": "scheduled",
                "scheduled_action": action["id"],
                "verification_readback": "Generated from live staffed Outreach event data.",
            }
            task_flow = types.SimpleNamespace(
                packet_from_scheduled_action=mock.Mock(return_value=canonical_packet),
                append_event=mock.Mock(),
            )
            with mock.patch.object(self.module, "scheduled_actions_db_rows", return_value=[]):
                with mock.patch.object(self.module, "scheduled_actions_db_upsert", return_value=True):
                    with mock.patch.object(self.module, "mailbox_has_matching_reply", return_value=False):
                        with mock.patch.object(self.module, "shared_task_flow", task_flow):
                            (state_dir / "scheduled-actions.jsonl").write_text(json.dumps(action) + "\n", encoding="utf-8")

                            result = self.module.process_scheduled_actions({}, state_dir, now_ts=time.time())

            self.assertEqual(result["queued"], 1)
            rows = read_jsonl(state_dir / "scheduled-actions.jsonl")
            draft = Path(rows[0]["queued_draft"])
            payload = json.loads(draft.read_text(encoding="utf-8"))
            self.assertEqual(payload["source_ref"], action["id"])
            self.assertEqual(payload["task_packet"]["dedupe_key"], "taskflow-canonical")
            self.assertEqual(payload["task_packet"]["scheduled_action"], action["id"])
            self.assertEqual(payload["task_packet"]["ops_portal_or_domain_task"], "368770")

    def test_send_approved_persists_scheduled_action_closeout_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            outbox = state_dir / "outbox"
            outbox.mkdir()
            action = pending_action("vanessa-post-tasting-checkin-2026-06-10-2130")
            action.update(
                {
                    "status": "queued",
                    "ops_task_id": 368770,
                    "verification_readback": "Generated from live staffed Outreach event data.",
                }
            )
            draft_path = outbox / f"{action['id']}.approved.json"
            draft_path.write_text(json.dumps(action["email"]) + "\n", encoding="utf-8")
            (state_dir / "scheduled-actions.jsonl").write_text(json.dumps(action) + "\n", encoding="utf-8")
            sent_packet = {
                "source_ref": action["id"],
                "dedupe_key": "taskflow-canonical",
                "intake_channel": "scheduled-action:nationaloutreach",
                "owner_lane": "outreach-coordinator",
                "responsible_worker_or_persona": "Vanessa Sterling",
                "ops_portal_or_domain_task": "368770",
                "status": "reported",
                "scheduled_action": action["id"],
                "completion_or_blocker_email": "<sent@example.test>",
                "verification_readback": "Generated from live staffed Outreach event data.",
            }
            send_result = {
                "draft": str(state_dir / "sent" / f"{action['id']}.sent-1.json"),
                "draft_basename": f"{action['id']}.sent-1.json",
                "action_id": action["id"],
                "source_ref": action["id"],
                "from": "vanessa.sterling@kovaldistillery.com",
                "to_count": 1,
                "cc_count": 0,
                "bcc_count": 0,
                "attachment_count": 0,
                "attachment_names": [],
                "subject": "9:30 PM post-tasting check-in",
                "message_id": "<sent@example.test>",
                "sent_folder_appended": True,
                "sent_folder": "Sent",
                "task_packet": sent_packet,
            }
            task_flow = types.SimpleNamespace(append_event=mock.Mock())
            with mock.patch.object(self.module, "scheduled_actions_db_rows", return_value=[]):
                with mock.patch.object(self.module, "scheduled_actions_db_upsert", return_value=True):
                    with mock.patch.object(self.module, "send_one", return_value=send_result):
                        with mock.patch.object(self.module, "record_email_trace"):
                            with mock.patch.object(self.module, "shared_task_flow", task_flow):
                                result = self.module.send_approved({}, state_dir, "vanessa.sterling@kovaldistillery.com")

            self.assertEqual(result["sent"], 1)
            rows = read_jsonl(state_dir / "scheduled-actions.jsonl")
            self.assertEqual(rows[0]["status"], "completed")
            self.assertEqual(rows[0]["sent_message_id"], "<sent@example.test>")
            self.assertEqual(rows[0]["completion_or_blocker_email"], "<sent@example.test>")
            self.assertEqual(rows[0]["verification_readback"], "Generated from live staffed Outreach event data.")
            task_flow.append_event.assert_called_once()
            event_packet = task_flow.append_event.call_args.args[1]
            self.assertEqual(event_packet["status"], "reported")
            self.assertEqual(event_packet["completion_or_blocker_email"], "<sent@example.test>")


if __name__ == "__main__":
    unittest.main()
