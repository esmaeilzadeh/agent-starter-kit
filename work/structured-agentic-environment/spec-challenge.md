# Specification Challenge

## Model

- Reviewer: `/root/spec_challenge_sol`, independent child with a clean context.
- Runtime: `codex`; model: `gpt-6.1-sol`; reasoning effort: `high`.
- Parent model: GPT-6-family Codex; its exact model identifier is unavailable. No exact identifier is inferred.
- Independence: context independence within the same GPT family, not cross-family diversity. The human explicitly selected Sol/high and confirmed continuation after the same-family warning. That choice overrides the generated Astra default; no second challenger was spawned.
- Authority: review and this report only. No implementation, Plan, specification promotion, acceptance, machine APPROVED decision or accepted-ref advancement is authorized by this challenge.
- Method: prepared `writing-for-agents` skill in embedded mode; stage 03 contract and repository delegation/verification policies.

## Specification

Reviewed source commit: `c988ea493be3136493dfb9b5eefdbb5d7721f238`.
The exact target bytes declare **PROPOSED revision 4**, relative to accepted
revision 3. The initial dispatch's revision-3 shorthand does not change the target.

| Input | Exact SHA256 |
| --- | --- |
| `specs/proposals/structured-agentic-environment.md`, file bytes | `48f23f757ce963998f45b2d953004e7164da515ae9b52f8d9954e9189cfbd9d8` |
| `specs/proposals/structured-agentic-environment.json`, file bytes | `b8fe01ea4dc5089a5374b3847b17d3b256adffa6069d7177fe76ade81427037c` |
| Proposed JSON, canonical sorted compact JSON | `ac839eff7893379eea48d97a8f454f69d8306ec3c3ab2e0fd7198d8f573a4af3` |
| `work/structured-agentic-environment/intent.md`, file bytes | `d05dabe7f4edbdfe91f1d282fdea42791a7ae8852297c4dcfc6cf417c084bb8e` |

Canonical hashing used parsed JSON, UTF-8, sorted keys, separators `(',', ':')`
and `ensure_ascii=False`. The proposal's prose and JSON were reviewed together.
Supporting context: `spec-change-context-first.md`, `GLOSSARY.md`, current revision-3
specification, design, plan, test plan, accepted pin, Engineering Model, and relevant
validator/snapshot/workbench/workflow/source/evidence code. These supporting
artifacts are context, not newly approved obligations.

The clean-tree gate passed at the reviewed commit. The previous challenge was
byte-identical to `spec-challenge-r3-historical.md` before replacing this report.
That historical approval remains about its original source and contract digests;
it does not approve revision 4.

## Ambiguities

### F1 — P1: A concrete Scenario has no selectable flow authority

**References:** `specs/proposals/structured-agentic-environment.md:19`, `:27`,
`:59`, `:87`; `specs/proposals/structured-agentic-environment.json:61`–`:70`.
The current projection's relevant join is
`_ask/scripts/engineering_model/workbench.py:59`–`:80`.

**Trigger:** Author separate Scenarios for a successful decision submission and a
stale submission. Both reference EM-007, whose canonical Given/When/Then combines
current/candidate state, external saves, concurrency and all public entry points.
One test checks successful publication; another checks stale rejection.

**Bad behavior permitted:** Each Scenario can display the same broad criterion as
its complete flow, and both tests can appear related to both Scenarios merely
because their criterion IDs match. The current projection already performs that
criterion-to-all-matching-Scenarios join. Unique Scenario titles and explicit
`covers` edges do not resolve the competing inferred association. The definition
contract references only a criterion, while forbidding a second editable
Given/When/Then authority. Consequently, two purported concrete flows need not
have independently selectable context/action/outcome or truthful flow-level test
associations. Preserving execution ownership does not solve this display problem.

**Required decision:** Define the canonical owner and stable selector for each
concrete flow, and the rule distinguishing criterion-related tests from tests
that cover that flow. An existing canonical test-plan case's `scenario` is one
possible source; another reviewed canonical example representation is possible.
Preserve criterion IDs and historical attribution. Require a counterexample in
which two distinct flows share a criterion and a test for one is not represented
as proving the other. This is a semantic decision, not a demand for a particular
schema field or testing syntax.

### F2 — P1: Passage failure has conflicting admission semantics

**References:** `specs/proposals/structured-agentic-environment.md:23`, `:43`–`:47`,
`:89`–`:91`; `specs/proposals/structured-agentic-environment.json:147`–`:154`.

**Trigger:** A valid current Task points to heading `Delivery / Evidence`. A
specification edit duplicates that heading path, or renames/deletes the selected
passage while leaving the Task reference unchanged.

**Bad behavior permitted:** One implementation rejects the whole current snapshot
as a broken/ambiguous reference and cannot open the selected current Task; another
admits it and shows unavailable context. The prose says to reject ambiguous
selectors, while EM-015 permits displaying missing/ambiguous context. The guard
also prohibits using invalid current state as actionable input. A last-validated
view does not by itself define how the newly missing or ambiguous context is
inspected or repaired. These choices affect unrelated work admission as well as
the returning human's ability to recover context.

