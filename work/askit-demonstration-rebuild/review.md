# Independent review: AskIt demonstration rebuild

## Verdict

**FAIL**

Candidate: `2ed93a92db5925fe17ba759dd11b321c10eb2e5a`
Accepted contract base: `63c377abd7764c689653d16a35baf25d9217e5c1`
Baseline: `2e5ea92989c48c10e4829bc22c325643443a38b3`

The candidate satisfies the structural, timing, compression, parity, primary-path,
boundary-preservation, and production-scope requirements. It fails the evidence
provenance and citation-inventory requirements:

1. `E-04` and `E-05` label rows as `SAVED` and cite `484bf94`, but that commit
   only adds `work/askit-demonstration-rebuild/traceability-accepted.json`; it
   does not produce or last change the listed saved sources. For example, the
   last-changing commits are `8f39ecd5f58c9c38def247007c1365c4036052bd`
   (`AGENTS.md`), `336133642b08440a5fbc33f1863699febbb6bb16`
   (`_ask/policies/delegation.md`), and
   `a3e2c6932dad29faf44ec6cbce13770f51d460ec` (`_ask/docs/spec-test-traceability.md`).
   `E-04` also groups multiple directories/files under one SHA rather than
   identifying each saved artifact's provenance.
2. The presenter notes directly cite `_ask/docs/workflow-references.md` in the
   EVIDENCE section and `_ask/policies/worktree.md` in RECOVERY, in both
   languages, but neither path has a citation-inventory row with a passage and
   `SUPPORTED` decision. The seven listed citation paths do exist and their
   listed decisions are `SUPPORTED`; the inventory is nevertheless incomplete
   for all cited workflow claims.

## Criterion-by-criterion findings

| Criterion | Decision | Finding |
| --- | --- | --- |
| DOC-001 | PASS | Both requested guides exist. Each has exactly `ORIENT`, `MODEL`, `ROUTE`, `WALKTHROUGH`, `EVIDENCE`, `RECOVERY`, `ADOPT`, `CLOSE` in that order, with matching session-map outcomes. |
| DOC-002 | PASS | Both guides provide the required opening, model, lifecycle walkthrough, evidence/recovery treatment, adoption exercise, and close. |
| DOC-003 | PASS | Every section has cue card, presenter notes, internal timing, and outcome. The eight allocations are `8+12+10+20+12+10+10+8 = 90` in both guides. |
| DOC-004 | FAIL | Inventory keys `E-01` through `E-07` are unique and each is labeled `LIVE`, `SAVED`, or `OPTIONAL`; LIVE material is explicitly non-execution. However, the SAVED rows do not provide valid producing/last-changing provenance for their cited artifacts: both use `484bf94`, which did not change those artifacts. |
| DOC-005 | FAIL | All seven listed citation paths exist and have passage descriptions plus `SUPPORTED` decisions. The inventory omits the directly cited `_ask/docs/workflow-references.md` and `_ask/policies/worktree.md`, so it does not record support decisions for every cited workflow source. |
| DOC-006 | PASS | The parity record covers all seven required dimensions and marks every one `MATCH`: section IDs/order, outcomes, timing, lifecycle, evidence labels, ownership, and primary/optional status. Direct comparison supports those matches. |
| DOC-007 | PASS | Physical `wc -l` counts including blank lines: English `721 → 349` (51.60% reduction); Persian `773 → 332` (57.05% reduction). The safety checklist preserves model, human ownership, evidence discipline, recovery/refusal, and failure boundaries. |

## Additional checks

- **Primary versus optional:** The bounded lifecycle walkthrough is explicitly
  the main demonstration; the two-moons experiment and shorter-hashes clinic
  are explicitly optional, with the historical clinic marked non-primary.
- **Unsupported execution claims:** No command is presented as already run.
  The walkthrough is labeled `LIVE`; optional material is labeled
  unexecuted or historical. No runtime test evidence is asserted by this
  review.
- **Candidate scope:** `git diff --name-only 2ed93a9^ 2ed93a9` contains only
  `docs/AskIt-demonstration-notes.md` and
  `docs/AskIt-demonstration-notes-fa.md`.
- **Canonical contract identity:** The canonical spec digest is
  `bcb2fbcb507eb9a1a53e789f1630d6f9fb799e5845fff09263ea43ed28bb5ed3`.
  The canonical plan digest is
  `21a01aab9822ae463fda87a71061a7b05ddd6cc1a81db833c734a85a821fbbe5`.
  The accepted plan declares executable tests empty, so this is a review-only
  assessment; no fabricated test cases or runtime results are included.

## Inspected sources

- `specs/current/askit-demonstration-rebuild.md`
- `specs/current/askit-demonstration-rebuild.json`
- `work/askit-demonstration-rebuild/plan.md`
- `work/askit-demonstration-rebuild/test-plan.json`
- `work/askit-demonstration-rebuild/traceability-accepted.json`
- `README.md`
- `AGENTS.md`
- `_ask/policies/workflow.md`
- `_ask/policies/delegation.md`
- `_ask/policies/worktree.md`
- `_ask/docs/demo/end-to-end-plan.md`
- `_ask/docs/spec-test-traceability.md`
- `_ask/docs/workflow-references.md`
- `.agents/ask/stages/`
- `docs/AskIt-demonstration-notes.md`
- `docs/AskIt-demonstration-notes-fa.md`
