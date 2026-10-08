# Specification Challenge

## Model

`gpt-6-luna` / Codex / parent model `GPT-6`. Luna is the explicit model override for this simple workstream Challenge; the generic generated `03-spec-challenge` default remains Astra as required by CM-001.

## Specification

`specs/current/codex-model-refresh.md` and its revision 2 JSON contract. This challenge independently assesses CM-001 through CM-003 for the clarified per-job cost and fit policy.

## Ambiguities

- “Current” model availability is time- and account-dependent. The contract bounds this claim to official guidance and the local catalog reviewed on 2026-10-08; it does not promise future availability.
- “Diverse” could imply cross-family independence. The spec explicitly defines the Astra choice as a distinct model in the same GPT family, and disclaims cross-family diversity, so the term is bounded by the repository’s existing pool semantics.
- “Best fit” might be read as a benchmark result. The spec identifies per-stage assignments as engineering judgment and makes no performance claim.

These are adequately bounded for this configuration change.

## Missing failure cases

- CM-001 would fail if the YAML contained the intended assignments but generated Codex agent definitions retained stale model pins, or if HIGH-risk Review still resolved to Luna. The criterion explicitly requires generated defaults and Astra escalation; the existing sync journey is planned to exercise generated output and risk routing.
- CM-002 would fail if a stage-specific environment value or existing work/consumer override were shadowed by the new role/pool values. The generator resolves explicit environment, work overlay, consumer overlay, then defaults; the role map and resolution code are outside the proposed runtime-value change.
- CM-003 would fail if its guidance suggested changing risk classification to represent complexity, or if it named a new automatic classifier. The criterion forbids both and points to existing workstream overrides.

No additional failure case requires a new behavior test: the proposed change is model-name configuration and explanatory guidance, and the existing sync regression check remains in the plan.

## Over-constraint risks

- Requiring Luna for every implementation regardless of task complexity would contradict the clarified cost/fit intent. CM-003 instead allows explicit promotion through the existing workstream overlay.
- Requiring cross-family diversity would change established pool behavior and exceed the stated scope. The accepted contract only requires Astra as a distinct configured model.
- Requiring new tests for static role-name strings would duplicate the existing generator check without testing new runtime behavior.

## Under-constraint risks

- “Use current models” alone would not pin the exact routing. The contract lists each role, pool, and picker entry and requires generated defaults.
- A picker update alone could leave review risk routing or stage roles stale. CM-001 includes generated defaults and high-risk escalation; CM-002 protects existing overrides and other runtimes.
- The absence of comparative performance data could invite unsupported capability claims. The specification and guidance explicitly limit assignments to engineering judgment and make no benchmark claim.

## Review-only justification

All three criteria concern runtime binding values, generated configuration, and documentation of already-supported overrides. They introduce no new execution behavior, API, risk rule, classifier, or external inference. Each JSON criterion has a non-empty reason and an attributable APPROVED decision under `_ask/policies/delegation.md`. The test plan consequently has no behavior-test obligations; the planned existing sync journey and mandatory repository CheckPlan remain applicable verification. This review approves only the exact revision 2 spec and associated plan digests recorded in `traceability/plan-review.json`.

## Recommended clarifications

None required before implementation. Keep the date and account boundary on availability claims, and preserve the explicit disclaimer that stage defaults are not a complexity classifier.

## Challenge verdict

**PASS** — the three criteria are observable by configuration/document inspection and the existing generation journey, their review-only scope is justified, and no conflict with the stated cost/fit intent or existing routing semantics was found. Eligible for acceptance of the reviewed contracts; implementation and later verification remain outstanding.
