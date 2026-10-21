#!/usr/local/bin/python3.13
"""User-run local terminal ceremony. Never run this through an agent tool."""
import argparse
import datetime
import getpass
import hmac
import json
import os
from pathlib import Path
import resource
import secrets
import stat
import sys
import tempfile
import termios


class SafeError(Exception):
    pass


def private(path, directory=False):
    info = path.lstat()
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if not expected(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise SafeError('Unsafe ownership or permissions; stopped without revealing anything.')


def save_json(path, data):
    fd, name = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(data, stream, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def terminal_check(private_ssh=False):
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise SafeError('An interactive terminal is required; redirected output is refused.')
    if any(os.environ.get(k) for k in ('TMUX', 'STY')):
        raise SafeError('Exit tmux/screen and use a separate private terminal window.')
    ssh = bool(os.environ.get('SSH_CONNECTION') and os.environ.get('SSH_TTY'))
    if any(os.environ.get(k) for k in ('SSH_CONNECTION', 'SSH_TTY')) and not (ssh and private_ssh):
        raise SafeError('For a direct private SSH terminal, explicitly select --private-ssh.')
    if not ssh and os.environ.get('TERM_PROGRAM') not in ('Apple_Terminal', 'iTerm.app'):
        raise SafeError('This terminal is not recognized as local Apple Terminal or iTerm.')
    if private_ssh and not ssh:
        raise SafeError('--private-ssh requires an interactive SSH connection.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-ssh', action='store_true', help='Use a direct SSH connection from your private terminal app.')
    args = parser.parse_args()
    terminal_check(args.private_ssh)
    if args.private_ssh:
        print('Use a direct SSH connection from your private Terminal app, not Workspaceboard or a browser terminal.', flush=True)
        if input('Type PRIVATE to confirm this terminal is not shared or recording: ').strip() != 'PRIVATE':
            print('Cancelled. No key displayed.')
            return
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    os.umask(0o077)
    config_path = Path(__file__).resolve().parents[2] / 'tmp/recovery-backup-review/disabled-config.json'
    private(config_path)
    config = json.loads(config_path.read_text())
    parent = Path('/Users/werkstatt/.local/recovery-backup')
    if parent.resolve() != parent:
        raise SafeError('Unexpected storage location.')
    vault = parent / 'private'
    vault.mkdir(mode=0o700, exist_ok=True)
    private(vault, directory=True)
    keyfile = vault / 'recovery-key'
    configured = config.get('password_file')
    if configured not in (None, 'NOT_CONFIGURED', str(keyfile)):
        raise SafeError('A different recovery key is configured; stopped to preserve it.')
    if not keyfile.exists() and not keyfile.is_symlink():
        fd = os.open(keyfile, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as stream:
            stream.write(secrets.token_urlsafe(48) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
    private(keyfile)
    key = keyfile.read_text().strip()
    if len(key) != 64 or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in key):
        raise SafeError('Unexpected key format; existing key preserved.')
    print('Pause screen sharing and terminal recording before continuing. This cannot detect every recorder.')
    print('Save in a private password manager independent of this Mac and the backup repositories.')
    if input('Type REVEAL to display the key locally: ').strip() != 'REVEAL':
        print('Cancelled. Backup remains disabled.')
        return
    tty = sys.stdin.fileno()
    previous = termios.tcgetattr(tty)
    try:
        hidden = termios.tcgetattr(tty)
        hidden[3] &= ~termios.ECHO
        termios.tcsetattr(tty, termios.TCSADRAIN, hidden)
        sys.stdout.write('\033[?1049h\033[2J\033[H')
        print('Mac mini recovery backup key — save privately; never paste into chat.\n')
        print(key, flush=True)
        input('\nPress Return after saving to clear this screen. ')
    finally:
        sys.stdout.write('\033[2J\033[H\033[?1049l')
        sys.stdout.flush()
        termios.tcsetattr(tty, termios.TCSADRAIN, previous)
    entered = getpass.getpass('Paste the saved key here to verify (hidden): ')
    if not hmac.compare_digest(entered, key):
        raise SafeError('Verification failed. Key preserved; backup remains disabled.')
    if input('Type SAVED to confirm independent storage: ').strip() != 'SAVED':
        print('No storage confirmation recorded. Backup remains disabled.')
        return
    config['password_file'] = str(keyfile)
    config.setdefault('excluded_paths', [])
    if str(vault) not in config['excluded_paths']:
        config['excluded_paths'].append(str(vault))
    config['key_escrow_verified_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    save_json(config_path, config)
    print('Saved copy verified. No backup started; remaining preflight gates are unchanged.')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled. Existing key preserved.')
        sys.exit(1)
    except SafeError as error:
        print(str(error))
        sys.exit(1)
    except Exception:
        print('Stopped safely. Use a local Mac Terminal with private configuration owned by your account. No key was logged.')
        sys.exit(1)
