import importlib.util
import pathlib
import subprocess
import tempfile
import unittest
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install_workspaceboard_session_context.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ContextTests(unittest.TestCase):
    def test_patch_preserves_source_and_is_idempotent(self):
        base = subprocess.check_output(['git', 'show', 'HEAD:scripts/robertcodex'], cwd=ROOT, text=True)
        result = m.patch_shell(base + '\n# preserve user note\n')
        self.assertIn('# preserve user note', result)
        self.assertEqual(m.patch_shell(result), result)
        self.assertIn('source /Users/werkstatt/ai_workspace/scripts/workspaceboard_session_context.sh', result)
        self.assertIn('WB_HANDOFF_CONTEXT_ARGS', result)

    def test_unrecognized_launcher_fails_before_write(self):
        with self.assertRaises(RuntimeError): m.patch_shell('echo unusual')
        with self.assertRaises(RuntimeError): m.patch_shared('echo unusual')

    def test_shared_adapter_preserves_owner_and_forwards_context(self):
        src = "const OWNER = {};\n'shell_environment_policy.set': OWNER,\nif (/^[0-9a-f-]{36}$/.test(id || '')) lastThreadId = id;\n"
        result = m.patch_shared(src)
        self.assertIn('wbContext.environment(OWNER)', result)
        self.assertIn('wbContext.recordThread(id)', result)
        self.assertEqual(m.patch_shared(result), result)

    def test_shell_arguments_work_with_and_without_context_on_macos_bash(self):
        import json, os, tomllib
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests/workspaceboard') as tmp:
            fake = pathlib.Path(tmp) / 'fake-codex'
            fake.write_text('#!/usr/local/bin/python3.13\nimport sys,json\nprint(json.dumps(sys.argv[1:]))\n')
            fake.chmod(0o700)
            for name in ['robertcodex', 'sonatcodex', 'dmytrocodex']:
                base = subprocess.check_output(['git','show',f'HEAD:scripts/{name}'],cwd=ROOT,text=True)
                script = pathlib.Path(tmp) / name
                script.write_text(m.patch_shell(base).replace('/usr/local/bin/codex', str(fake)))
                for session in ['', '1234567890abcdef']:
                    env = dict(os.environ)
                    for key in ['TMUX','TMUX_PANE','WORKSPACEBOARD_SESSION_ID']: env.pop(key,None)
                    if session: env['WORKSPACEBOARD_SESSION_ID'] = session
                    args = json.loads(subprocess.check_output(['/bin/bash',str(script),'test prompt'],env=env,text=True))
                    values = [a for a in args if a.startswith('shell_environment_policy.set.WORKSPACEBOARD_SESSION_ID=')]
                    self.assertEqual(len(values), int(bool(session)))
                    if values:
                        self.assertEqual(tomllib.loads(values[0])['shell_environment_policy']['set']['WORKSPACEBOARD_SESSION_ID'],session)

    def test_real_isolated_tmux_session_identification(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests/workspaceboard') as tmp:
            socket = str(pathlib.Path(tmp) / 'tmux.sock')
            output = str(pathlib.Path(tmp) / 'context.txt')
            command = f'source {ROOT}/scripts/workspaceboard_session_context.sh; printf "%s" "$WORKSPACEBOARD_SESSION_ID" > "$1"; sleep 1'
            env = dict(__import__('os').environ)
            for key in ['TMUX','TMUX_PANE','WORKSPACEBOARD_SESSION_ID']: env.pop(key, None)
            try:
                subprocess.run(['/usr/local/bin/tmux','-S',socket,'new-session','-d','-s','wb-personal-1234567890abcdef','/bin/bash','-c',command,'test',output],check=True,env=env,capture_output=True)
                for _ in range(40):
                    if pathlib.Path(output).exists(): break
                    time.sleep(.05)
                self.assertEqual(pathlib.Path(output).read_text(), '1234567890abcdef')
            finally:
                subprocess.run(['/usr/local/bin/tmux','-S',socket,'kill-server'],capture_output=True)

if __name__ == '__main__': unittest.main()
