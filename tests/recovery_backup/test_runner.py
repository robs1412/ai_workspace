import hashlib, importlib.util, json, os, sqlite3, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/recovery_backup'))
import runner
from inventory import inventory

class Safety(unittest.TestCase):
 def test_execution_disabled(self):
  for action in ['run','init','check','retention-preview']:
   with self.assertRaises(runner.BackupError):runner.gate({'execution_enabled':False},action,True)
   with self.assertRaises(runner.BackupError):runner.gate({'execution_enabled':True},action,False)
  runner.gate({},'estimate',False)
 def test_inventory_no_follow_and_exclusions(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   p=Path(td);(p/'data').write_bytes(b'a'*12);(p/'loop').symlink_to(p)
   (p/'node_modules').mkdir();(p/'node_modules/x').write_bytes(b'b'*24)
   r=inventory([{'path':td,'label':'fixture'}],['node_modules'])
   self.assertEqual(r['total_logical_bytes'],12);self.assertEqual(r['sources'][0]['symlinks'],1)
   self.assertEqual(r['sources'][0]['excluded_logical_bytes'],24)
 def test_sqlite_committed_wal(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   p=Path(td);src=p/'source.db';conn=sqlite3.connect(src);conn.execute('PRAGMA journal_mode=WAL');conn.execute('CREATE TABLE t(x)');conn.execute('INSERT INTO t VALUES (42)');conn.commit()
   runner.sqlite_copy(src,p/'target.db')
   with sqlite3.connect(p/'target.db') as dest:self.assertEqual(dest.execute('SELECT x FROM t').fetchone()[0],42)
   conn.close()
 def test_private_material_requires_private_mode(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   p=Path(td)/'test-key';p.write_text('synthetic');p.chmod(0o644)
   with self.assertRaises(runner.BackupError):runner.private_file(p)
 def test_no_plaintext_child_error(self):
  with patch('runner.shutil.which',return_value='/fixture'),patch('runner.child_env',return_value={}),patch('runner.subprocess.run',return_value=subprocess.CompletedProcess([],3,'sensitive','private')):
   with self.assertRaisesRegex(runner.BackupError,'code 3'):runner.restic({}, {'repository':'fixture'},['backup'])
 def test_database_lock_not_implicit(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   with self.assertRaisesRegex(runner.BackupError,'write locks'):runner.stage_data({'database_exports':[{'requires_write_lock':True}]},Path(td),False)
 def test_overlap_rejected(self):
  with self.assertRaisesRegex(runner.BackupError,'Overlapping'):
   runner.validate({'sources':[{'path':'/a'},{'path':'/a/b'}],'destinations':[{'repository':'r1','label':'a'},{'repository':'r2','label':'b'}],'staging_root':'/z'})

 def test_database_export_is_gzip_and_exact(self):
  import gzip
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   out=Path(td)/'export.sql.gz'
   runner.export_database({'argv':[sys.executable,'-c','print("SELECT 42;")']},out,0)
   self.assertEqual(gzip.decompress(out.read_bytes()),b'SELECT 42;\n')
 def test_database_export_failure_is_not_success(self):
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   with self.assertRaises(runner.BackupError):
    runner.export_database({'argv':[sys.executable,'-c','raise SystemExit(2)']},Path(td)/'bad.sql.gz',0)
 def test_unresolved_activation_blockers(self):
  with self.assertRaisesRegex(runner.BackupError,'Activation blockers'):
   runner.gate({'execution_enabled':True,'activation_blockers':['fixture']},'run',True)

class Integration(unittest.TestCase):
 def test_two_independent_encrypted_repositories_and_restore(self):
  binary=ROOT/'tmp/recovery-backup-review/restic'
  if not binary.exists():self.skipTest('local fixture restic not installed')
  with tempfile.TemporaryDirectory(dir=ROOT/'tmp') as td:
   p=Path(td);src=p/'source';src.mkdir();(src/'data.txt').write_text('synthetic restoration proof')
   with sqlite3.connect(src/'state.db') as db:db.execute('CREATE TABLE t(x)');db.execute('INSERT INTO t VALUES(7)')
   key=p/'synthetic-key';key.write_text('fixture-only-password');key.chmod(0o600)
   config={'execution_enabled':True,'sources':[{'path':str(src),'label':'fixture'}], 'staging_root':str(p/'stage'),
    'password_file':str(key),'restic_binary':str(binary),'require_database_exports':False,'minimum_local_free_bytes':0,
    'destinations':[{'label':'local-test','repository':str(p/'r1')},{'label':'cloud-test','repository':str(p/'r2')}]}
   for d in config['destinations']:runner.restic(config,d,['init'])
   receipt=runner.run_backup(config);self.assertEqual(receipt['status'],'verified_both')
   for d,r in zip(config['destinations'],receipt['destinations']):
    target=p/('full-'+d['label']);runner.restic(config,d,['restore',r['snapshot_id'],'--target',str(target)])
    self.assertEqual((target/src.relative_to(src.anchor)/'data.txt').read_text(),'synthetic restoration proof')
    maps=list(target.rglob('sqlite-restore-map.json'));self.assertEqual(len(maps),1)
    entry=json.loads(maps[0].read_text())[0]
    with sqlite3.connect(maps[0].parent/entry['snapshot']) as db:self.assertEqual(db.execute('SELECT x FROM t').fetchone()[0],7)
   self.assertFalse(any((p/'stage').rglob('*.sql')))
   # A failure of destination two must not claim redundancy, and must preserve first snapshot proof.
   real=runner.restic
   def fail_second(c,d,args):
    if d['label']=='cloud-test' and 'backup' in args:raise runner.BackupError('synthetic failure')
    return real(c,d,args)
   with patch('runner.restic',side_effect=fail_second):partial=runner.run_backup(config)
   self.assertEqual(partial['status'],'incomplete');self.assertEqual(partial['destinations'][0]['status'],'verified')
if __name__=='__main__':unittest.main()
