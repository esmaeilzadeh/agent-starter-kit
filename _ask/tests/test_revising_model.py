"""Versioned model behavior at the public validation seam."""
import copy
import unittest

from _ask.tests.revising_fixture import digest, model, plan, reference_bytes
from _ask.scripts.engineering_model.validation import validate


class V2ModelTests(unittest.TestCase):
    def test_optional_containment_support_and_graph_rejections(self):
        document = model()
        refs, canonical_plan = reference_bytes()
        document["nodes"][2]["case"]["plan_digest"] = digest(canonical_plan)
        errors = validate(document, ".", "product", reference_bytes=refs)
        self.assertEqual(errors, [], "v2 permits optional intent and zero-or-one legal containment")

        invalid = copy.deepcopy(document)
        invalid["edges"].extend([
            {"type": "contains", "source": "capability", "target": "story"},
            {"type": "contains", "source": "story", "target": "scenario"},
            {"type": "contains", "source": "capability", "target": "scenario"},
            {"type": "contains", "source": "story", "target": "capability"},
            {"type": "depends_on", "source": "task", "target": "story"},
            {"type": "enables", "source": "task", "target": "scenario"},
        ])
        before = copy.deepcopy(invalid)
        codes = {item["code"] for item in validate(invalid, ".", "product", reference_bytes=refs)}
        self.assertTrue({"EM001_MULTIPLE_PARENTS", "EM001_CONTAINS_CYCLE", "EM001_DEPENDENCY_CYCLE",
                         "EM001_ILLEGAL_EDGE"} <= codes)
        self.assertEqual(invalid, before, "validation leaves the submitted definition unchanged")

        v1 = {"schema": "ask-engineering-model/v1", "work_id": "product", "revision": 1,
              "nodes": [{"id": "task", "type": "task", "title": "Task", "lifecycle": "active"}],
              "edges": []}
        self.assertIn("EM001_SCHEMA", {item["code"] for item in validate(v1, ".", "product")})

    def test_execution_aliases_and_foreign_product_boundaries(self):
        document = model()
        refs, canonical_plan = reference_bytes()
        document["nodes"][2]["case"]["plan_digest"] = digest(canonical_plan)
        other = copy.deepcopy(document["nodes"][3])
        other["id"] = "task-two"
        document["nodes"].append(other)
        foreign = {"type": "supports", "source": "test", "target": "foreign-story"}
        document["edges"].append(foreign)
        codes = {item["code"] for item in validate(document, ".", "product", reference_bytes=refs)}
        self.assertIn("EM001_DUPLICATE_EXECUTION", codes,
                      "execution identity is the explicit work_id/task_id pair")
        self.assertIn("EM001_DANGLING_EDGE", codes,
                      "foreign product identities cannot be represented as local support edges")

        distinct = copy.deepcopy(document)
        distinct["nodes"].pop()
        distinct["nodes"][3]["execution"] = {"work_id": "other-delivery", "task_id": "same-id"}
        self.assertEqual(validate(distinct, ".", "product", reference_bytes=refs),
                         [], "equal local task IDs in different execution works remain distinct")


class FlowTests(unittest.TestCase):
    def test_shared_criterion_does_not_prove_another_concrete_flow(self):
        document = model()
        refs, canonical_plan = reference_bytes()
        document["nodes"][2]["case"]["plan_digest"] = digest(canonical_plan)
        self.assertEqual(validate(document, ".", "product", reference_bytes=refs), [])

        wrong_digest = copy.deepcopy(document)
        wrong_digest["nodes"][2]["case"]["plan_digest"] = "0" * 64
        self.assertIn("EM001_FLOW_CASE", {item["code"] for item in validate(
            wrong_digest, ".", "product", reference_bytes=refs)})

        wrong_coverage = copy.deepcopy(document)
        wrong_coverage["edges"][2]["source"] = "test"
        wrong_coverage["nodes"][4]["reference"]["id"] = "WB-stale"
        self.assertIn("EM001_FLOW_COVERAGE", {item["code"] for item in validate(
            wrong_coverage, ".", "product", reference_bytes=refs)})

        unplanned = copy.deepcopy(document)
        unplanned["nodes"][2]["lifecycle"] = "draft"
        del unplanned["nodes"][2]["case"]
        self.assertEqual(validate(unplanned, ".", "product", reference_bytes=refs), [],
                         "draft scenarios without a selected case remain inspectable")

        # A same-plan selector cannot smuggle the containing plan digest, and an
        # explicit alternate mapping must retain its independent review binding.
        mapped = copy.deepcopy(document)
        mapped["nodes"][2]["case"] = {"scope": "local", "case_id": "WB-publish",
                                       "plan_digest": digest(canonical_plan)}
        self.assertIn("EM001_FLOW_CASE", {item["code"] for item in validate(
            mapped, ".", "product", reference_bytes=refs)})


if __name__ == "__main__":
    unittest.main()
