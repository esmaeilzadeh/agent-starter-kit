"""Behavioral contract for immutable integrity catalog publication."""
from __future__ import annotations

import json
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.store import (CatalogError, initialize_catalog, payload_digests,
                                 register_revision, resolve_version)


def make_git_repo(root: Path, content: bytes) -> str:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=root, check=True)
    source = root / "items.json"
    source.write_bytes(content)
    subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "frozen item"], cwd=root, check=True)
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


class ReferenceTests(unittest.TestCase):
    def test_immutable_revision_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"id":"SH-01","then":["original"]}\n'
            commit = make_git_repo(root, payload)
            subprocess.run(["git", "update-ref", "refs/ask/accepted-tests/alpha", commit],
                           cwd=root, check=True)
            catalog = root / "work/alpha/references/integrity.json"
            initialize_catalog(catalog, "alpha")
            accepted_before = subprocess.check_output(
                ["git", "rev-parse", "refs/ask/accepted-tests/alpha"], cwd=root, text=True
            ).strip()
            first = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": commit, "path": "items.json",
            }, "SH-01", "structured-item/1", payload, expected_generation=0)
            next_payload = b'{"id":"SH-01","then":["next"]}\n'
            (root / "items.json").write_bytes(next_payload)
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "next item"], cwd=root, check=True)
            next_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
            second = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": next_commit, "path": "items.json",
            }, "SH-01", "structured-item/1", next_payload, expected_generation=1)
            self.assertIsNotNone(first, "a committed catalog entry must be returned")
            self.assertEqual(first["reference"], "alpha/spec/1@1")
            self.assertEqual(second["reference"], "alpha/spec/1@2")
            self.assertEqual(resolve_version(catalog, first["reference"], root)["payload"], payload)
            self.assertEqual(resolve_version(catalog, first["reference"], root)["entry"], first)
            with self.assertRaises(CatalogError):
                register_revision(catalog, "alpha", "alpha/spec/1", {
                    "commit": commit, "path": "items.json",
                }, "SH-01", "structured-item/1", b'{"id":"SH-01","then":["mutated"]}\n',
                   expected_generation=2, revision=1)
            doc = json.loads(catalog.read_text())
            self.assertEqual(doc["schema"], "ask-reference-catalog/v1")
            self.assertEqual(len(doc["entries"]), 2)
            self.assertEqual(doc["entries"][0]["reference"], "alpha/spec/1@1")
            accepted_after = subprocess.check_output(
                ["git", "rev-parse", "refs/ask/accepted-tests/alpha"], cwd=root, text=True
            ).strip()
            self.assertEqual(accepted_after, accepted_before, "catalog publication must not change accepted-tests authority")

    def test_canonical_and_byte_digest_semantics(self):
        left = b'{"id":"SH-01","value":[1,2]}\n'
        right = b'{\n  "value": [1, 2], "id": "SH-01"\n}\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            commit = make_git_repo(root, left)
            catalog = root / "integrity.json"
            initialize_catalog(catalog, "alpha")
            entry = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": commit, "path": "items.json",
            }, "SH-01", "structured-item/1", left)
            self.assertIsNotNone(entry, "integrity publication must return its immutable revision")
            resolved = resolve_version(catalog, entry["reference"], root)
            self.assertIn("digests", resolved, "resolution must verify declared digest semantics")
            alternative = payload_digests(right)
            self.assertEqual(resolved["digests"]["canonical-json/1"], alternative["canonical-json/1"])
            self.assertNotEqual(resolved["digests"]["exact-bytes/1"], alternative["exact-bytes/1"])
            with self.assertRaises(CatalogError):
                payload_digests(right, semantics="display-only")

    def test_concurrent_and_interrupted_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"id":"SH-01"}\n'
            commit = make_git_repo(root, payload)
            catalog = root / "integrity.json"
            initialize_catalog(catalog, "alpha")
            barrier = threading.Barrier(2)
            results = []

            def publish():
                barrier.wait()
                try:
                    results.append(register_revision(catalog, "alpha", "alpha/spec/1", {
                        "commit": commit, "path": "items.json",
                    }, "SH-01", "structured-item/1", payload, expected_generation=0))
                except CatalogError as exc:
                    results.append(exc)

            workers = [threading.Thread(target=publish) for _ in range(2)]
            for worker in workers: worker.start()
            for worker in workers: worker.join()
            self.assertEqual(sum(isinstance(value, dict) for value in results), 1)
            self.assertEqual(sum(isinstance(value, CatalogError) for value in results), 1)
            from workflow_refs import store
            original_git = store._git

            def stop_before_ref(root_arg, *args, **kwargs):
                if args and args[0] == "update-ref":
                    raise CatalogError("interrupted", "before authority advancement")
                return original_git(root_arg, *args, **kwargs)

            with patch("workflow_refs.store._git", side_effect=stop_before_ref):
                with self.assertRaises(CatalogError):
                    register_revision(catalog, "alpha", "alpha/spec/2", {
                        "commit": commit, "path": "items.json",
                    }, "SH-02", "structured-item/1", payload)
            recovered_before = register_revision(catalog, "alpha", "alpha/spec/2", {
                "commit": commit, "path": "items.json",
            }, "SH-02", "structured-item/1", payload)
            self.assertEqual(recovered_before["reference"], "alpha/spec/2@1")

            original_atomic_bytes = store._atomic_bytes

            def stop_after_ref(path, raw):
                if Path(path) == catalog:
                    raise RuntimeError("after authority advancement")
                return original_atomic_bytes(path, raw)

            with patch("workflow_refs.store._atomic_bytes", side_effect=stop_after_ref):
                with self.assertRaises(RuntimeError):
                    register_revision(catalog, "alpha", "alpha/spec/3", {
                        "commit": commit, "path": "items.json",
                    }, "SH-03", "structured-item/1", payload)
            recovered = register_revision(catalog, "alpha", "alpha/spec/3", {
                "commit": commit, "path": "items.json",
            }, "SH-03", "structured-item/1", payload)
            self.assertEqual(recovered["reference"], "alpha/spec/3@1")
            self.assertEqual(resolve_version(catalog, recovered["reference"], root)["payload"], payload)

    def test_history_and_missing_integrity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"id":"SH-01","then":["kept"]}\n'
            commit = make_git_repo(root, payload)
            catalog = root / "integrity.json"
            initialize_catalog(catalog, "alpha")
            entry = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": commit, "path": "items.json",
            }, "SH-01", "structured-item/1", payload)
            self.assertIsNotNone(entry, "history must be published before it is resolved")
            resolved = resolve_version(catalog, entry["reference"], root)
            self.assertIn("payload", resolved, "historical source bytes must resolve")
            self.assertEqual(resolved["payload"], payload)
            with self.assertRaises(CatalogError):
                resolve_version(catalog, "alpha/spec/1@9", root)
            doc = json.loads(catalog.read_text())
            doc["entries"][0]["snapshot"]["path"] = "missing.json"
            catalog.write_text(json.dumps(doc))
            with self.assertRaises(CatalogError):
                resolve_version(catalog, entry["reference"], root)


if __name__ == "__main__":
    unittest.main()
