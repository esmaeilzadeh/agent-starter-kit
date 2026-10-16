"""Candidate-local fixtures for the revising workbench model tests."""
import hashlib
import json


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def model(work_id="product"):
    return {
        "schema": "ask-engineering-model/v2", "work_id": work_id, "revision": 1,
        "nodes": [
            {"id": "capability", "type": "feature", "title": "Capability", "lifecycle": "active"},
            {"id": "story", "type": "story", "title": "Outcome", "lifecycle": "active"},
            {"id": "scenario", "type": "scenario", "title": "Publish", "lifecycle": "active",
             "reference": {"path": "specs/current/product.json", "id": "EM-007"},
             "case": {"work_id": "product", "plan_digest": "pending", "case_id": "WB-publish"}},
            {"id": "task", "type": "task", "title": "Implement", "lifecycle": "planned",
             "execution": {"work_id": "delivery", "task_id": "same-id"}},
            {"id": "test", "type": "test", "title": "Publish assertion", "lifecycle": "active",
             "reference": {"path": "work/product/test-plan.json", "id": "WB-publish"}},
        ],
        "edges": [
            {"type": "enables", "source": "capability", "target": "story"},
            {"type": "contributes_to", "source": "task", "target": "story"},
            {"type": "covers", "source": "test", "target": "scenario"},
        ],
    }


def plan():
    result = {"schema": "ask-test-plan/v1", "work_id": "product", "tests": [
        {"id": "WB-publish", "criterion_ids": ["EM-007"], "scenario": {
            "given": "A valid publication proposal", "when": "Publish", "then": ["It is published"]}},
        {"id": "WB-stale", "criterion_ids": ["EM-007"], "scenario": {
            "given": "A stale proposal", "when": "Publish", "then": ["It is refused"]}},
    ]}
    return result


def reference_bytes():
    spec = {"schema": "ask-spec/v1", "work_id": "product", "revision": 1,
            "criteria": [{"id": "EM-007", "given": "A proposal", "when": "Published", "then": ["Result"]}]}
    canonical_plan = plan()
    return {"specs/current/product.json": json.dumps(spec).encode(),
            "work/product/test-plan.json": json.dumps(canonical_plan).encode()}, canonical_plan
