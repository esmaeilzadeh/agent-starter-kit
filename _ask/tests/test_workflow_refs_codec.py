"""Behavioral contract for compact, typed and lossless workflow envelopes."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.codec import EnvelopeError, decode_envelope, encode_envelope, normalize_envelope


class ReferenceTests(unittest.TestCase):
    def test_compact_lossless_versioned_envelopes(self):
        payload = {
            "missing-is-absent": None,
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
        self.assertIn("explicit-null", normalized["payload"])
        self.assertEqual(normalized["payload"]["empty"], [])
        self.assertEqual(normalized["references"]["task"], "alpha/spec/2/plan/1/task/3@2")
        self.assertEqual(envelope["references"]["task"], {"id": 3, "revision": 2})
        with self.assertRaises(EnvelopeError):
            decode_envelope('{"schema":"ask-workflow-envelope/v9"}')
        with self.assertRaises(EnvelopeError):
            decode_envelope('{"schema":"ask-workflow-envelope/v1","schema":"ask-workflow-envelope/v1"}')
        with self.assertRaises(EnvelopeError):
            encode_envelope(payload, "ask-test-plan/v1", {"owner": "alpha", "type": "task"},
                            {"task": "beta/spec/1/plan/1/task/3@2"})

    def test_persisted_producer_roundtrip(self):
        contexts = [
            ({"owner": "alpha", "type": "spec"}, "alpha/spec/2@1"),
            ({"owner": "alpha", "type": "plan", "spec": 2}, "alpha/spec/2/plan/1@1"),
            ({"owner": "alpha", "type": "task", "spec": 2, "plan": 1}, "alpha/spec/2/plan/1/task/4@2"),
            ({"owner": "alpha", "type": "test", "spec": 2, "plan": 1, "task": 4}, "alpha/spec/2/plan/1/task/4/test/3@1"),
        ]
        for context, reference in contexts:
            envelope = encode_envelope({"value": None, "notes": "verbatim workflow context"},
                                       "workflow-record/v1", context, {"record": reference})
            self.assertTrue(envelope, "each producer must emit a versioned record")
            restored = normalize_envelope(decode_envelope(envelope))
            self.assertEqual(restored["references"]["record"], reference)
            self.assertNotIn("sha256", json.dumps(envelope))
            self.assertEqual(restored["payload"], {"value": None, "notes": "verbatim workflow context"})


if __name__ == "__main__":
    unittest.main()
