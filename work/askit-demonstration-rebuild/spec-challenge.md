# Specification Challenge

## Model

model=opus; runtime=claude; parent_model=unknown.

This is the independent Spec Challenge review for
`askit-demonstration-rebuild`. The requested Opus selection was recorded; no
parent model identity was available to establish. The review followed the
stage contract, the spec/test traceability contract, and the embedded
`writing-for-agents` guidance. No production documentation was edited and no
approval was invented.

## Specification

Reviewed:

- `specs/current/askit-demonstration-rebuild.md`
- `specs/current/askit-demonstration-rebuild.json`
- `work/askit-demonstration-rebuild/intent.md`
- `work/askit-demonstration-rebuild/plan.md`
- `work/askit-demonstration-rebuild/test-plan.json`
- `work/askit-demonstration-rebuild/inner-loop/tasks.yaml`
- `docs/AskIt-demonstration-notes.md`
- `docs/AskIt-demonstration-notes-fa.md`
- `AGENTS.md`, `README.md`, `_ask/docs/demo/end-to-end-plan.md`,
  `_ask/policies/{delegation,workflow}.md`, and
  `_ask/docs/spec-test-traceability.md`

The canonical spec contains the exact criteria `DOC-001` through `DOC-007`,
all marked `verification_mode: "review"`. The canonical spec digest is
`f4126d944d1308a4844ffde6aa91b097768271687b292e2d20e4cf674a20eb15`.
The current test-plan digest is
`0cddbc2f440c4b3584c915090b223c220fa4c7670aea7744ddad9b116b67576e`; its
engineering-model digest is
`b2745a59031139556a5e5eff9f667bce90e90df9deeb55680faf0e73f2004602`.

## Ambiguities

1. **Section identity and scope are undefined (`DOC-001`, `DOC-003`).**
   The spec requires matching ordered “section IDs” and says every section
   needs four fields, but does not define the ID syntax, the authoritative
   section set, or whether preparation, references, appendices, and closing
   checks count. A guide can satisfy the headings informally while English
   and Persian differ in a non-obvious subsection.

2. **The 90-minute requirement has two possible truths.** The Goal and intent
   describe a 90-minute session, while the intent permits a shorter session if
   that is “more honest,” and the spec only says the total must remain
   explicit and coherent. There is no decision rule for choosing 90 minutes
   versus another duration, nor a tolerance for rounding. A schedule can
   total 89, 90, or 95 minutes and still be arguable under the current text.

3. **“Important,” “supports the claim,” “substantially shorter,” and “easier
   to scan” are not observable bounds (`DOC-005`, `DOC-007`).** Existence of a
   cited path does not show that the cited source supports the adjacent
   statement. Likewise, the current English and Persian notes are 721 and 773
   lines; “materially/substantially shorter” has no threshold, baseline
   measure, or required scanability test.

4. **Demonstration-label coverage is underspecified (`DOC-004`).** The
   requirement names `live`, `saved evidence`, and `optional`, but does not
   define the label format or require an inventory of every command, result,
   historical example, or hypothetical instruction. A sentence such as “run
   `./ask verify`” can be read as a recommendation or as an executed fact.

5. **Semantic parity lacks a review protocol (`DOC-006`).** “Same outcomes and
   lifecycle” does not identify the parity dimensions to compare, how timing
   and evidence labels are paired, or what degree of natural-language
   variation is acceptable. The existing files already show different
   non-slide sections, so heading-number parity alone would be insufficient.

## Missing failure cases

- A cited source exists but is stale, unrelated, or does not support the
  statement; `DOC-005` currently tests path existence and support only as an
  unbounded reviewer judgment.
- A command is labeled `live` but the repository contains no corresponding
  execution evidence, or a saved artifact is described without its path/SHA.
- English and Persian have the same section IDs but one omits an audience
  outcome, changes the timing, or reverses the evidence boundary inside prose.
- The two documents have matching section headings but the combined timing
  exceeds the stated session length, or rounded per-section values do not sum
  to it.
- The rebuilt guide is only trivially shorter than the 40-slide source, or is
  shorter by deleting the human-ownership and evidence-safety boundaries;
  `DOC-007` does not distinguish successful compression from unsafe omission.
- A historical or optional appendix becomes the practical primary path despite
  the invariant that the simple walkthrough remains primary.
- A source path is renamed or removed after drafting; the current criteria do
  not require a reproducible citation inventory tied to the candidate revision.

