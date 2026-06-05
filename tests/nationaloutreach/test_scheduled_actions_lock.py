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
    sys.modules.setdefault("mailbox_imap_helpers", types.ModuleType("mailbox_imap_helpers"))
    sys.modules.setdefault("email_trace_recorder", types.ModuleType("email_trace_recorder"))
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


if __name__ == "__main__":
    unittest.main()
