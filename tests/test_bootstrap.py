"""Test download, extraction, argument forwarding, and failure without a network."""

import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chatgpt bootstrap ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.bin = self.home / "bin"
        self.bin.mkdir()
        self.archive = self.home / "fixture.tar.gz"
        with tarfile.open(self.archive, "w:gz") as archive:
            for path, content in {
                "install.sh": '''#!/usr/bin/env bash
python3 -c 'import json,os,sys; from pathlib import Path; Path(os.environ["HOME"],"called.json").write_text(json.dumps(sys.argv[1:]))' "$@"
''',
                "scripts/install-in-container.sh": "# fixture only\n",
                "scripts/enable-ujust-updates.py": "# fixture only\n",
                "keys/openai.asc": "fixture key\n",
            }.items():
                data = content.encode()
                member = tarfile.TarInfo("chatgpt-distrobox-main/" + path)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))
        curl = self.bin / "curl"
        curl.write_text('''#!/usr/bin/env python3
import os,shutil,sys
if os.environ.get("FAIL_DOWNLOAD"):
    sys.exit(22)
shutil.copyfile(os.environ["FIXTURE_ARCHIVE"], sys.argv[sys.argv.index("--output") + 1])
''')
        curl.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home),
                    "PATH": f"{self.bin}:{os.environ['PATH']}",
                    "FIXTURE_ARCHIVE": str(self.archive)}

    def bootstrap(self, *args):
        # Feed it through stdin, matching the published curl | bash command.
        return subprocess.run(["bash", "-s", "--", *args],
                              input=(ROOT / "bootstrap.sh").read_text(),
                              env=self.env, text=True, capture_output=True)

    def test_installs_snapshot_and_forwards_arguments_with_spaces(self):
        args = ["--name", "chatgpt-test", "--enable-ujust-updates", "a b"]
        result = self.bootstrap(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.home / "called.json").read_text()), args)
        base = self.home / ".local/share/chatgpt-distrobox"
        self.assertEqual((base / "keys/openai.asc").read_text(), "fixture key\n")
        self.assertTrue((base / "scripts/enable-ujust-updates.py").exists())
        self.assertEqual(list(base.parent.glob(".chatgpt-distrobox.*")), [])

    def test_download_failure_never_runs_setup_or_replaces_previous_files(self):
        base = self.home / ".local/share/chatgpt-distrobox"
        base.mkdir(parents=True)
        previous = base / "install.sh"
        previous.write_text("previous version")
        self.env["FAIL_DOWNLOAD"] = "1"
        result = self.bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / "called.json").exists())
        self.assertEqual(previous.read_text(), "previous version")
        self.assertEqual(list(base.parent.glob(".chatgpt-distrobox.*")), [])

    def test_invalid_archive_never_runs_setup(self):
        self.archive.write_text("not an archive")
        result = self.bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.home / "called.json").exists())
        self.assertFalse((self.home / ".local/share/chatgpt-distrobox").exists())

    def test_help_does_not_download(self):
        self.env["FAIL_DOWNLOAD"] = "1"
        result = self.bootstrap("--help")
        self.assertEqual(result.returncode, 0)
        self.assertFalse((self.home / ".local").exists())