## Over-constraint risks

- Requiring identical English/Persian prose or line-by-line translation would
  conflict with the explicit requirement for natural Persian. The current
  semantic-alignment criterion should remain structural and meaning-based, not
  textual identity.
- Treating every repository claim as requiring a live command would conflict
  with the no-benchmark/no-new-artifact non-goals. Saved evidence and clearly
  optional material are legitimate modes.
- Requiring preservation of all 40 slide slots would undermine the stated Why
  and the non-goal of retaining the existing structure.

## Under-constraint risks

- The test plan is not merely sparse: `obligations`, `runners`, and `tests`
  are all empty, and `DOC-REBUILD.test_ids` is empty. Under
  `_ask/docs/spec-test-traceability.md`, review-only criteria may have empty
  executable cases, but every testable criterion still needs an explicit
  required type, case/decision mapping, assertions, source paths, and an
  independent review-only classification decision. The exact `DOC-001` to
  `DOC-007` obligations and decisions are absent.
- The plan says it will create a “review-only criteria mapping,” but the
  committed JSON contains no such mapping. This is a direct artifact/spec
  inconsistency and prevents an exact plan review or accepted pin.
- The single task has no test IDs. Consequently, even a later semantic review
  cannot demonstrate coverage of each exact criterion or bind the review to
  the `DOC-REBUILD` scope.
- “Review-only” is an evidence mode, not permission to omit authority. No
  independent plan-review decision or accepted traceability pin is present in
  the inspected workstream artifacts. Worker prose cannot substitute for the
  coordinator-recorded authority required by the traceability contract.
- `E2E: not_applicable` is reasonable for static Markdown, but the spec should
  explicitly state that structural, parity, citation, timing, and editorial
  review obligations replace runtime E2E—not leave the empty test plan to
  imply that no evidence is required.
- Migration scope is not bounded enough to resolve whether source references
  are copied, only cited, or updated when canonical paths change. The
  non-goal forbids unrelated documentation edits, but the plan's broad source
  list could invite incidental cleanup.

## Recommended clarifications

1. Add a deterministic section contract: define a stable ID format, enumerate
   the required section IDs/order, state whether appendices and preparation
   material are included, and require each ID to expose cue, guidance, timing,
   and outcome fields in both languages.
2. Choose one session-duration rule. For example, declare a target of exactly
   90 minutes with an explicit rounding tolerance, or change the target to a
   stated shorter duration and explain why. Require the sum of canonical
   numeric timings to satisfy that rule in both documents.
3. Replace subjective compression wording with a reviewable baseline and
   guardrail: record current line/section counts, set a minimum reduction, and
   require an explicit checklist showing that the core model, ownership,
   evidence, recovery, and failure boundaries remain.
4. Define a claim-label and citation inventory. Every demonstration command,
   result, historical example, and optional activity should have one of the
   three labels; saved evidence should name its repository path (and SHA when
   the source requires it); live material should be an instruction to execute,
   not a claim that execution already occurred.
5. Define source-reference review as a per-claim decision: path exists,
   relevant source excerpt/heading identified, and the claim is supported.
   Include a failure decision for unsupported or stale citations.
6. Add a parity checklist covering exact section IDs/order, outcomes,
   lifecycle stages, evidence labels, timing, ownership boundaries, and
   optional/primary status. Permit natural Persian wording while requiring an
   explicit semantic-review result for each dimension.
7. Populate `work/askit-demonstration-rebuild/test-plan.json` with one
   explicit review obligation for each exact criterion `DOC-001`–`DOC-007`,
   required type `review`, case IDs, assertions, source paths, and
   review-only classification decisions. Map those case IDs to `DOC-REBUILD`
   in `task_scopes`; keep executable `cases` empty only where the contract
   explicitly permits it.
8. Recompute the plan (and any task-graph/engineering-model contract digest),
   obtain the independent `decision: APPROVED` plan-review record, and pin the
   exact spec/plan/task/delegation contracts before implementation. This
   challenge does not grant that approval.

## Challenge verdict

**ESCALATE.**

The intended What/Why is coherent and the review-only verification mode is
appropriate for static facilitation notes, but the missing review obligations
and exact criterion mapping are a blocking traceability defect, not an
implementation detail. The unbounded timing, parity, citation, demonstration
label, and compression criteria also admit concrete contradictory outcomes.
Human/coordinator decisions are required before the plan can be independently
approved and pinned. Artifact written: yes.
