import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('reminders', Path(__file__).resolve().parents[1] / 'scripts/workspaceboard_blocked_reminder_sweep.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class DeliveryTests(TestCase):
    def test_pause_cap_and_failed_or_suppressed_receipts(self):
        with TemporaryDirectory(dir='/Users/werkstatt/tmp') as folder:
            policy=Path(folder)/'policy.json'; log=Path(folder)/'receipts.jsonl'
            now=datetime.now(timezone.utc)
            with patch.object(m,'POLICY_PATH',policy):
                self.assertEqual(m.recipient_delivery_gate(1,log,now),'')
                policy.write_text(json.dumps({'paused_recipient_user_ids':[1]}))
                self.assertEqual(m.recipient_delivery_gate(1,log,now),'defer_recipient_paused')
                self.assertEqual(m.recipient_delivery_gate(3,log,now),'')
                policy.write_text('{}')
                row={'recipient_user_id':1,'logged_at':now.isoformat(),'ok':True}
                log.write_text(json.dumps(dict(row,suppressed=True))+'\n'+json.dumps(dict(row,ok=False))+'\n')
                self.assertEqual(m.recipient_delivery_gate(1,log,now),'')
                with log.open('a') as out: out.write(json.dumps(row)+'\n')
                self.assertEqual(m.recipient_delivery_gate(1,log,now),'defer_recipient_daily_limit')
                self.assertEqual(m.recipient_delivery_gate(3,log,now),'')
                policy.write_text('{broken')
                self.assertEqual(m.recipient_delivery_gate(3,log,now),'defer_delivery_policy_unavailable')
