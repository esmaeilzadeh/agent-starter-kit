# Specification Challenge

## Model

model=opus; runtime=claude; parent_model=unknown.

This is the independent rerun for `askit-demonstration-rebuild` at contract
commit `9ef3a3e1977470df5ae6e45a00cdce298c77ab8f`. The prior challenge is the
artifact committed at `3f4d8ad960c3d1ea2a67e263494a0c8890d65ad5`. The requested
Opus model is the configured Claude adversarial binding; no parent-model
identity was available. This review did not edit production documentation or
invent approval.

## Specification

Reviewed the updated intent, canonical JSON and Markdown specification,
test-plan, plan, task graph, engineering model, prior challenge, and the
relevant protocol/authority documents:

- `work/askit-demonstration-rebuild/{intent.md,plan.md,test-plan.json,inner-loop/tasks.yaml,engineering-model.json,spec-challenge.md}`
- `specs/current/askit-demonstration-rebuild.{json,md}`
- `_ask/docs/spec-test-traceability.md`
- `_ask/policies/{delegation,verification,workflow}.md`
- `_ask/docs/demo/end-to-end-plan.md`, `README.md`, and `AGENTS.md`
- baseline production notes `docs/AskIt-demonstration-notes.md` and
  `docs/AskIt-demonstration-notes-fa.md`, only for baseline/verification

The canonical spec digest is
`1ee038693c4765dd7d7bfd254662c4a7a26fc6e36638a4e325358dbdd23db1a1`.
The updated test-plan digest is
`9da9facd33e619538946d0ad059834d5ee69138a2ba1ed8da55fdf4f339a3282`; the
engineering-model digest is
`b2745a59031139556a5e5eff9f667bce90e90df9deeb55680faf0e73f2004602`.

The update resolves several findings from the prior challenge: the required
fixed IDs/order are now explicit
(`ORIENT`, `MODEL`, `ROUTE`, `WALKTHROUGH`, `EVIDENCE`, `RECOVERY`, `ADOPT`,
`CLOSE`); internal timing is stated as an exact 90-minute sum while audience
cue cards need not show duration; the 35% language-specific line reduction is
explicit; labels, citation-review fields, and parity dimensions are named; and
the plan now attempts criterion-level mappings.

The production baseline is 721 English lines and 773 Persian lines at
baseline source commit
`2e5ea92989c48c10e4829bc22c325643443a38b3`. No
`work/askit-demonstration-rebuild/traceability/` evidence or
`refs/ask/accepted-tests/askit-demonstration-rebuild` authority ref exists.

## Ambiguities

1. **Target versus canonical duration.** The intent and specification prose
   call the session “approximately 90 minutes,” while the canonical criterion
   and test case require an exact eight-section sum of 90. The intended rule
   appears to be “approximately 90 for the audience; exactly 90 in the
   facilitator schedule,” but that distinction should be stated once as the
   acceptance rule. Otherwise a 89- or 91-minute schedule can be defended by
   the prose despite failing the intended internal contract.

2. **Saved-evidence SHA semantics.** The updated criterion says a `SAVED` row
   names a path and a relevant SHA “when applicable,” while the requested
   contract requires saved rows to identify path and relevant SHA. “Relevant”
   and “applicable” are not defined: source commit, workstream commit, and
   artifact-producing commit are different claims. Define the row schema and
   require a specific SHA rule, or explicitly enumerate the exceptions.

3. **Baseline and line-count method.** “Current-language baseline” is not
   pinned in the test plan, and line count does not say whether blank lines,
   headings, and the final newline count. Once the two production files are
   replaced, “current” can move. The baseline paths and commit above, plus a
   deterministic counting rule, need to be part of the accepted evidence.

4. **Outcome and inventory identity.** “Matching session outcomes” has no
   canonical list, and “every command, result, historical example, and
   optional activity” has no item identity rule. A command repeated in
   presenter prose and an evidence table could receive two labels or none
   unless the inventory row is the authority and each item has a stable key.

5. **Citation and parity record shape.** The criteria require a citation path,
   relevant heading/excerpt, support decision, and seven parity dimensions,
   but do not define allowed decision values or where the records live. A
   reviewer could produce incompatible “supported” and “yes” records and
   both appear compliant.

## Missing failure cases

- **The updated contracts do not validate.** Running
  `./ask traceability validate-plan askit-demonstration-rebuild
  --revision 9ef3a3e` fails with `unauthorized_review_only` for every
  `DOC-001`–`DOC-007`, then `invalid_obligation` and `invalid_required_types`
  for those same obligations, plus `invalid_test_type` and
  `invalid_runner_case` for `DOC-001-R`–`DOC-007-R`. The validator permits
  executable types `unit`, `integration`, and `e2e`; `review` is not a test
  type. Review-only criteria instead require a reason and an attributable
  `APPROVED` decision under `_ask/policies/delegation.md`. This is a
  blocking authority/traceability defect, not merely missing runtime evidence.

- **DOC-002 mapping drops recovery.** The canonical criterion requires
  “evidence and recovery,” but `DOC-002-R` checks
  `opening/model/route/walkthrough/evidence/adoption/close` and omits an
  explicit recovery assertion. A guide can therefore pass the mapped case
  while omitting the RECOVERY teaching beat.

- **DOC-007 mapping is not exhaustive.** Its generic “safety checklist” does
  not enumerate the required preservation checks for core model, ownership,
  evidence, recovery, and failure boundaries. It does not establish which
  omitted boundary is a failure.

