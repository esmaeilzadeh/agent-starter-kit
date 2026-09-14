# Baseline: kit flow before OpenSpec machinery

Recorded 2026-09-14 on `agent/openspec-governance-integration` before cutover.
Comparison measures are those listed in `specs/current/openspec-governance-integration.md`
(Baseline and later evaluation). This is the pre-switch snapshot. The later
evaluation workstream compares against it after two or three marked-pilot
changes.

Work-id under observation: `openspec-governance-integration` (Grill → Spec →
Challenge → Spec Change → Plan). No OpenSpec directories in the repo at this
commit.

## Time spent producing and maintaining artifacts

This workstream produced, in order: `intent.md`, identical copies under
`specs/proposals/` and `specs/current/`, `spec-challenge.md`, `spec-change.md`,
rewritten CURRENT spec, then `plan.md`. Challenge required a human Spec Change
before Plan because several acceptance criteria were unimplementable as first
written. Kit `plan.md` and `specs/` are duplicated by construction
(`start-work.sh` seeds `plan.md`; 02 Spec writes both proposal and CURRENT
copies). No wall-clock log exists; the cost signal is the extra 03/04 round
and the dual spec copies.

## Duplicated or contradictory information

- `specs/proposals/openspec-governance-integration.md` and
  `specs/current/openspec-governance-integration.md` were kept identical after
  Spec Change. Two files, one meaning.
- `work/.../plan.md` was an empty template until 05 Plan, while the spec
  already described lifecycle and gates. Status reported `intent` plus
  `code-without-plan` because `.ask/tracker.md` is outside `work/` and
  `specs/`.
- Challenge A6: the bare word "archive" meant both `./ask status` `life:
  archived` and OpenSpec's directory move. Spec Change renamed the OpenSpec
  sense to openspec-archive; that rename is not yet in scripts.

## Missed or ambiguous requirements

Challenge verdict ESCALATE. Load-bearing gaps that 04 closed in the spec but
that current scripts still do not implement: no pilot marker, no targeted
OpenSpec gate, `verify` has no `--work-id` and writes gitignored
`verification-result.json` rather than `work/<id>/verification.json`,
`check-workstream` treats any `specs/current/*` as the accepted spec for any
work-id.

## Semantic-change handling

04 Spec Change rewrote CURRENT from an accepted proposal. There is no
structural delta/apply engine. Semantic edits are whole-file rewrites of
Markdown. Challenge could not be re-run automatically against a delta; a
human confirmed the rewrite.

## Agent adherence to the intended command surface

Agents used `./ask` (`status`, `check-clean`, `check-workstream`, `prepare`,
`sync`). No competing OpenSpec command files exist in `.cursor/commands` or
`.cursor/skills`. Direct OpenSpec CLI is not on PATH in this checkout.

## Review and verification quality

Independent Spec Challenge (model claude-opus-5) ran against kit machinery and
measured OpenSpec 1.12.0 CLI facts; it found unimplementable criteria rather
than rubber-stamping. `./ask verify` still has no work-id binding, no dirty
refuse, and does not write the seeded `work/<id>/verification.json`. Review
(`07`) has not run for this workstream yet.

## Merge conflicts

One live unrelated branch: `agent/kit-talk-ai-team`. This branch has not
merged to default. No merge-conflict sample from parallel OpenSpec edits
(there is no `openspec/` yet). Kit policy already serializes related branches
that touch shared files.

## Readability of current specifications and archived history

`specs/current/` holds accepted kit specs as full Markdown documents. Archived
workstreams keep `work/<id>/` on the default branch with `life: archived` from
`./ask status`. There is no OpenSpec archive tree. Specs are readable as
prose; they are not structurally validated (no required delta schema, no
`isPlanningComplete`).

## Notes for the later evaluation

Do not treat this dogfood work-id as one of the two or three evaluation
changes unless that later workstream says so. Park that workstream at cutover
as `.later/openspec-pilot-evaluation.md`.
