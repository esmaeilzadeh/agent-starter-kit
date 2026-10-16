# Specification Challenge

## Model

- model: `gpt-6-astra`
- runtime: `codex`
- reasoning_effort: `high`
- parent_model: GPT-6-family Codex, exact identifier unavailable
- independence: separate reviewer context within the same GPT family
- selection: parent reports that the human replied `asta high` after the Codex
  picker and same-family warning; this review uses that selection.

The binding resolves `03-spec-challenge` → `adversarial` → `gpt-6-astra`, with
`high` effort in `.agents/ask/bindings/runtimes/codex.yaml`. No work overlay,
applicable environment override, `.ask.env`, or consumer model map was present.
Prepared `writing-for-agents` was applied in embedded mode.

## Specification

Independent review of PROPOSED revision 2 for `revising-workbench`, dated
2026-10-16, at source commit `5439564e8ee523196c11ccedd8906692c6c966ad`.
The initial worktree cleanliness check passed. Scope is the specification challenge;
intent confirmation, promotion, planning, implementation and acceptance remain
outside this decision.

The following SHA256 values were independently computed from the inspected bytes:

| Input | SHA256 |
| --- | --- |
| `work/revising-workbench/intent.md` | `d7b5d20f8c07576eaba63cab675f9ed764983550d24f9157b6b554dc68c57d1e` |
| `work/revising-workbench/spec.md` | `327cdc5a80490d36fd45cc353d46320037791aa6506aae7fb0f0cb433dfd1ccb` |
| `work/revising-workbench/spec.json` — file bytes | `3994ffb7f28abe6e232e78c30952860deca6349c66b563efebe265ca59cfc203` |
| `spec.json` — canonical JSON | `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd` |

Canonical JSON uses `json.dumps(value, sort_keys=True, separators=(",", ":"))`,
UTF-8 encoded, matching `.agents/ask/verification/traceability/contracts.py:28`.
This verdict applies only to these inputs. Changed input bytes require a new
challenge decision; this artifact is not an accepted test-plan pin.

Reviewed the pinned baseline Markdown and JSON at
`159f516d5fb81575b1f96a1f310ae66e3427c31f`, the stage protocol, delegation/risk/
verification/worktree/workflow/git-flow policies, and
`_ask/docs/spec-test-traceability.md`. Examined the current model validator,
semantic editing and canonical-reference boundaries, the read-only evidence
adapter and qualified-source/result inspector, the actual WB-003 test and helpers,
its plan case, retained TaskResult and local run reports/logs.

## Ambiguities

No blocking ambiguity remains in the proposed product behavior.

- **Work entry:** `spec.md:40` names the actual agent/coordinator intake and its
  timing before branch creation, intent recording or admission. `spec.md:46`
  distinguishes explicit subjects, recorded associations, conflicts and the
  chooser. EM-013 (`spec.json:130`) explicitly rejects resolver-only test evidence.
  The concrete caller wiring belongs in Plan; its absence today is expected for
  this proposed change.
- **Context admission:** `spec.md:114` distinguishes unsafe/malformed references
  from safe missing, zero-match and multiple-match references. `spec.md:122` makes
  the dependent-action restriction explicit. These rules permit honest partial
  inspection without making a broken current document actionable.
- **Flow identity:** `spec.md:92` selects a canonical case by source work, plan
  digest and case ID; `spec.md:98` requires explicit coverage agreement. The
  criterion-to-flow distinction is sufficient to prevent a generic criterion
  match from becoming flow proof. Concrete v2 field names and selector syntax
  are design details to settle before implementation.
- **Human understanding:** `spec.md:172` and EM-016 (`spec.json:164`) require
  individual pass/fail identifications, exact candidate/context binding,
  invalidation after relevant changes and a successful exercise without chat
  assistance. A polished screenshot or a reviewer saying the UI looks clear
  cannot satisfy this requirement.

The Why in `intent.md:36` is addressed by meaningful purpose, selected source
passages, concrete flow and helper context, actual outcomes, and the comprehension
exercise. The specification permits standalone/shared work without making the
human invent missing ancestors.

