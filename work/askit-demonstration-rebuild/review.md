# Independent review: AskIt demonstration rebuild

## Verdict

**PASS**

Candidate: `cfa06aabcf4f060a0b6ab4b39f56d0eb669d4fff`
Accepted contract base: `63c377abd7764c689653d16a35baf25d9217e5c1`
Baseline: `2e5ea92989c48c10e4829bc22c325643443a38b3`

The two findings from the prior review are fixed. The corrected candidate
provides per-artifact saved-source paths and last-changing SHAs, and both
guides now inventory the directly cited workflow-reference and worktree-policy
sources. No remaining blocking finding was identified.

## Criterion-by-criterion findings

| Criterion | Decision | Finding |
| --- | --- | --- |
| DOC-001 | PASS | Both requested guides exist. Each has exactly `ORIENT`, `MODEL`, `ROUTE`, `WALKTHROUGH`, `EVIDENCE`, `RECOVERY`, `ADOPT`, `CLOSE` in that order, with matching session-map outcomes. |
| DOC-002 | PASS | Both guides provide the required opening, model, lifecycle walkthrough, evidence/recovery treatment, adoption exercise, and close. |
| DOC-003 | PASS | Every section has cue card, presenter notes, internal timing, and outcome. The eight allocations are `8+12+10+20+12+10+10+8 = 90` in both guides. |
| DOC-004 | PASS | Inventory keys `E-01`, `E-02`, `E-03`, `E-04a`, `E-04b`, `E-04c`, `E-05`, `E-06`, and `E-07` are unique in both guides and each has exactly one `LIVE`, `SAVED`, or `OPTIONAL` label. SAVED rows identify artifact paths and per-artifact last-changing SHAs: `AGENTS.md` at `8f39ecd5f58c9c38def247007c1365c4036052bd`; `.agents/ask/stages/` at `bc0f332cc7f7ea952a48a2cab9394ef59d0d47bb`; delegation/workflow policies at `336133642b08440a5fbc33f1863699febbb6bb16` and `bc0f332cc7f7ea952a48a2cab9394ef59d0d47bb`; and traceability documentation at `a3e2c6932dad29faf44ec6cbce13770f51d460ec`. LIVE instructions remain explicitly non-execution claims. |
| DOC-005 | PASS | Every citation inventory row names an existing path, a passage to inspect, and `SUPPORTED`. The inventories include `README.md`, `AGENTS.md`, workflow/delegation policies, demo lifecycle, traceability, `_ask/docs/workflow-references.md`, `_ask/policies/worktree.md`, and canonical stage sources in both languages. |
| DOC-006 | PASS | The parity record covers all seven required dimensions and marks every one `MATCH`: section IDs/order, outcomes, timing, lifecycle, evidence labels, ownership, and primary/optional status. Direct comparison supports those matches. |
| DOC-007 | PASS | Physical `wc -l` counts including blank lines: English `721 → 353` (51.04% reduction); Persian `773 → 336` (56.53% reduction). The safety checklist preserves model, human ownership, evidence discipline, recovery/refusal, and failure boundaries. |

## Additional checks

- **Primary versus optional:** The bounded lifecycle walkthrough is explicitly
  the main demonstration; the two-moons experiment and shorter-hashes clinic
  are explicitly optional, with the historical clinic marked non-primary.
- **Unsupported execution claims:** No command is presented as already run.
  The walkthrough is labeled `LIVE`; optional material is labeled
  unexecuted or historical.
- **Candidate scope:** `git diff --name-only cfa06aa^ cfa06aa` contains only
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