**Required decision:** Classify unsafe paths, malformed selectors, multiple
matches, zero matches and absent optional references separately. State which
invalidate admission and which are admitted unavailable context, what inspection
is permitted for an invalid current document, and which actions remain blocked.
Keep explicit repair/import and stale-generation labeling. Test both inspection
and action admission for the same missing/ambiguous input; a UI-only warning test
cannot settle this invariant.

### F3 — P1: Request-entry behavior lacks an owning public caller

**References:** `specs/proposals/structured-agentic-environment.md:49`, `:65`,
`:79`–`:83`; `specs/proposals/structured-agentic-environment.json:127`–`:134`;
`work/structured-agentic-environment/intent.md:22`–`:30`.

**Trigger:** From `develop`, a new chat requests a contribution to an existing
Story and supplies a later-card reference. No work is yet selected. Alternatively,
the chat begins on an execution branch but explicitly names a different existing
Task. The normal chat workflow must establish a subject before recording intent
or admitting delivery work.

**Bad behavior permitted:** A standalone resolver can pass EM-013 tests without
being called by the actual chat/coordinator entry. The workbench can correctly open
explicit subjects while the agent still takes the branch's work as product scope
or creates a new identity. The enumerated public callers concern editing and
workflow admission, not request-context resolution. “Beginning adopted work” also
leaves unclear who discovers adoption before a subject/workstream has been chosen.
Excluding general Explore/Grill improvements is appropriate, but does not assign
this adopted entry behavior to a concrete caller.

**Required decision:** Name the adopted request-entry boundary, its responsible
caller, the explicit/current/recorded-context precedence, and where subject
resolution must occur relative to branch creation, intent recording and work
admission. Define the observable result for inspection-only entry and conflicting
subjects. Require evidence through that caller, including a fresh chat/context
case, rather than only a pure resolver or UI test. Keep general omission-discovery
protocol improvements outside this amendment.

### F4 — P2: Model, execution and external item identities need an explicit relation

**References:** `specs/proposals/structured-agentic-environment.md:17`, `:21`,
`:79`–`:83`; `specs/proposals/structured-agentic-environment.json:77`, `:131`.
Current model-node IDs use slugs (`_ask/scripts/engineering_model/validation.py:49`),
while the real execution graph uses `WB-003`
(`work/structured-agentic-environment/inner-loop/tasks.yaml:33`).

**Trigger:** The model node `bind-test-details` represents execution Task
`(structured-agentic-environment, WB-003)`. A later card and supplied tracker item
also refer to that work. A second Story links to it, or another execution
workstream requests a contribution to the same existing product item.

**Bad behavior permitted:** “One qualified identity” can mean the model-node pair,
the TaskGraph pair, or the tracker identity. Two model aliases can point to one
execution Task without a specified canonical display/counting rule; a node's local
lifecycle can disagree with the execution Task despite the prohibition on a second
status authority. Conversely, equal-looking IDs can be silently used as a join.
The spec does not state whether cross-model support is legal, or whether the user
must select the owning model without cloning the item. None of these choices
requires Jira integration, but they change the meaning of identity reuse.

**Required decision:** Distinguish product item, local model record, execution
Task and external/later reference identities. Define alias uniqueness, authoritative
status dimensions and cross-model resolution behavior. Either bound support edges
to one model with explicit foreign-item resolution, or specify qualified external
endpoints and their revision rules. Resolve missing/conflicting targets explicitly;
do not demand cross-workstream writes or tracker APIs as an incidental solution.

## Missing failure cases

### F5 — P1: The one complete real demonstration is deferred and can remain incomplete

**References:** `specs/proposals/structured-agentic-environment.md:101`–`:109`;
`specs/proposals/structured-agentic-environment.json:157`–`:164`;
`work/structured-agentic-environment/intent.md:126`–`:128`.

**Trigger:** Implement the proposed Story with an arbitrary real Task, display a
generic criterion and future plan placeholder, and show unavailable for every
retained outcome. Automated fixture journeys all pass and fixture labels are honest.

**Bad behavior permitted:** EM-016 expressly allows results only “when available,”
so it can pass without one complete real Task-to-Test-to-outcome example. The prose
says unavailable evidence cannot pass the executed-result portion, but no concrete
example, availability assessment or completion rule establishes that portion. Line
109 defers even the real selectors, despite the intent saying specification will
propose them. This is the same core usability assumption the real Story was meant
to test, not merely an absent future test-plan mapping.

**Required decision:** In the specification, select one existing Task, concrete
flow, test selector, main-spec passage and plan entry, and identify the retained
candidate/run records to inspect or the exact missing evidence. For example, the
repository contains WB-003 and a retained task-result record naming three cases
and red/final-green runs
(`work/structured-agentic-environment/inner-loop/results/WB-003.json:3`–`:33`);
that is a candidate to assess, not validated execution evidence from this review.
Define whether at least one genuine retained result is required for the complete
demonstration. If none is available, name that unresolved prerequisite or obtain an
explicit scope decision. Keep fixture-based automation and missing-evidence
counterexamples; neither substitutes for the representative real example. Exact
future task/test inventories remain Plan work.