## Missing failure cases

No unhandled failure case found that permits a materially incorrect delivery to
meet revision 2. The following counterexamples were tested against its wording;
they are required rejection/limitation cases, not reports of implemented behavior.

| Failure trigger and bad outcome | Controlling requirement | Assessment |
| --- | --- | --- |
| Success and stale-rejection Scenarios share EM-007; the UI advertises the success Test as proving both. | `spec.md:98`; EM-008/011 | Disallowed: selected case or reviewed flow mapping must agree; criterion overlap is only a related obligation. |
| A Task supports two Stories; opening it through the second duplicates the Task or Back returns to the first route. | `spec.md:77`, `spec.md:143`; EM-008/009 | Disallowed: qualified identity and initiating route are preserved. |
| A branch is treated as an Epic, or a later card creates a live Task during inspection. | `spec.md:46`, `spec.md:58`; EM-013 | Disallowed: subject resolution precedes execution creation and inspection writes nothing. |
| A missing plan passage blocks every unrelated decision, or an ambiguous heading silently selects the first match. | `spec.md:114`, `spec.md:122`; EM-015 | Disallowed: missing/ambiguous context is admitted with limitations, with dependent actions blocked separately. |
| A spec-only edit, newly created target file or duplicate heading leaves a stale decision form actionable. | `spec.md:125`; EM-007/015 | Disallowed: captured dependency bytes and match state participate in freshness and action admission. |
| A selected test method is readable only after searching for helpers, or a current helper is substituted into historical source. | `spec.md:158`; EM-011/016 | Disallowed: necessary same-revision fixture/helper/global context is part of inspection and the human exercise. |
| A fixture's synthetic `passed` value or the TaskResult's output excerpt stands in for the genuine retained test execution. | `spec.md:201`, `spec.md:207`; EM-016 | Disallowed: actual reports/logs and authority must validate; a missing prerequisite blocks the demonstration. |
| Unchanged test bytes make an older implementation run appear current, or tampered output survives refresh. | `spec.md:151`, `spec.md:164`; EM-003/011/012 | Disallowed: candidate and integrity authority remain in force; execution outcome and applicability are separate. |
| A readability exercise fails, omits an identification, or is reused after helper/context changes. | `spec.md:172`; EM-016 | Disallowed: unresolved failure blocks completion and relevant changes invalidate the review. |
| V2 browsing converts a v1 record, relaxes its original validation, or assigns the old accepted pin to the new work identity. | `spec.md:24`, `spec.md:87`, `spec.md:220`; EM-014/017 | Disallowed: explicit reviewed migration, historical preservation and new contract authority are required. |

WB-003 provides concrete evidence for the distinction between fixtures and actual
execution. At candidate `70dd295aacff869857081a94870d02fcbf4d640c`, the selected
test source has SHA256
`a690829ed979e6f4976f83300337822d682d363573adc89ef88f759f40d47414`; its canonical
plan digest is `4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8`.
The selected method at `_ask/tests/test_engineering_workbench_evidence.py:113`
uses `setUp`, `_report`, `_ledger` and Git/file helpers. Its synthetic records
exercise matching identities and contradictory source/candidate attribution;
they are not the retained execution of this method.

Local reports for red `111e0f24d5e448c387cd1558b864b18e` and final green
`799924ec199b4717a3eabf4fb39a1bdc` contain the specified qualified test, with
recorded outcomes `failed`/`behavior_assertion` and `passed`, respectively. Both
selected logs exist and match their recorded SHA256 digests. A local accepted
ref exists. These are limited availability/identity observations, not a full
authority evaluation or workstream-completion verdict. The requirement to use
the existing evaluator remains unsatisfied until the future demonstration.

## Over-constraint risks

No blocking over-constraint identified.

- Active Scenarios require planned concrete cases, while unplanned Scenarios can
  remain draft (`spec.md:92`). This preserves the intended canonical assertion
  boundary without forbidding exploratory definitions.
- Necessary helper context may use curated references (`spec.md:158`); a general
  program analyzer or mandatory test syntax is unnecessary.
