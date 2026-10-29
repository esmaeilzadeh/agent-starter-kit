from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".agents/ask"))
from workflow_refs.migration import export_bundle, import_bundle, migrate
from workflow_refs.store import CatalogError, resolve_version


class ReferenceMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="refs-migration-")
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=self.root, check=True)
        self.source = self.root / "work/demo/source.json"
        self.source.parent.mkdir(parents=True)
        self.raw = b'{"items":[{"id":"plan-item","value":3,"inputs":[]}]}'
        self.source.write_bytes(self.raw)
        subprocess.run(["git", "add", "work/demo/source.json"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", "legacy source"], cwd=self.root, check=True)
        self.commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.root, text=True).strip()
        self.references = self.root / "work/demo/references"
        self.references.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_legacy_migration_and_bundle_retention(self):
        declaration = {"schema": "ask-reference-migration/v1", "owner": "demo", "mappings": [{
            "legacy_reference": "old-plan:abc123", "logical_id": "demo/spec/1/plan/1/item/1",
            "snapshot": {"commit": self.commit, "path": "work/demo/source.json"},
            "item_id": "plan-item", "profile": "structured-item/1",
            "source_sha256": hashlib.sha256(self.raw).hexdigest(),
        }]}
        (self.references / "migration.json").write_text(json.dumps(declaration))
        migrated = migrate(self.root, "demo")
        ref = migrated["mappings"][0]["reference"]
        self.assertEqual(ref, "demo/spec/1/plan/1/item/1@1")
        self.assertEqual(resolve_version(self.references / "integrity.json", ref, self.root)["payload"], self.raw)
        self.assertEqual(migrate(self.root, "demo")["mappings"][0]["reference"], ref)

        bundle = self.root / "transfer.refs"
        exported = export_bundle(self.root, "demo", bundle)
        self.assertEqual(exported["status"], "exported")
        imported = import_bundle(self.root, bundle)
        self.assertTrue(imported["idempotent"])
        self.assertEqual(imported["entries_verified"], 1)

    def test_bundle_manifest_cannot_create_authority(self):
        declaration = {"schema": "ask-reference-migration/v1", "owner": "demo", "mappings": [{
            "legacy_reference": "old-plan:abc123", "logical_id": "demo/spec/1/plan/1/item/1",
            "snapshot": {"commit": self.commit, "path": "work/demo/source.json"},
            "item_id": "plan-item", "profile": "structured-item/1",
        }]}
        (self.references / "migration.json").write_text(json.dumps(declaration))
        migrate(self.root, "demo")
        bundle = self.root / "transfer.refs"
        export_bundle(self.root, "demo", bundle)

        other = self.root / "other"
        subprocess.run(["git", "clone", "-q", str(self.root), str(other)], check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=other, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.test"], cwd=other, check=True)
        with self.assertRaisesRegex(CatalogError, "cannot establish or replace"):
            import_bundle(other, bundle)


if __name__ == "__main__":
    unittest.main()
