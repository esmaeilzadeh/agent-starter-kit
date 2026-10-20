"""Behavioral contract for compact, typed and lossless workflow envelopes."""
from __future__ import annotations

import json
import sys
import unittest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.codec import EnvelopeError, decode_envelope, encode_envelope, normalize_envelope


class ReferenceTests(unittest.TestCase):
    def test_compact_lossless_versioned_envelopes(self):
        payload = {
            "explicit-null": None,
            "empty": [],
            "unicode": "café 🧭",
            "array": [{"id": 2}, {"id": 10}],
        }
        envelope = encode_envelope(payload, "ask-test-plan/v1", {
            "owner": "alpha", "type": "task", "spec": 2, "plan": 1,
        }, {"task": "alpha/spec/2/plan/1/task/3@2"})
        self.assertTrue(envelope, "persisted workflow records need an explicit versioned envelope")
        encoded = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
        self.assertLess(len(encoded), len(json.dumps(envelope, ensure_ascii=False)))
        decoded = decode_envelope(encoded)
        normalized = normalize_envelope(decoded)
        self.assertEqual(normalized["payload"], payload)
        self.assertNotIn("missing-is-absent", normalized["payload"])
        self.assertIn("explicit-null", normalized["payload"])
        self.assertEqual(normalized["payload"]["empty"], [])
        self.assertEqual(normalized["references"]["task"], "alpha/spec/2/plan/1/task/3@2")
        self.assertEqual(envelope["references"]["task"], {"id": 3, "revision": 2})
        with self.assertRaises(EnvelopeError):
            decode_envelope('{"schema":"ask-workflow-envelope/v9"}')
        with self.assertRaises(EnvelopeError):
            decode_envelope('{"schema":"ask-workflow-envelope/v1","schema":"ask-workflow-envelope/v1"}')
        for raw in (
            '{"schema":"ask-workflow-envelope/v1","payload_schema":"x","context":{"owner":"alpha","type":"spec"},"payload":{"value":NaN},"references":{}}',
            '{"schema":"ask-workflow-envelope/v1","payload_schema":"x","context":{"owner":"alpha","type":"spec"},"payload":{"value":Infinity},"references":{}}',
            '{"schema":"ask-workflow-envelope/v1","payload_schema":" ","context":{"owner":"alpha","type":"spec"},"payload":null,"references":{}}',
        ):
            with self.assertRaises(EnvelopeError):
                decode_envelope(raw)
        cross_owner = encode_envelope(payload, "ask-test-plan/v1", {
            "owner": "alpha", "type": "task", "spec": 2, "plan": 1,
        }, {"task": "beta/spec/1/plan/1/task/3@2"})
        self.assertEqual(cross_owner["references"]["task"], "beta/spec/1/plan/1/task/3@2")
        self.assertEqual(normalize_envelope(cross_owner)["references"]["task"],
                         "beta/spec/1/plan/1/task/3@2")

    def test_persisted_producer_roundtrip(self):
        contexts = [
            ({"owner": "alpha", "type": "spec"}, "alpha/spec/2@1"),
            ({"owner": "alpha", "type": "plan", "spec": 2}, "alpha/spec/2/plan/1@1"),
            ({"owner": "alpha", "type": "task", "spec": 2, "plan": 1}, "alpha/spec/2/plan/1/task/4@2"),
            ({"owner": "alpha", "type": "test", "spec": 2, "plan": 1, "task": 4}, "alpha/spec/2/plan/1/task/4/test/3@1"),
        ]
        contexts.extend([
            ({"owner": "alpha", "type": "part", "spec": 2}, "alpha/spec/2/part/6@1"),
            ({"owner": "alpha", "type": "item", "spec": 2, "plan": 1}, "alpha/spec/2/plan/1/item/8@1"),
        ])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            for context, reference in contexts:
                envelope = encode_envelope({"value": None, "notes": "verbatim workflow context"},
                                           "workflow-record/v1", context, {"record": reference})
                encoded = json.dumps(envelope, ensure_ascii=False, separators=(",", ":"))
                path.write_text(encoded, encoding="utf-8")
                # Simulate a separate process loading persisted bytes.
                persisted = path.read_bytes()
                restored = normalize_envelope(decode_envelope(persisted.decode("utf-8")))
                self.assertEqual(restored["references"]["record"], reference)
                self.assertNotIn("sha256", encoded)
                self.assertEqual(restored["payload"], {"value": None, "notes": "verbatim workflow context"})


if __name__ == "__main__":
    unittest.main()
