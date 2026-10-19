# Context-engineering audit

Workstream: `refactor-inner-loop`  
Candidate: `020aca2bb83419b91bd9605bc4369434a86dca38`  
Scope: final read-only audit of the accepted workflow, canonical contracts, generated runtime guidance, and verification evidence.

| ID | Check | Verdict |
| --- | --- | --- |
| CE-01 | Instruction hierarchy identifies canonical protocol sources and policy requirements | pass |
| CE-02 | Task loop and 06–08 stage contracts agree on nested TDD, review, correction, and outer gates | pass |
| CE-03 | Grill choices allow a selectable decision and accompanying free text | pass |
| CE-04 | Verify and traceability completion fail closed on missing or stale evidence | pass |
| CE-05 | Branch, clean-tree, single-writer, and integration boundaries remain explicit | pass |
| CE-06 | Guide, spec, templates, and generated runtime bundles preserve the canonical contract | pass |

Open IDs: none. This audit records evidence; it does not provide the human Accept decision.

## CE-01 — Instruction hierarchy

**Verdict:** pass

- `AGENTS.md` identifies `.agents/ask/` as the source of truth for stages, bindings, and verification, with `_ask/` for guides, specs, policies, skills manifest, and templates.
- `.agents/ask/stages/06-implement.md`, `07-review.md`, `08-refactor.md`, `09-verify.md`, and `10-accept.md` define the corresponding stage contracts.
- `_ask/policies/workflow.md`, `worktree.md`, `delegation.md`, `risk.md`, `verification.md`, and `git-flow.md` provide the required policy layer.

## CE-02 — Canonical task lifecycle

**Verdict:** pass

- `.agents/ask/task-loop.md` defines the task-local Red → Green → Refactor cycle, independent Review, correction and re-review, and the distinction between local fixes and broader later work.
- `.agents/ask/stages/06-implement.md`, `07-review.md`, and `08-refactor.md` delegate to that contract and the inner-loop runner rather than introducing a second lifecycle.
- `work/refactor-inner-loop/plan.md` keeps workstream-level assessment and final Verify/Accept outside the task-local loop.

## CE-03 — Grill and continuation interaction

**Verdict:** pass

- `.agents/ask/stages/01-grill.md` requires selectable choices for load-bearing decisions and permits accompanying user text in the same response; its fallback permits a numbered choice with added text.
- Generated stage and runtime bundles were checked by the passing candidate verification, including the `BUNDLE-01`/`BUNDLE-02` behavior cases and bundle parity checks.
- The plan and canonical continuation contract distinguish an explicit stop from a missing gate that blocks an authorized next action.

## CE-04 — Verification and evidence gates

**Verdict:** pass

- `.agents/ask/stages/09-verify.md` requires `./ask verify` and treats missing required checks as failure.
- `./ask traceability check-completion` passed at candidate and anchor `020aca2bb83419b91bd9605bc4369434a86dca38`, using accepted-plan revision `4a513749673f3548aac833d410ca5ae091f271f2`; its report is `work/refactor-inner-loop/traceability/completion.json`.
- `./ask verify` passed at the candidate; `work/refactor-inner-loop/result.json` records `pass`. The run covered all mandatory checks, including static shell checks and traceability completion.
- Candidate-bound Red/Green executions and independent reviews are recorded under `work/refactor-inner-loop/inner-loop/` and `work/refactor-inner-loop/traceability/` runtime evidence.

## CE-05 — Worktree and integration boundaries

**Verdict:** pass

- `AGENTS.md` and `_ask/policies/worktree.md` require a clean worktree before labor, one workstream branch, and commits after meaningful steps.
- `_ask/policies/worktree.md` defines the single-writer integration boundary; `_ask/docs/inner-loop-evidence.md` describes candidate-bound verification and fast-forward integration.
- The workstream was completed on `agent/refactor-inner-loop`. Runtime state, result, and execution evidence remain local as required by the evidence contract; they are not source deliverables.

## CE-06 — Guides and generated runtime bundles

**Verdict:** pass

- `work/refactor-inner-loop/plan.md` enumerates the guide, spec, demo, stage, and runtime bundle outcomes and their ownership.
- The candidate verification passed generated bundle consistency and install/upgrade integration checks, including `BUNDLE-03` regression coverage.
- `./ask sync` completed for the candidate. The final `./ask verify` passed after all task candidates were integrated.
