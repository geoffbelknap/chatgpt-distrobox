import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/enable-ujust-updates.py"
spec = importlib.util.spec_from_file_location("updates", SCRIPT)
updates = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updates)


class UpdateConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = Path(self.temp.name) / "config.json"

    def test_preserves_other_settings_and_exact_backup(self):
        original = '{"modules":{"distrobox":{"disable":true,"binary-path":"/custom/dbx"},"flatpak":{"disable":true}},"checks":{"hardware":{"enable":false}}}\n'
        self.config.write_text(original)
        self.config.chmod(0o640)
        backup = updates.enable(self.config)
        self.assertEqual(backup.read_text(), original)
        expected = json.loads(original)
        expected["modules"]["distrobox"]["disable"] = False
        self.assertEqual(json.loads(self.config.read_text()), expected)
        self.assertEqual(self.config.stat().st_mode & 0o777, 0o640)

    def test_repeat_run_does_not_change_file_or_create_backup(self):
        self.config.write_text('{"modules":{"distrobox":{"disable":false}}}')
        before = self.config.stat().st_mtime_ns
        self.assertIsNone(updates.enable(self.config))
        self.assertEqual(self.config.stat().st_mtime_ns, before)
        self.assertEqual(list(self.config.parent.glob("*.backup-*")), [])

    def test_absent_module_is_enabled(self):
        self.config.write_text('{"modules":{"system":{"disable":false}}}')
        updates.enable(self.config)
        result = json.loads(self.config.read_text())
        self.assertEqual(result["modules"]["system"], {"disable": False})
        self.assertEqual(result["modules"]["distrobox"], {"disable": False})

    def test_invalid_input_is_untouched(self):
        for original in ("not json", '[]', '{"modules":null}', '{"modules":{"distrobox":[]}}'):
            with self.subTest(original=original):
                self.config.write_text(original)
                with self.assertRaises((ValueError, AttributeError, TypeError)):
                    updates.enable(self.config)
                self.assertEqual(self.config.read_text(), original)
                self.assertEqual(list(self.config.parent.glob("*.backup-*")), [])

    def test_symlink_is_rejected(self):
        target = self.config.with_name("target.json")
        target.write_text("{}")
        self.config.symlink_to(target)
        with self.assertRaises(ValueError):
            updates.enable(self.config)
        self.assertEqual(target.read_text(), "{}")