### F6 — P2: Readability review has no candidate-bound success/failure disposition

**References:** `specs/proposals/structured-agentic-environment.md:95`–`:99`,
`:146`–`:149`; `specs/proposals/structured-agentic-environment.json:111`,
`:157`–`:164`.

**Trigger:** A selected test calls a fixture that imports a helper/global from a
second module. The panel contains the test method, one helper and readable prose,
but the human cannot explain which input the fixture supplies or what the assertion
establishes. Automated source/mapping checks pass; the review records that failure.

**Bad behavior permitted:** Recording the readability exercise can be treated as
completion even when its main objective failed. There is no explicit disposition
for failed identifications or requirement to bind the exercise to the inspected
candidate, selected examples and helper-source revisions. A review of one candidate
can therefore be reused after relevant helper/context edits, or a failing exercise
can coexist with all JSON criteria reporting tested success. Same-revision source
alone does not establish that all necessary fixture/import/comment context was
included.

**Required decision:** State the required successful identifications, record the
candidate/snapshot and selected Task/Scenario/Test/helper sources, and define how
unresolved comprehension failures block the representative demonstration or require
a human scope decision. Require relevant context changes to invalidate that review.
Permit explicit curated helper references; no general whole-program analyzer is
required. Retain automated tests and actual execution requirements. If any criterion
becomes review-only, require its reason and attributable independent APPROVED
authority under the existing policy; this report supplies no such approval.

## Over-constraint risks

The v2 migration must change version-specific expectations rather than attempt to
make one document satisfy incompatible v1/v2 parent rules. The accepted `MV-valid`
case explicitly asserts that missing intent rejects
(`work/structured-agentic-environment/test-plan.json:103`–`:114`), whereas v2 makes
intent optional. The proposal already requires reviewed migration and task/test
updates, so this is a transition obligation, not an additional blocker or a request
to change accepted tests now. Keep historical v1 validation and evidence attribution.

Broadening guard inputs to passage/context references can block an entire adopted
workstream when one optional context reference breaks. F2 requires an explicit
classification; neither silently weakening the guard nor treating every context
limitation as a fatal schema error is an approved default.

## Under-constraint risks

The proposal correctly prohibits fabricated ancestors, competing evidence authority,
automatic migration and Jira integration. Those boundaries do not themselves prove
correct flow association (F1), invocation of the request-entry contract (F3), or a
complete comprehensible real example (F5/F6). In particular, precise IDs and honest
unavailable labels can all be present while the returning human's central job fails.

## Recommended clarifications

Resolve F1, F2, F3 and F5 before treating this specification as ready for acceptance
or deriving an implementation plan. Resolve F4/F6 as explicit identity and evidence
rules rather than leaving implementations to choose incompatible meanings.
Re-challenge amended prose and JSON at new exact digests.

The one-Scenario-per-Story interpretation is explicitly an unconfirmed assumption
in `intent.md:121`–`:123`; this review does not convert it into a human decision.
Complete-intent confirmation remains pending, but that does not invalidate the
explicitly authorized drafting and challenge or constitute the verdict by itself.

### Future test obligations and independent authority

No revision-4 test plan or accepted mapping exists, and this report approves none.
The following are required categories to examine during independent Plan review,
not invented accepted case assignments:

- Unit checks for v2 graph/cardinality, version dispatch, qualified identities,
  selector classification and flow-specific association.
- Integration checks through the shared document guard and actual request-entry
  caller for linked-text-only changes, missing/ambiguous passages, alias conflicts,
  snapshot dependency discovery, helper/context revisions and no-write inspection.
- Streamlit AppTest plus real temporary-browser E2E for direct Story/Task entry,
  standalone/Story-less records, shared Task navigation and Back context, source/
  evidence applicability, the representative journey and preserved historical
  harness inspection. Pure graph tests cannot establish those public journeys.
- A recorded candidate-bound human readability exercise alongside automation.
  Automated presence-of-text checks cannot stand in for successful comprehension.

Keep the existing genuine red/final-green and independent semantic-review rules
for new/changed behavior. Determine concrete migration, task ownership, cases,
required-type mappings and any reviewed runner amendment in the future Plan;
preserve current accepted authority until that transition is reviewed and pinned.

## Challenge verdict

**ESCALATE** for the exact proposal Markdown and canonical JSON digests recorded
above. F1/F2/F3/F5 require specification decisions; F4/F6 require clarification.
This is an independent specification decision, not a plan-review APPROVED record.
No accepted reference was advanced and no current contract was replaced.

Limits of review: repository/source inspection and digest/cleanliness checks only.
No product implementation, tests, browser session, benchmark, acceptance or runtime
completion evaluation was executed. Retained task-result records were read as
context and not independently certified; local run/log availability and original
accepted authority for the selected real demonstration still need assessment.
No claims about current feature behavior or comparative usability follow from this
review. The historical challenge remains preserved separately.
