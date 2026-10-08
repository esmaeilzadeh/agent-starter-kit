# Context-engineering audit

Workstream: `harness-review`. Reviewed range: `ed6fa62..4c13aec`, including independent correction re-review of `a7944f0..4c13aec`.
Specification: `specs/current/harness-review.md`.

Independent child reviewer `/root/spec_challenge_fallback` implemented none of the source. Model/runtime fallback and same-family limits are recorded in `review.md`. This audit applies the existing CE-01..CE-06 pointer checklist; it does not replace implementation review or executed verification.

| ID | Check | Verdict | Evidence |
| --- | --- | --- | --- |
| CE-01 | Instruction hierarchy and protocol source of truth | pass | Root `AGENTS.md` identifies `.agents/ask/` as canonical and requires policy reads; `.cursor/rules/starter-kit-bootstrap.mdc` preserves the same order. |
| CE-02 | Stages 06–08 delegate to the runner without inlining a DAG | pass | 06 names `./ask inner-loop run`/resume and `_ask/scripts/inner_loop/`; 07 names current-writer status and coordinator `record-review`; 08 stays on the current writer and invokes the runner. No task graph was copied into these stages. |
| CE-03 | Expanded load-bearing Grill questions remain required | pass | `.agents/ask/stages/01-grill.md` retains alternatives/tradeoffs/failure modes and the rule against blessing an unexpanded decision. This work did not modify that stage. |
| CE-04 | Fail-closed Verify remains reachable from stage 09 | pass | 09 requires `./ask verify`, committed CheckPlan, nonempty mandatory checks and commit SHA. The canonical runner refuses empty/zero-mandatory plans; the candidate wrapper also requires mandatory checks and validates executed identity/results. |
| CE-05 | One-writer and clean-worktree gates remain visible | pass | Root checklist and Cursor bootstrap preserve clean-tree and one-workstream instructions. `_ask/policies/worktree.md` retains one writer and now points to local locking/evidence recovery. Runtime recovery finding F1 was fixed and its public regressions independently rerun at `4c13aec`; see `review.md`. |
| CE-06 | Canonical protocol pointers and generated projections remain aligned | pass | Updated 06/07 canonical stage bodies are embedded verbatim in `.agents/skills/kit-*`, `.cursor/skills/kit-*` and `.cursor/commands/*` (commands add a generated-file header). Workflow Explore and `_ask/agents/00-explore.md` remain canonical-stage pointers. |

Open checklist IDs: none. F1 is fixed with rerun evidence and implementation review is APPROVED at `4c13aec`. Final full verification/acceptance is a separate parent responsibility.

Correction re-review preserves CE-01..CE-06. The new Git repair and pinned verification snapshot live behind the existing runner interface; no DAG, extra human approval flow or alternate protocol source was added. Updated evidence documentation states both recorded-base runner provenance and tracked-runtime preservation. The exact spec wording now names recorded-base runner/import snapshots, consistent with the existing coordinator-owned verification boundary.
