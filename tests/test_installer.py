"""Exercise the installer with fake Distrobox; never create real containers."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chatgpt installer ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.log = self.directory / "calls.jsonl"
        fake = self.directory / "distrobox"
        fake.write_text('''#!/usr/bin/env python3
import json, os, sys
with open(os.environ["CALL_LOG"], "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
if sys.argv[1] == "list":
    print(os.environ.get("CONTAINER_LIST", "ID | NAME | STATUS | IMAGE"))
    sys.exit(int(os.environ.get("LIST_EXIT", "0")))
if sys.argv[1] == "create":
    sys.exit(int(os.environ.get("CREATE_EXIT", "0")))
if sys.argv[1] == "enter":
    assert "localpkg_gpgcheck=1" in sys.stdin.read()
    sys.exit(int(os.environ.get("ENTER_EXIT", "0")))
''')
        fake.chmod(0o755)
        self.env = {**os.environ, "PATH": f"{self.directory}:{os.environ['PATH']}",
                    "CALL_LOG": str(self.log)}

    def run_installer(self, *args):
        return subprocess.run(["bash", str(ROOT / "install.sh"), *args],
                              env=self.env, text=True, capture_output=True)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_new_container_gets_official_image_and_key(self):
        result = self.run_installer("--name", "chatgpt-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.calls()
        self.assertEqual(calls[1], ["create", "--yes", "--name", "chatgpt-test",
                                  "--image", "registry.fedoraproject.org/fedora-toolbox:44"])
        self.assertEqual(calls[2], ["enter", "--name", "chatgpt-test", "--", "bash",
                                  "-s", "--", str(ROOT / "keys/openai.asc")])

    def test_existing_container_is_never_recreated(self):
        self.env["CONTAINER_LIST"] = "ID | NAME | STATUS | IMAGE\n123 | chatgpt | Up | fedora"
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([call[0] for call in self.calls()], ["list", "enter"])

    def test_list_failure_does_not_create_a_container(self):
        self.env["LIST_EXIT"] = "1"
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call[0] for call in self.calls()], ["list"])

    def test_create_failure_stops_installation(self):
        self.env["CREATE_EXIT"] = "1"
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([call[0] for call in self.calls()], ["list", "create"])

    def test_container_failure_does_not_report_success(self):
        self.env["ENTER_EXIT"] = "1"
        result = self.run_installer()
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Installed.", result.stdout)

    def test_option_like_and_shell_container_names_are_rejected(self):
        for name in ("--root", "chatgpt;touch unexpected", "", "a/b"):
            with self.subTest(name=name):
                self.assertEqual(self.run_installer("--name", name).returncode, 2)
        self.assertFalse(self.log.exists())

    def test_help_needs_no_container_access(self):
        self.assertEqual(self.run_installer("--help").returncode, 0)
        self.assertFalse(self.log.exists())