- V2 changes optional containment and support relationships explicitly. V1's
  existing parent/coverage rules remain historical behavior, visible in
  `_ask/scripts/engineering_model/validation.py:212`. A global relaxation of that
  validator would violate EM-014; version dispatch and migration are Plan work.
- Streamlit remains the baseline with an evidence-backed amendment route
  (`spec.md:147`). Existing local pilot budgets are discoverable in
  `work/structured-agentic-environment/workbench-design.md:157`: 20 warm samples,
  p95 limits of 1.5s overview, 500ms metadata navigation/filter and 1s selected
  source/result, plus five cold restarts with a 4s limit. This review makes no
  performance claim and grants no budget reduction.

## Under-constraint risks

No blocking under-constraint identified. Verification must retain the following
scope when the independently reviewed test plan is written. This is an assessment
of required evidence classes, not an executable plan or authority record.

| Criteria | Required evidence scope |
| --- | --- |
| EM-001/008/014 | Unit graph, lifecycle, identity and coverage rules; integration through versioned admission/migration, with preserved v1 behavior and evidence attribution. |
| EM-002/006/007/015 | Unit semantic/selector/freshness rules; integration through each adopted public mutation/admission entry point, including stale inputs and pre/action/post/publication ordering; UI conflict/decision journeys for the exposed behavior. |
| EM-003/011 | Unit identity and integrity counterexamples; integration through the existing nonmutating authority and revisioned sources; browser inspection of helpers, outcomes and historical/unavailable states. |
| EM-004 | Integration through the public CLI for shared JSON/Markdown identity, guarded edits, errors and reload persistence. |
| EM-005/009/010 | AppTest integration plus real-browser journeys for direct entry, missing context, shared Task/Back behavior, exact summary records and current/historical decision restrictions. |
| EM-012 | Structural lazy-loading/cache checks and a real-browser benchmark/accessibility exercise using the existing sampling/budget obligations; AppTest alone cannot establish browser timing, focus or narrow-layout behavior. |
| EM-013/018 | Resolver unit cases and integration through actual fresh intake, including explicit/recorded/conflicting/unavailable subjects, repository ownership and inspection with no external-service dependency or writes. |
| EM-016/017 | Real representative browser journey with genuine retained evidence, plus the bound human comprehension record; integration checks preserve original historical records and explicit historical access while removing the old main-pilot presentation. |

All 18 criteria use `verification_mode: tests`. No review-only exception is
requested or granted. The human exercise supplements execution and semantic
review; it cannot replace either. Exact per-criterion required types, cases,
assertions and TaskGraph scopes must receive independent review and a new
coordinator pin under `_ask/docs/spec-test-traceability.md` before implementation.
New/changed behavior needs genuine assertion red and final green. Unchanged
baseline regressions need current execution; shared criterion IDs do not transfer
old completion, accepted pins or approvals.

The baseline's guard, dependency invalidation, CLI parity, evidence authority,
decision protections and historical inspection remain obligations (`spec.md:24`).
Implementation must preserve them while adding the new behavior. The current
source's lack of v2/context-intake support is expected implementation work, not
evidence that the proposed requirement is contradictory.

## Recommended clarifications

No product clarification or acceptance-criteria change is required for this
challenge to pass. Severity: no blocking findings.

Future Plan should record the concrete selector grammar and action-to-passage
dependencies, actual coordinator intake caller, v2 migration/registration steps,
exact case/type mapping, and comprehension-record format. These choices must
implement the already specified behavior. If they require changing that behavior
or weakening preserved obligations, use Spec Change and renewed independent
review. Missing current intent confirmation, future contracts, migration or
implementation evidence does not by itself invalidate this specification-only
review.

## Challenge verdict

**PASS** for the exact revision 2 input digests above. No concrete counterexample
was found that the requirements permit while defeating the stated Why.

Eligible for the parent's acceptance of the specification after the applicable
human confirmation. This decision does not close Grill or Accept, promote the
specification, approve a future test plan, authorize implementation, certify the
representative demonstration, or advance accepted refs.