- **Reduction cannot be reproduced from the test plan.** `DOC-007-R` names
  only the rebuilt files as `source_paths`, not the pinned English/Persian
  baselines or a count procedure. A later reviewer cannot distinguish a
  genuine 35% reduction from a changed baseline.

- **Label and citation counterexamples remain admissible.** A row can label
  an item `SAVED` without a SHA under the undefined “when applicable”
  exception; a citation can name an existing but unrelated path; and a
  repeated command can have conflicting labels. The plan has no explicit
  duplicate/conflict or stale-source failure assertion.

- **Review authority is absent.** There is no plan-review decision, accepted
  traceability pin, or independent semantic-review record for these exact
  contract digests. The worker-authored challenge cannot supply that
  coordinator authority.

- **Intent authority is stale.** `intent-confirmation.json` records digest
  `777e4ed...`, while the committed current `intent.md` hashes to
  `76c299a...`; `./ask check-workstream askit-demonstration-rebuild` reports
  that the intent changed after confirmation. Implementation/acceptance must
  not treat the earlier approval as approval of the updated intent.

## Over-constraint risks

- Requiring identical English/Persian prose or line-by-line translation would
  contradict the natural-Persian requirement. Parity should remain
  dimension-by-dimension and meaning-based.
- Requiring every command to be executed live would contradict the explicit
  `SAVED` and `OPTIONAL` modes and the no-benchmark/no-new-artifact
  non-goals.
- Requiring preservation of the old 40-slide structure would undermine the
  Why. The fixed eight-section contract and safety checklist are the better
  boundary.
- An exact internal 90-minute sum is appropriate for a facilitator schedule,
  but should not be read as requiring audience cue cards to display duration;
  that audience-facing exemption is explicitly intended and should remain.

## Under-constraint risks

- The canonical criteria are all `verification_mode: "review"` but lack the
  required per-criterion `reason` and attributable `review_decision`. Adding
  a review-shaped test plan does not authorize them.
- The test plan conflates review-only decisions with executable tests. It has
  no supported runner/case for these review entries and therefore cannot be
  accepted or pinned by the traceability validator.
- The parity checklist names the right dimensions but does not require an
  explicit result for each language pair, including lifecycle and
  primary/optional status.
- Citation review is not bound to a complete claim inventory, so “important”
  claims can be omitted from review. The inventory must cover every cited
  workflow/evidence claim, not only the paths a reviewer happens to notice.
- Migration scope says the two Markdown files are deliverables but does not
  explicitly state whether indexes, links, or the PPTX files are intentionally
  unchanged. Leaving this implicit risks either stale navigation or unrelated
  documentation cleanup.

## Recommended clarifications

1. **Repair the review-only contract before implementation.** Add a reason and
   an attributable `APPROVED` review decision (with policy, reviewer, and
   recorded-by fields) for each review-only criterion, or change the criteria
   to an actually supported verification mode. Remove `review` obligations
   and pseudo-tests from `test-plan.json`; review-only criteria may have empty
   executable cases, but still require independent semantic review. Do not
   fabricate the approval in this challenge.

2. **Create and pin authority through the coordinator.** Recompute the exact
   spec/plan/task-graph/delegation digests after the contract repair, obtain
   the independent `decision: APPROVED` plan-review record, run
   `accept-plan`, and commit the resulting accepted pin. The challenge verdict
   is not that approval.

3. **Make the acceptance language deterministic.** State: “The session target
   is approximately 90 minutes; the eight internal numeric timings must sum
   exactly to 90 minutes. Cue cards need not display duration.” Define the
   outcome list, item-key rule, allowed labels, and the exact `SAVED` path/SHA
   rule.

4. **Pin baseline evidence.** Record both baseline paths, commit
   `2e5ea92989c48c10e4829bc22c325643443a38b3`, the counting command/rule, and
   the 35% calculation in the review obligation. Keep the baseline as
   verification history after the production files are replaced.

5. **Tighten the review mappings.** Add an explicit RECOVERY assertion to
   `DOC-002-R`; expand `DOC-007-R` into five named safety assertions; and
   require one decision per parity dimension and one row per cited claim.
   Record citation support as a bounded value such as `SUPPORTED` or
   `UNSUPPORTED`, including the relevant heading/excerpt.

6. **Bound migration.** State that only the two requested Markdown files are
   production deliverables; PPTX files and unrelated indexes/links remain
   unchanged unless a separately approved scope change identifies a broken
   reference. Record the old files' commit as baseline rather than silently
   deleting historical context.

7. **Renew intent confirmation.** Obtain confirmation against the current
   `intent.md` digest before implementation. Preserve the submitted choice
   and exact digest; do not infer renewed approval from the prior
   `intent-confirmation.json`.

## Challenge verdict

**ESCALATE.**

The What/Why and the requested eight-section teaching contract are coherent,
and the update resolves the prior challenge's major content ambiguities.
However, the exact updated contracts fail the repository's traceability
validator because review-only criteria are missing their required authority
metadata and are incorrectly represented as unsupported `review` tests. The
timing/baseline/label inventory details and two incomplete test mappings leave
acceptance reproducibility open as well. Human/coordinator decisions and a
repaired, independently accepted contract pin are required before
implementation or acceptance. No approval is implied by this artifact.
