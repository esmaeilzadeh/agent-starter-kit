"""Versioned model behavior at the public validation seam."""
import copy
import unittest

from _ask.tests.revising_fixture import digest, model, plan, reference_bytes, reviewed_mapping
from _ask.scripts.engineering_model.validation import validate
from _ask.scripts.engineering_model.domain import task_states


class V2ModelTests(unittest.TestCase):
    def test_optional_containment_support_and_graph_rejections(self):
        document = model()
        refs, canonical_plan = reference_bytes()
        document["nodes"][2]["case"]["plan_digest"] = digest(canonical_plan)
        errors = validate(document, ".", "product", reference_bytes=refs)
        self.assertEqual(errors, [], "v2 permits optional intent and zero-or-one legal containment")
        task = task_states(document)[0]
        self.assertEqual(task["product_identity"], {"work_id": "product", "node_id": "task"})
        self.assertEqual(task["execution_identity"], {"work_id": "delivery", "task_id": "same-id"})

        invalid = copy.deepcopy(document)
        invalid["edges"].extend([
            {"type": "contains", "source": "capability", "target": "story"},
            {"type": "contains", "source": "story", "target": "scenario"},
            {"type": "contains", "source": "capability", "target": "scenario"},
            {"type": "contains", "source": "story", "target": "capability"},
            {"type": "depends_on", "source": "task", "target": "story"},
            {"type": "enables", "source": "task", "target": "scenario"},
        ])
        invalid["nodes"].append({"id": "task-two", "type": "task", "title": "Second", "lifecycle": "planned"})
        invalid["edges"].extend([
            {"type": "depends_on", "source": "task", "target": "task-two"},
            {"type": "depends_on", "source": "task-two", "target": "task"},
        ])
        before = copy.deepcopy(invalid)
        codes = {item["code"] for item in validate(invalid, ".", "product", reference_bytes=refs)}
        self.assertTrue({"EM001_MULTIPLE_PARENTS", "EM001_CONTAINS_CYCLE", "EM001_DEPENDENCY_CYCLE",
                         "EM001_ILLEGAL_EDGE"} <= codes)
        self.assertEqual(invalid, before, "validation leaves the submitted definition unchanged")

        v1 = {"schema": "ask-engineering-model/v1", "work_id": "product", "revision": 1,
              "nodes": [{"id": "task", "type": "task", "title": "Task", "lifecycle": "active"}],
              "edges": []}
        v1_codes = {item["code"] for item in validate(v1, ".", "product")}
        self.assertTrue({"EM001_INTENT_COUNT", "EM001_PARENT_COUNT"} <= v1_codes)

        many = copy.deepcopy(document)
        many["nodes"].append({"id": "story-two", "type": "story", "title": "Second outcome", "lifecycle": "active"})
        many["edges"].extend([
            {"type": "contributes_to", "source": "task", "target": "scenario"},
            {"type": "enables", "source": "capability", "target": "story-two"},
        ])
        self.assertEqual(validate(many, ".", "product", reference_bytes=refs), [],
                         "support remains many-to-many and does not manufacture containment")

        one_intent = copy.deepcopy(document)
        one_intent["nodes"].append({"id": "purpose", "type": "intent", "title": "Purpose", "lifecycle": "active"})
        self.assertEqual(validate(one_intent, ".", "product", reference_bytes=refs), [])
        two_intents = copy.deepcopy(one_intent)
        two_intents["nodes"].append({"id": "purpose-two", "type": "intent", "title": "Other", "lifecycle": "draft"})
        self.assertIn("EM001_INTENT_COUNT", {item["code"] for item in validate(
            two_intents, ".", "product", reference_bytes=refs)})

        bad_decision = copy.deepcopy(document)
        bad_decision["nodes"].append({"id": "choice", "type": "decision", "title": "Choice",
                                      "lifecycle": "resolved", "options": [
                                          {"id": "a", "label": "A"}, {"id": "b", "label": "B"}],
                                      "history": []})
        self.assertIn("EM001_DECISION_RESOLUTION", {item["code"] for item in validate(
            bad_decision, ".", "product", reference_bytes=refs)})

        duplicate = copy.deepcopy(document)
        duplicate["nodes"].append(copy.deepcopy(duplicate["nodes"][1]))
        self.assertIn("EM001_DUPLICATE_ID", {item["code"] for item in validate(
            duplicate, ".", "product", reference_bytes=refs)})

        malformed = copy.deepcopy(document)
        malformed["nodes"][1]["lifecycle"] = "not-a-state"
        self.assertIn("EM001_LIFECYCLE", {item["code"] for item in validate(
            malformed, ".", "product", reference_bytes=refs)})
        malformed["nodes"][1]["lifecycle"] = []
        malformed["nodes"][1]["type"] = []
        self.assertTrue(validate(malformed, ".", "product", reference_bytes=refs),
                        "malformed JSON values produce diagnostics rather than crashing validation")

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
        distinct["edges"].pop()
        distinct["nodes"][3]["execution"] = {"work_id": "other-delivery", "task_id": "same-id"}
        self.assertEqual(validate(distinct, ".", "product", reference_bytes=refs),
                         [], "equal local task IDs in different execution works remain distinct")

        distinct["nodes"][3]["execution"] = {"work_id": "other-delivery", "task_id": "task"}
        self.assertEqual(validate(distinct, ".", "product", reference_bytes=refs), [],
                         "a local product slug cannot implicitly join an execution task")


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

        missing_active = copy.deepcopy(document)
        del missing_active["nodes"][2]["case"]
        self.assertIn("EM001_FLOW_CASE", {item["code"] for item in validate(
            missing_active, ".", "product", reference_bytes=refs)})

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

        # A same-plan selector cannot smuggle the containing plan digest.
        mapped = copy.deepcopy(document)
        mapped["nodes"][2]["case"] = {"scope": "local", "case_id": "WB-publish",
                                       "plan_digest": digest(canonical_plan)}
        self.assertIn("EM001_FLOW_CASE", {item["code"] for item in validate(
            mapped, ".", "product", reference_bytes=refs)})

        # A reviewed local mapping can relate a distinct canonical test case to
        # the selected flow. Its body is bound independently of the review.
        alternate = copy.deepcopy(document)
        alternate["nodes"].append({"id": "test-stale", "type": "test", "title": "Stale assertion",
                                   "lifecycle": "active", "reference": {
                                       "path": "work/product/test-plan.json", "id": "WB-stale"}})
        alternate["edges"].append({"type": "covers", "source": "test-stale", "target": "scenario"})
        alternate_plan = plan()
        alternate_plan["flow_mappings"] = [reviewed_mapping(
            {"scope": "local", "case_id": "WB-publish"},
            {"scope": "local", "case_id": "WB-stale"})]
        refs["work/product/test-plan.json"] = __import__("json").dumps(alternate_plan).encode()
        alternate["nodes"][2]["case"]["plan_digest"] = digest(alternate_plan)
        self.assertEqual(validate(alternate, ".", "product", reference_bytes=refs), [],
                         "an independently reviewed local mapping explicitly relates the cases")

        self_reference = copy.deepcopy(alternate_plan)
        self_reference["flow_mappings"][0]["scenario_case"]["plan_digest"] = digest(self_reference)
        body = {key: self_reference["flow_mappings"][0][key] for key in ("scenario_case", "test_case")}
        self_reference["flow_mappings"][0]["review"]["body_digest"] = digest(body)
        refs["work/product/test-plan.json"] = __import__("json").dumps(self_reference).encode()
        alternate["nodes"][2]["case"]["plan_digest"] = digest(self_reference)
        self.assertIn("EM001_FLOW_MAPPING", {item["code"] for item in validate(
            alternate, ".", "product", reference_bytes=refs)})

        unreviewed_plan = copy.deepcopy(alternate_plan)
        unreviewed_plan["flow_mappings"][0]["review"]["decision"]["decision"] = "PENDING"
        refs["work/product/test-plan.json"] = __import__("json").dumps(unreviewed_plan).encode()
        alternate["nodes"][2]["case"]["plan_digest"] = digest(unreviewed_plan)
        self.assertIn("EM001_FLOW_MAPPING_REVIEW", {item["code"] for item in validate(
            alternate, ".", "product", reference_bytes=refs)})

        external = copy.deepcopy(document)
        foreign_plan = {"schema": "ask-test-plan/v1", "work_id": "delivery", "tests": [
            {"id": "WB-external", "scenario": {"given": "Given", "when": "When", "then": ["Then"]}}]}
        selected_plan = plan()
        selected_plan["flow_mappings"] = [reviewed_mapping(
            {"scope": "local", "case_id": "WB-publish"},
            {"scope": "external", "work_id": "delivery", "plan_digest": digest(foreign_plan),
             "case_id": "WB-external"})]
        external["nodes"].append({"id": "external-test", "type": "test", "title": "External assertion",
                                  "lifecycle": "active", "reference": {
                                      "path": "work/delivery/test-plan.json", "id": "WB-external",
                                      "work_id": "delivery", "plan_digest": digest(foreign_plan)}})
        external["edges"].append({"type": "covers", "source": "external-test", "target": "scenario"})
        refs, _ = reference_bytes()
        refs["work/product/test-plan.json"] = __import__("json").dumps(selected_plan).encode()
        refs["work/delivery/test-plan.json"] = __import__("json").dumps(foreign_plan).encode()
        external["nodes"][2]["case"]["plan_digest"] = digest(selected_plan)
        self.assertEqual(validate(external, ".", "product", reference_bytes=refs), [],
                         "an external canonical test keeps its owning work and immutable plan digest")

        changed = copy.deepcopy(selected_plan)
        changed["flow_mappings"][0]["test_case"]["case_id"] = "missing"
        refs["work/product/test-plan.json"] = __import__("json").dumps(changed).encode()
        external["nodes"][2]["case"]["plan_digest"] = digest(changed)
        self.assertIn("EM001_FLOW_MAPPING_REVIEW", {item["code"] for item in validate(
            external, ".", "product", reference_bytes=refs)})


if __name__ == "__main__":
    unittest.main()
