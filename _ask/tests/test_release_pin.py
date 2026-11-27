"""Release pins change only the installer and never move backwards."""

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('pin_release', ROOT / '.github/scripts/pin-release.py')
pin_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pin_release)


class ReleasePinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.readme = Path(self.temp.name) / 'README.md'
        self.original = 'Install:\n  tag="v2.0.3"\nKeep the rest.\n'
        self.readme.write_text(self.original)

    def test_updates_only_the_installer_pin(self):
        pin_release.pin_release(self.readme, 'v2.0.10')
        expected = self.original.replace('v2.0.3', 'v2.0.10')
        self.assertEqual(self.readme.read_text(), expected)
        pin_release.pin_release(self.readme, 'v2.0.10')
        pin_release.pin_release(self.readme, 'v2.0.9')
        self.assertEqual(self.readme.read_text(), expected)

    def test_invalid_tags_leave_the_readme_unchanged(self):
        for tag in ('main', 'v2.0', 'v02.0.4', 'v2.0.4-rc1', 'v2.0.4\nmalicious'):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                pin_release.pin_release(self.readme, tag)
            self.assertEqual(self.readme.read_text(), self.original)

    def test_missing_or_ambiguous_pin_is_rejected(self):
        for text in ('No installer pin\n', self.original * 2):
            self.readme.write_text(text)
            with self.assertRaises(ValueError):
                pin_release.pin_release(self.readme, 'v2.0.4')
            self.assertEqual(self.readme.read_text(), text)


if __name__ == '__main__':
    unittest.main()
