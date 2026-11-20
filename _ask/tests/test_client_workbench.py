"""Workbench startup must choose its listener address explicitly."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ask-workbench-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.kit_root = self.root / 'kit'
        self.ui = self.kit_root / '_ask/scripts/ui.sh'
        self.ui.parent.mkdir(parents=True)
        shutil.copy2(ROOT / '_ask/scripts/ui.sh', self.ui)
        app = self.kit_root / '_ask/ui/streamlit_app.py'
        app.parent.mkdir(parents=True)
        app.write_text('import streamlit as st\nst.write("ok")\n', encoding='utf-8')
        self.capture = self.root / 'argv.json'
        self.fake_python = self.root / 'python'
        self.fake_python.write_text(
            '#!/usr/bin/env python3\n'
            'import json, os, sys\n'
            'if sys.argv[1:] == ["-m", "streamlit", "--version"]:\n'
            '    print("Streamlit, version 1.59.2")\n'
            'else:\n'
            '    with open(os.environ["CAPTURE_ARGV"], "w") as output:\n'
            '        json.dump(sys.argv[1:], output)\n',
            encoding='utf-8',
        )
        self.fake_python.chmod(0o755)

    def env(self, **values):
        env = {key: value for key, value in os.environ.items()
               if key not in {'STREAMLIT_SERVER_ADDRESS', 'ASK_PYTHON', 'CAPTURE_ARGV'}}
        env.update(HOME=str(self.root / 'home'), XDG_CONFIG_HOME=str(self.root / 'config'),
                   ASK_PYTHON=str(self.fake_python), CAPTURE_ARGV=str(self.capture))
        env.update(values)
        return env

    def run_fake(self, *args, **env_values):
        return subprocess.run(['bash', str(self.ui), *args], cwd=self.root, env=self.env(**env_values),
                              text=True, capture_output=True)

    def test_address_precedence(self):
        project_config = self.root / '.streamlit'
        project_config.mkdir()
        (project_config / 'config.toml').write_text(
            '[server]\naddress = "0.0.0.0"\n', encoding='utf-8')

        default = self.run_fake('--server.port=8765', '--browser.gatherUsageStats=false',
                                STREAMLIT_SERVER_ADDRESS='0.0.0.0')
        self.assertEqual(default.returncode, 0, default.stderr)
        argv = json.loads(self.capture.read_text(encoding='utf-8'))
        self.assertEqual(argv, [
            '-m', 'streamlit', 'run', str(self.kit_root / '_ask/ui/streamlit_app.py'),
            '--server.address=127.0.0.1', '--server.port=8765',
            '--browser.gatherUsageStats=false',
        ])

        for address_args in (('--server.address=192.0.2.8',),
                             ('--server.address', '192.0.2.8')):
            self.capture.unlink()
            result = self.run_fake(*address_args, '--server.port=8765')
            self.assertEqual(result.returncode, 0, result.stderr)
            argv = json.loads(self.capture.read_text(encoding='utf-8'))
            self.assertEqual(argv.count('--server.address=192.0.2.8'), 1)
            self.assertNotIn('--server.address=127.0.0.1', argv)
            self.assertIn('--server.port=8765', argv)

        self.capture.unlink()
        result = self.run_fake('--', '--server.address=192.0.2.8', 'app value')
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(self.capture.read_text(encoding='utf-8'))
        self.assertEqual(argv, [
            '-m', 'streamlit', 'run', str(self.kit_root / '_ask/ui/streamlit_app.py'),
            '--server.address=127.0.0.1', '--', '--server.address=192.0.2.8', 'app value',
        ])

        self.capture.unlink()
        result = self.run_fake('--server.address=192.0.2.8', '--',
                               '--server.address=127.0.0.1')
        self.assertEqual(result.returncode, 0, result.stderr)
        argv = json.loads(self.capture.read_text(encoding='utf-8'))
        self.assertEqual(argv[-3:], ['--server.address=192.0.2.8', '--',
                                     '--server.address=127.0.0.1'])

        for invalid in (
            ('--server.address',),
            ('--server.address', '--server.port=8765'),
            ('--server.address=',),
            ('--server.address=bad address',),
            ('--server.address=192.0.2.8', '--server.address=127.0.0.1'),
            ('--server.address=192.0.2.8', '--server.address', '127.0.0.1'),
        ):
            self.capture.unlink(missing_ok=True)
            result = self.run_fake(*invalid)
            self.assertNotEqual(result.returncode, 0, f'accepted {invalid!r}')
            self.assertFalse(self.capture.exists(), f'launched with {invalid!r}')

    @staticmethod
    def listener_inodes(pid):
        inodes = set()
        try:
            descriptors = list(Path(f'/proc/{pid}/fd').iterdir())
        except OSError:
            return inodes
        for fd in descriptors:
            try:
                target = os.readlink(fd)
            except FileNotFoundError:
                continue
            match = re.fullmatch(r'socket:\[(\d+)\]', target)
            if match:
                inodes.add(match.group(1))
        return inodes

    def wait_for_listener(self, process, port, expected_address):
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                self.fail(f'UI exited before listening ({process.returncode}): {stdout}\n{stderr}')
            inodes = self.listener_inodes(process.pid)
            for table in ('tcp', 'tcp6'):
                try:
                    lines = Path(f'/proc/{process.pid}/net/{table}').read_text().splitlines()[1:]
                except OSError:
                    continue
                for line in lines:
                    fields = line.split()
                    address, state, inode = fields[1], fields[3], fields[9]
                    address_hex, port_hex = address.split(':')
                    if inode not in inodes or state != '0A' or int(port_hex, 16) != port:
                        continue
                    packed = bytes.fromhex(address_hex)
                    observed = socket.inet_ntop(socket.AF_INET if table == 'tcp' else socket.AF_INET6,
                                                packed[::-1] if table == 'tcp' else packed)
                    if observed != expected_address:
                        self.fail(f'UI listener bound to {observed}:{port}; expected {expected_address}')
                    return
            time.sleep(.1)
        self.fail(f'UI did not listen on {expected_address}:{port}')

    def start_real_ui(self, address, port, ambient_address, *app_args):
        project_config = self.root / '.streamlit'
        project_config.mkdir(exist_ok=True)
        (project_config / 'config.toml').write_text(
            f'[server]\naddress = "{ambient_address}"\n', encoding='utf-8')
        env = {key: value for key, value in os.environ.items()
               if key not in {'ASK_PYTHON', 'STREAMLIT_SERVER_ADDRESS'}}
        env.update(HOME=str(self.root / 'home'), XDG_CONFIG_HOME=str(self.root / 'config'),
                   PYTHONUSERBASE=str(Path.home() / '.local'),
                   STREAMLIT_SERVER_ADDRESS=ambient_address)
        args = ['bash', str(self.ui), f'--server.port={port}', '--server.headless=true']
        if address is not None:
            args.append(f'--server.address={address}')
        args.extend(app_args)
        process = subprocess.Popen(args, cwd=self.root, env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop_process, process)
        return process

    @staticmethod
    def stop_process(process):
        if process.poll() is None:
            process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()

    def wait_for_health(self, port):
        deadline = time.monotonic() + 25
        last_error = None
        while time.monotonic() < deadline:
            try:
                with urlopen(f'http://127.0.0.1:{port}/_stcore/health', timeout=1) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read(), b'ok')
                    return
            except Exception as exc:
                last_error = exc
                time.sleep(.1)
        self.fail(f'Streamlit health endpoint did not respond: {last_error}')

    def test_actual_listener(self):
        self.assertTrue(Path('/proc/self/fd').exists(), 'listener assertion requires Linux /proc')
        for address, expected, ambient, app_args in (
                (None, '127.0.0.1', '0.0.0.0', ('--', '--server.address=0.0.0.0')),
                ('0.0.0.0', '0.0.0.0', '127.0.0.1',
                 ('--', '--server.address=127.0.0.1'))):
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            process = self.start_real_ui(address, port, ambient, *app_args)
            self.wait_for_listener(process, port, expected)
            self.wait_for_health(port)
            self.stop_process(process)


if __name__ == '__main__':
    unittest.main()
