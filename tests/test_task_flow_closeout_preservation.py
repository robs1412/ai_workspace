"""A stale monitor must not reopen a verified filed/no-action record."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CloseoutPreservationTest(unittest.TestCase):
    def test_verified_closeouts_survive_weaker_monitor_events(self):
        source = (ROOT / 'scripts/task_flow_mysql_recorder.php').read_text()
        # Load the actual function definitions without invoking the CLI or a live DB.
        definitions = source.split("\n$command = $argv[1] ?? '';", 1)[0]
        harness = r'''
class FixtureStatement extends PDOStatement {
    public function __construct(private array $row) {}
    public function execute(?array $params = null): bool { return true; }
    public function fetch(int $mode = PDO::FETCH_DEFAULT, int $orientation = PDO::FETCH_ORI_NEXT, int $offset = 0): mixed { return $this->row; }
}
class FixturePDO extends PDO {
    public function __construct(private array $row) {}
    public function prepare(string $query, array $options = []): PDOStatement|false { return new FixtureStatement($this->row); }
}
$base = ['status'=>'no_action_closed','verification_readback'=>'Historical check verified; canonical recurring OPS task retained','completion_or_blocker_email'=>'','clarification_email'=>'','next_update'=>'','workspaceboard_session'=>''];
$incoming=['status'=>'blocked','verification_readback'=>'already-reported','completion_or_blocker_email'=>''];
$out=[];
$out['filed_monitor']=task_flow_should_preserve_existing_packet(new FixturePDO($base),'same-source',$incoming,'frank_previous_message_reconciled');
$closed=$base;$closed['status']='closed_with_proof';
$out['closed_monitor']=task_flow_should_preserve_existing_packet(new FixturePDO($closed),'same-source',$incoming,'avignon_previous_message_reconciled');
$unverified=$base;$unverified['verification_readback']='';
$out['unverified']=task_flow_should_preserve_existing_packet(new FixturePDO($unverified),'same-source',$incoming,'frank_previous_message_reconciled');
$newProof=$incoming;$newProof['completion_or_blocker_email']='<new-evidence@example.test>';
$out['new_evidence']=task_flow_should_preserve_existing_packet(new FixturePDO($base),'same-source',$newProof,'owner_reopened');
$reopened=$incoming;$reopened['status']='reopened';
$out['explicit_reopen']=task_flow_should_preserve_existing_packet(new FixturePDO($base),'same-source',$reopened,'owner_reopened');
echo json_encode($out);
'''
        with tempfile.TemporaryDirectory(dir=ROOT / 'tmp') as tmp:
            path = Path(tmp) / 'preserve.php'
            path.write_text(definitions + '\n' + harness)
            result = subprocess.run(['php', str(path)], text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout), {
            'filed_monitor': True, 'closed_monitor': True, 'unverified': False,
            'new_evidence': False, 'explicit_reopen': False,
        })


if __name__ == '__main__':
    unittest.main()
