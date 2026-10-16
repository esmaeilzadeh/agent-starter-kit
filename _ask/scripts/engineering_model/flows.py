"""Canonical case selection and explicit reviewed flow mappings."""
import hashlib
import json
from pathlib import Path


def _decode(raw):
    if raw is None:
        return None
    try:
        return json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
    except (UnicodeError, ValueError, TypeError):
        return None


def _digest(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


def _source(path, root, captured):
    if captured is not None:
        return _decode(captured.get(path))
    try:
        return _decode((Path(root) / path).read_bytes())
    except OSError:
        return None


def _mapping_review_valid(entry):
    review = entry.get("review")
    body = {key: entry.get(key) for key in ("scenario_case", "test_case")}
    if not isinstance(review, dict) or review.get("body_digest") != _digest(body):
        return False
    decision = review.get("decision")
    return (isinstance(decision, dict) and decision.get("decision") == "APPROVED"
            and isinstance(decision.get("reviewer"), str) and bool(decision["reviewer"].strip())
            and decision.get("independent") is True)


def _qualified_selector(value, plan_work, plan_digest):
    if not isinstance(value, dict):
        return None
    if value.get("scope") == "local" and set(value) == {"scope", "case_id"}:
        return (plan_work, plan_digest, value["case_id"])
    if value.get("scope") == "external" and set(value) == {"scope", "work_id", "plan_digest", "case_id"}:
        if all(isinstance(value.get(k), str) and value[k] for k in ("work_id", "plan_digest", "case_id")):
            return (value["work_id"], value["plan_digest"], value["case_id"])
    return None


def flow_diagnostics(document, nodes, edges, root, work_id, reference_bytes):
    errors = []

    def error(code, path, message, *ids):
        item = {"code": code, "path": path, "message": message}
        if ids: item["ids"] = list(ids)
        errors.append(item)

    selected = {}
    for node_id, node in sorted(nodes.items()):
        if node.get("type") != "scenario":
            continue
        case = node.get("case")
        path = f"$.nodes[{list(nodes).index(node_id)}].case"
        if case is None:
            if node.get("lifecycle") != "draft":
                error("EM001_FLOW_CASE", path, "active scenario requires a selected canonical case", node_id)
            continue
        if not isinstance(case, dict) or set(case) != {"work_id", "plan_digest", "case_id"} or not all(
                isinstance(case.get(k), str) and case[k] for k in ("work_id", "plan_digest", "case_id")):
            error("EM001_FLOW_CASE", path, "case must select work_id, plan_digest, and case_id", node_id)
            continue
        plan_path = f"work/{case['work_id']}/test-plan.json"
        plan = _source(plan_path, root, reference_bytes)
        actual_digest = _digest(plan) if isinstance(plan, dict) else None
        if (not isinstance(plan, dict) or plan.get("work_id") != case["work_id"]
                or actual_digest != case["plan_digest"]):
            error("EM001_FLOW_CASE", path, "selected case source work or plan digest does not match", node_id)
            continue
        tests = plan.get("tests")
        entries = [item for item in tests if isinstance(item, dict) and item.get("id") == case["case_id"]] if isinstance(tests, list) else []
        if len(entries) != 1 or not isinstance(entries[0].get("scenario"), dict):
            error("EM001_FLOW_CASE", path, "selected canonical case is missing or ambiguous", node_id)
            continue
        selected[node_id] = (case["work_id"], case["plan_digest"], case["case_id"])
        _validate_mappings(plan, plan_path, case["work_id"], actual_digest, root,
                           reference_bytes, error, node_id)

    # Coverage is a concrete case relation. A shared criterion is intentionally
    # not consulted here.
    for kind, test_id, scenario_id in edges:
        if kind != "covers" or test_id not in nodes or scenario_id not in selected:
            continue
        test_ref = nodes[test_id].get("reference")
        test_case_id = test_ref.get("id") if isinstance(test_ref, dict) else None
        test_work = test_ref.get("work_id") if isinstance(test_ref, dict) else None
        test_path = test_ref.get("path") if isinstance(test_ref, dict) else None
        if test_work is None and isinstance(test_path, str):
            parts = Path(test_path).parts
            test_work = parts[1] if len(parts) == 3 and parts[0] == "work" and parts[2] == "test-plan.json" else None
        test_plan_path = f"work/{test_work}/test-plan.json" if isinstance(test_work, str) else None
        test_plan = _source(test_plan_path, root, reference_bytes) if test_plan_path else None
        test_digest = _digest(test_plan) if isinstance(test_plan, dict) else None
        if isinstance(test_ref, dict) and test_ref.get("plan_digest") is not None and test_ref["plan_digest"] != test_digest:
            error("EM001_FLOW_COVERAGE", "$.edges", "Test source plan digest does not match", test_id, scenario_id)
            continue
        if (test_work, test_digest, test_case_id) == selected[scenario_id]:
            continue
        selected_work = selected[scenario_id][0]
        plan_path = f"work/{selected_work}/test-plan.json"
        plan = _source(plan_path, root, reference_bytes)
        allowed = False
        if isinstance(plan, dict):
            for mapping in plan.get("flow_mappings", []) if isinstance(plan.get("flow_mappings"), list) else []:
                if not isinstance(mapping, dict) or not _mapping_review_valid(mapping):
                    continue
                scenario_key = _qualified_selector(mapping.get("scenario_case"), plan.get("work_id"), _digest(plan))
                test_key = _qualified_selector(mapping.get("test_case"), plan.get("work_id"), _digest(plan))
                if scenario_key == selected[scenario_id] and test_key == (test_work, test_digest, test_case_id):
                    allowed = True
        if not allowed:
            error("EM001_FLOW_COVERAGE", "$.edges", "test does not cover the scenario's selected canonical case", test_id, scenario_id)
    return errors


def _validate_mappings(plan, path, plan_work, digest, root, captured, error, scenario_id):
    mappings = plan.get("flow_mappings", [])
    if not isinstance(mappings, list):
        error("EM001_FLOW_MAPPING", path, "flow_mappings must be an array", scenario_id)
        return
    seen = set()
    for index, entry in enumerate(mappings):
        item_path = f"{path}.flow_mappings[{index}]"
        if not isinstance(entry, dict) or set(entry) != {"scenario_case", "test_case", "review"}:
            error("EM001_FLOW_MAPPING", item_path, "flow mapping needs scenario_case, test_case, and review", scenario_id)
            continue
        body = {"scenario_case": entry["scenario_case"], "test_case": entry["test_case"]}
        key = _digest(body)
        if key in seen:
            error("EM001_FLOW_MAPPING", item_path, "duplicate flow mapping", scenario_id)
        seen.add(key)
        for selector in (entry["scenario_case"], entry["test_case"]):
            if not isinstance(selector, dict):
                error("EM001_FLOW_MAPPING", item_path, "flow mapping selector is malformed", scenario_id)
            elif selector.get("scope") == "local" and set(selector) != {"scope", "case_id"}:
                error("EM001_FLOW_MAPPING", item_path, "local mapping selectors omit containing plan digest", scenario_id)
            elif selector.get("scope") == "external" and _qualified_selector(selector, plan_work, digest) is None:
                error("EM001_FLOW_MAPPING", item_path, "external mapping selector needs immutable qualified identity", scenario_id)
            elif selector.get("scope") == "local" and isinstance(selector.get("case_id"), str):
                records = plan.get("tests", [])
                if not isinstance(records, list) or sum(isinstance(row, dict) and row.get("id") == selector["case_id"] for row in records) != 1:
                    error("EM001_FLOW_MAPPING", item_path, "local mapping case is missing or ambiguous", scenario_id)
            elif selector.get("scope") == "external":
                qualified = _qualified_selector(selector, plan_work, digest)
                if qualified is not None and qualified[0] == plan_work:
                    error("EM001_FLOW_MAPPING", item_path, "containing-plan cases use local selectors without a digest", scenario_id)
                external_path = f"work/{qualified[0]}/test-plan.json"
                external_plan = _source(external_path, root, captured)
                if (not isinstance(external_plan, dict) or _digest(external_plan) != qualified[1]
                        or external_plan.get("work_id") != qualified[0]
                        or not isinstance(external_plan.get("tests"), list)
                        or sum(isinstance(row, dict) and row.get("id") == qualified[2]
                               for row in external_plan["tests"]) != 1):
                    error("EM001_FLOW_MAPPING", item_path, "external mapping target identity is unavailable or mismatched", scenario_id)
            elif not isinstance(selector.get("scope"), str) or selector.get("scope") not in {"local", "external"}:
                error("EM001_FLOW_MAPPING", item_path, "mapping selector scope is unknown", scenario_id)
        if not _mapping_review_valid(entry):
            error("EM001_FLOW_MAPPING_REVIEW", item_path, "flow mapping lacks an unchanged independently approved body", scenario_id)
