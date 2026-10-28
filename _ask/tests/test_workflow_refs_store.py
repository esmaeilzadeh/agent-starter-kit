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
            payload = b'{"items":[{"id":"SH-01","then":["original"]}]}\n'
            commit = make_git_repo(root, payload)
            subprocess.run(["git", "update-ref", "refs/ask/accepted-tests/alpha", commit],
                           cwd=root, check=True)
            catalog = root / "work/alpha/references/integrity.json"
            initialize_catalog(catalog, "alpha")
            accepted_before = subprocess.check_output(
                ["git", "rev-parse", "refs/ask/accepted-tests/alpha"], cwd=root, text=True
            ).strip()
            for invalid in (commit[:39], "a" * 41, "a" * 63):
                with self.assertRaises(CatalogError):
                    register_revision(catalog, "alpha", "alpha/spec/1", {
                        "commit": invalid, "path": "items.json",
                    }, "SH-01", "structured-item/1", payload)
            # Length alone is not enough for SHA-256 repositories: a 40 digit
            # prefix is abbreviated there, though it is a full SHA-1 ID.
            sha256_root = root / "sha256"
            sha256_root.mkdir()
            init = subprocess.run(["git", "init", "-q", "--object-format=sha256"], cwd=sha256_root,
                                  capture_output=True)
            if init.returncode == 0:
                subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=sha256_root, check=True)
                subprocess.run(["git", "config", "user.name", "Test"], cwd=sha256_root, check=True)
                (sha256_root / "items.json").write_bytes(payload)
                subprocess.run(["git", "add", "items.json"], cwd=sha256_root, check=True)
                subprocess.run(["git", "commit", "-qm", "sha256 source"], cwd=sha256_root, check=True)
                sha256_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=sha256_root, text=True).strip()
                sha256_catalog = sha256_root / "integrity.json"
                initialize_catalog(sha256_catalog, "alpha")
                with self.assertRaises(CatalogError):
                    register_revision(sha256_catalog, "alpha", "alpha/spec/1", {
                        "commit": sha256_commit[:40], "path": "items.json",
                    }, "SH-01", "structured-item/1", payload)
            first = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": commit, "path": "items.json",
            }, "SH-01", "structured-item/1", payload, expected_generation=0)
            subprocess.run(["git", "commit", "--allow-empty", "-qm", "unrelated source commit"],
                           cwd=root, check=True)
            unrelated_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            repeated = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": unrelated_commit, "path": "items.json",
            }, "SH-01", "structured-item/1", payload, expected_generation=1)
            self.assertEqual(repeated, first, "an unrelated Git commit must not publish a new item revision")
            next_payload = b'{"items":[{"id":"SH-01","then":["next"]}]}\n'
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
            (root / "items.json").write_bytes(payload)
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "restore prior item content"], cwd=root, check=True)
            restored_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            third = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": restored_commit, "path": "items.json",
            }, "SH-01", "structured-item/1", payload, expected_generation=2)
            self.assertEqual(third["reference"], "alpha/spec/1@3",
                             "restoring old content after a later revision must keep history append-only")
            with self.assertRaises(CatalogError):
                register_revision(catalog, "alpha", "alpha/spec/1", {
                    "commit": next_commit, "path": "items.json",
                }, "SH-01", "structured-item/1", next_payload,
                   expected_generation=3, revision=1)
            run = register_revision(catalog, "alpha", "alpha/run/1", {
                "commit": next_commit, "path": "items.json",
            }, "run-1", "run-evidence/1", next_payload, expected_generation=3)
            self.assertEqual(run["reference"], "alpha/run/1@1")
            doc = json.loads(catalog.read_text())
            self.assertEqual(doc["schema"], "ask-reference-catalog/v1")
            self.assertEqual(len(doc["entries"]), 4)
            self.assertEqual(len(doc.get("snapshots", {})), 3)
            snapshot_ids = [entry.get("snapshot_id") for entry in doc["entries"]]
            self.assertEqual(snapshot_ids[1], snapshot_ids[3], "repeated immutable source snapshots must be shared")
            self.assertEqual([entry["reference"] for entry in doc["entries"][:2]],
                             ["alpha/spec/1@1", "alpha/spec/1@2"],
                             "adding run evidence must preserve contract history")
            self.assertNotIn("snapshot", doc["entries"][0], "entries must refer to the shared snapshot table")
            self.assertEqual(doc["entries"][0]["reference"], "alpha/spec/1@1")
            accepted_after = subprocess.check_output(
                ["git", "rev-parse", "refs/ask/accepted-tests/alpha"], cwd=root, text=True
            ).strip()
            self.assertEqual(accepted_after, accepted_before, "catalog publication must not change accepted-tests authority")

            def publish_x(source, message):
                (root / "items.json").write_bytes(source)
                subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
                subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True)
                source_commit = subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=root, text=True
                ).strip()
                generation = json.loads(catalog.read_text())["generation"]
                return register_revision(catalog, "alpha", "alpha/spec/2", {
                    "commit": source_commit, "path": "items.json",
                }, "x", "structured-item/1", source,
                   expected_generation=generation)

            first_items = b'{"items":[{"id":"x","value":1,"extra":{"k":"v"}},{"id":"y","value":1}]}\n'
            item_x = publish_x(first_items, "register x and sibling y")
            whitespace_only = b'{\n  "items": [ {"extra":{"k":"v"}, "value":1, "id":"x"}, {"value":1,"id":"y"} ]\n}\n'
            same_x = publish_x(whitespace_only, "reformat items without changing x")
            with self.subTest(change="whitespace and object key order"):
                self.assertEqual(same_x["reference"], item_x["reference"])
            sibling_only = b'{"items":[{"id":"x","value":1,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            unchanged_x = publish_x(sibling_only, "change sibling y only")
            with self.subTest(change="sibling item only"):
                self.assertEqual(unchanged_x["reference"], item_x["reference"])
            changed_x = b'{"items":[{"id":"x","value":2,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            next_x = publish_x(changed_x, "change x content")
            self.assertEqual(next_x["reference"], "alpha/spec/2@2",
                             "a meaningful change to x must append an item revision")
            boolean_x = b'{"items":[{"id":"x","value":true,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            bool_revision = publish_x(boolean_x, "change x value to boolean")
            numeric_x = b'{"items":[{"id":"x","value":1,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            number_revision = publish_x(numeric_x, "change x value to number")
            self.assertNotEqual(bool_revision["reference"], number_revision["reference"],
                                "JSON true and number 1 have distinct item meanings")
            close_decimal_a = b'{"items":[{"id":"x","value":1.0000000000000000000000000000000001,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            first_decimal = publish_x(close_decimal_a, "change x to close decimal a")
            close_decimal_b = b'{"items":[{"id":"x","value":1.0000000000000000000000000000000002,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            second_decimal = publish_x(close_decimal_b, "change x to close decimal b")
            self.assertNotEqual(first_decimal["reference"], second_decimal["reference"],
                                "distinct JSON decimals must not collapse through binary float parsing")
            zero = b'{"items":[{"id":"x","value":0,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            zero_revision = publish_x(zero, "change x value to zero")
            zero_with_scale = b'{"items":[{"id":"x","value":0.00,"extra":{"k":"v"}},{"id":"y","value":2}]}\n'
            scaled_zero_revision = publish_x(zero_with_scale, "reformat zero value")
            with self.subTest(change="zero exponent"):
                self.assertEqual(zero_revision["reference"], scaled_zero_revision["reference"],
                                 "zero values with different decimal exponents are numerically equal")
            nested = 1
            for _ in range(500):
                nested = {"child": nested}
            deep_item = {"id": "x", "value": nested, "extra": {"k": "v"}}
            deep_source = json.dumps({"items": [deep_item, {"id": "y", "value": 2}]},
                                     separators=(",", ":")).encode() + b"\n"
            try:
                publish_x(deep_source, "publish too-deep structured item")
            except CatalogError as exc:
                self.assertEqual(exc.code, "comparison_incomplete")
            except Exception as exc:
                self.fail(f"deep item comparison must refuse as incomplete, not raise {type(exc).__name__}: {exc}")
            else:
                self.fail("deep item comparison must refuse as incomplete instead of publishing a revision")

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
            external_bytes = payload_digests(b"\xff exact log bytes", semantics="exact-bytes/1")
            self.assertEqual(set(external_bytes), {"exact-bytes/1"})
            with self.assertRaises(CatalogError):
                payload_digests(right, semantics="display-only")

    def test_concurrent_and_interrupted_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"items":[{"id":"SH-01"}]}\n'
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
            with self.assertRaises(CatalogError):
                resolve_version(catalog, "alpha/spec/2@1", root)
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
            # A reader at the authority-advanced cut must recover the exact
            # committed catalog bytes and observe one complete new entry.
            observed = resolve_version(catalog, "alpha/spec/3@1", root)
            self.assertEqual(observed["payload"], payload)
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
            # Current checkout bytes diverge; exact pinned history still wins.
            (root / "items.json").write_bytes(b'{"id":"SH-01","then":["checkout"]}\n')
            self.assertEqual(resolve_version(catalog, entry["reference"], root)["payload"], payload)
            with self.assertRaises(CatalogError):
                resolve_version(catalog, "alpha/spec/1@9", root)
            # A registered off-HEAD source stays reachable through the trusted
            # catalog even after reflogs are expired and unreachable objects pruned.
            external_payload = b'{"id":"SH-02","then":["external"]}\n'
            blob = subprocess.check_output(["git", "hash-object", "-w", "--stdin"],
                                           cwd=root, input=external_payload, text=False).decode().strip()
            tree = subprocess.check_output(["git", "mktree"], cwd=root,
                                          input=f"100644 blob {blob}\titems.json\n", text=True).strip()
            external_commit = subprocess.check_output(["git", "commit-tree", tree, "-m", "external pinned source"],
                                                      cwd=root, text=True).strip()
            subprocess.run(["git", "update-ref", "refs/heads/pinned-source", external_commit], cwd=root, check=True)
            external_entry = register_revision(catalog, "alpha", "alpha/spec/2", {
                "commit": external_commit, "path": "items.json",
            }, "SH-02", "structured-item/1", external_payload)
            subprocess.run(["git", "update-ref", "-d", "refs/heads/pinned-source"], cwd=root, check=True)
            subprocess.run(["git", "reflog", "expire", "--expire=now", "--all"], cwd=root, check=True)
            subprocess.run(["git", "gc", "--prune=now"], cwd=root, check=True)
            try:
                resolved_external = resolve_version(catalog, external_entry["reference"], root)
            except CatalogError as exc:
                self.fail(f"catalog history must retain required source objects: {exc}")
            self.assertEqual(resolved_external["payload"], external_payload,
                             "catalog history must retain required source objects")
            missing_payload = b'{"id":"SH-03","then":["unavailable"]}\n'
            missing_blob = subprocess.check_output(
                ["git", "hash-object", "-w", "--stdin"], cwd=root, input=missing_payload
            ).decode().strip()
            missing_tree = subprocess.check_output(
                ["git", "mktree"], cwd=root,
                input=f"100644 blob {missing_blob}\titems.json\n", text=True
            ).strip()
            missing_commit = subprocess.check_output(
                ["git", "commit-tree", missing_tree, "-m", "source object loss"],
                cwd=root, text=True
            ).strip()
            missing_entry = register_revision(catalog, "alpha", "alpha/spec/3", {
                "commit": missing_commit, "path": "items.json",
            }, "SH-03", "structured-item/1", missing_payload)
            objects = Path(subprocess.check_output(
                ["git", "rev-parse", "--git-path", "objects"], cwd=root, text=True
            ).strip())
            if not objects.is_absolute():
                objects = root / objects
            commit_object = objects / missing_commit[:2] / missing_commit[2:]
            self.assertTrue(commit_object.exists(), "the fixture source commit should be loose before corruption")
            commit_object.unlink()
            with self.assertRaises(CatalogError):
                resolve_version(catalog, missing_entry["reference"], root)
            doc = json.loads(catalog.read_text())
            snapshot_id = doc["entries"][0]["snapshot_id"]
            doc["snapshots"][snapshot_id]["path"] = "missing.json"
            catalog.write_text(json.dumps(doc))
            with self.assertRaises(CatalogError):
                resolve_version(catalog, entry["reference"], root)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"id":"SH-04","then":["same"]}\n'
            old_commit = make_git_repo(root, payload)
            catalog = root / "integrity.json"
            initialize_catalog(catalog, "alpha")
            entry = register_revision(catalog, "alpha", "alpha/spec/1", {
                "commit": old_commit, "path": "items.json",
            }, "SH-04", "structured-item/1", payload)
            subprocess.run(["git", "add", "items.json"], cwd=root, check=True)
            subprocess.run(["git", "commit", "--allow-empty", "-qm", "equivalent current source"],
                           cwd=root, check=True)
            current_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=root, text=True
            ).strip()
            self.assertEqual(subprocess.check_output(
                ["git", "show", f"{current_commit}:items.json"], cwd=root
            ), payload)
            objects = Path(subprocess.check_output(
                ["git", "rev-parse", "--git-path", "objects"], cwd=root, text=True
            ).strip())
            if not objects.is_absolute():
                objects = root / objects
            (objects / old_commit[:2] / old_commit[2:]).unlink()
            with self.assertRaises(CatalogError):
                register_revision(catalog, "alpha", "alpha/spec/1", {
                    "commit": current_commit, "path": "items.json",
                }, "SH-04", "structured-item/1", payload)

    def test_snapshot_identity_requires_full_object_id(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = b'{"id":"SH-01"}\n'
            commit = make_git_repo(root, payload)
            catalog = root / "integrity.json"
            initialize_catalog(catalog, "alpha")
            for invalid in (commit[:39], "a" * 41, "a" * 63):
                with self.assertRaises(CatalogError):
                    register_revision(catalog, "alpha", "alpha/spec/1", {
                        "commit": invalid, "path": "items.json",
                    }, "SH-01", "structured-item/1", payload)


if __name__ == "__main__":
    unittest.main()
