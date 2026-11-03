from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


class ReferenceSavingsTests(unittest.TestCase):
    def test_strict_frozen_aggregate_savings(self):
        root = Path(__file__).resolve().parents[2]
        replay = root / "work/shorter-hashes/benchmark/results/replay-selective.py"
        with tempfile.TemporaryDirectory(prefix="refs-savings-test-") as directory:
            output = Path(directory) / "result"
            result = subprocess.run(
                ["python3", str(replay), "--root", str(root), "--output", str(output)],
                cwd=root, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((output / "report.json").read_text(encoding="utf-8"))

        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["journeys"]), 3)
        self.assertTrue(all(row["equivalent_evidence"] for row in report["journeys"]))
        self.assertLess(report["totals"]["candidate"]["agent_input_tokens"],
                        report["totals"]["baseline"]["agent_input_tokens"])
        self.assertLess(report["totals"]["candidate"]["metadata_bytes"],
                        report["totals"]["baseline"]["metadata_bytes"])


if __name__ == "__main__":
    unittest.main()
