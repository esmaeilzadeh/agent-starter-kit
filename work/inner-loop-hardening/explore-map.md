# Explore Map: Concurrent inner-loop hardening

## Destination

Ownable What/Why for one workstream that:

1. Adds a resumable concurrent subagent runner inside ASK Implement→Refactor (06–08), borrowing cc-sdd task dispatch and Learn Harness Engineering’s instructions/state/verification/scope/lifecycle checks, without importing a second SDLC.
2. Makes TypeScript and Python verification deterministic (presets behind a language-neutral core).
3. Adds an OpenCode runtime adapter and strengthens the Codex adapter, generated from one portable source of truth.

Human authority, dirty-tree refusal, dedicated `agent/<work-id>` branch, evidence SHA, and Accept stay outer-loop.

## Notes

- Kit Explore, not Cursor’s built-in Explore subagent.
- `codebase-design` is pinned (`mattpocock/skills` `v1.2.3`, role `inner-loop-seam-design`) and prepared. Vocabulary in this file: module, interface, seam, adapter, depth, leverage, locality.
- Extra related skills that would change What/Why — ask before prepare; do not prepare unless accepted:
  - `tdd` — would make RED→GREEN a kit inner-loop requirement rather than consumer checks.
  - `diagnosing-bugs` — would make debugger a protocol stage rather than an inner-loop role adapter.
  - `prototype` — would spike TaskGraph before Spec; changes Explore duration, not destination.
- Default: do not prepare those three. `codebase-design` is enough for seam placement.
- Comparison sources (prior session, primary READMEs): [cc-sdd](https://github.com/gotalab/cc-sdd), [Learn Harness Engineering](https://github.com/walkinglabs/learn-harness-engineering), [OpenSpec](https://github.com/Fission-AI/OpenSpec), [Spec Kit](https://github.com/github/spec-kit).
- This checkout is clean on `agent/inner-loop-hardening`. Intent/plan templates exist and are empty; do not fill them in Explore.

## Tracker map (optional)

- No external tracker map. This file is canonical (ADR 0003).

## Research facts

### Comparison (gathered 2026-09-19)

| Project | Layer | Strongest capability | Weakness vs this destination |
|---|---|---|---|
| ASK | Outer governance / evidence protocol | Dirty-tree, workstream branch, SHA, human Accept | Inner loop is sequential and chat-orchestrated |
| OpenSpec | Spec/change engine | Brownfield delta + archive | Does not govern branches, review isolation, or Accept |
| cc-sdd | Autonomous implement harness | Per-task implementer / reviewer / debugger, TDD, resume | Weaker provenance and human-authority gates |
| Spec Kit | Workflow distribution | Ecosystem, presets | Duplicates ASK+OpenSpec; does not add a runner or TS/Python hardening |
| Learn Harness Engineering | Course + harness auditor | Five-part model: instructions, state, verification, scope, lifecycle | Structural score, not a feature SDLC |

Standing composition from that comparison (not yet a Spec):

```text
ASK outer governance
  OpenSpec as spec/change engine (when present)
    cc-sdd-shaped per-task implement / review / debug
      TS/Python checks as hard gates
```

Borrow, do not vendor: one task graph with owned paths; fresh implementer/reviewer contexts; bounded debugger; resumable notes; harness checks for instructions/state/verification/scope/lifecycle.

Do not stack full cc-sdd or Spec Kit on ASK (two SDLCs).

This checkout has no `openspec/` tree. OpenSpec appears only as `.later/openspec-pilot-evaluation.md` from `openspec-governance-integration`. “Keep pinned OpenSpec” is a standing preference from that comparison, not a file on this branch.

### Inner loop (06→09) as implemented

- Stage contracts: `_ask/agents/06-implement.md` … `09-verify.md`.
- 06 Implement: labor in the parent chat. No spawn section. No task DAG, owned paths, retry/resume state, or worktree automation.
- Required isolated spawn: 07 Review only (plus 03 Spec Challenge, outer-loop). 01 Grill and 05 Plan may spawn. 08 Refactor and 09 Verify do not spawn.
- Aggregation is chat-authored `review.md` / `verification.json`, not a deterministic merge of node evidence.
- `_ask/spec/06-phases-and-acceptance.md` v1 forbids a custom multi-agent runtime. Kit shape remains protocol + instructions + small scripts + artifacts + policy.
- Worktree policy (`_ask/policies/worktree.md`) forbids overlapping *workstreams* on common files. It does not define in-workstream concurrent tasks.
- Cursor research already flags two isolation models: Cursor worktrees vs kit `agent/<work-id>` (`_ask/docs/research/cursor-binding-surfaces.md`).

Investigation recommendation (not a decision): deep module `_ask/inner-loop/` whose interface is a TaskGraph (nodes: dependencies, owned paths, role configs, checks, status/evidence). Persistent state: `work/<id>/inner-loop/state.json`. Runtime adapters spawn implement / review / debug. Final 09 Verify and 10 Accept stay outer-loop.

Depth claim: callers (06, runtime adapters, tests) learn TaskGraph + state.json; scheduling, conflict refusal, retry, resume, and evidence fold live in the implementation. Locality: change the runner once, not in four stage contracts and three runtime projections.

Two adapters already exist at the runtime seam (Cursor, Claude, Codex generated today; OpenCode requested). That makes a real seam, not a hypothetical one.

### Verification as implemented

- Dispatcher: `./ask verify` → `_ask/scripts/verify.sh`.
- Optional consumer overlay: source `.starter-kit/verify.conf` if present. This repo has no `.starter-kit/`.
- Default discovery if `CHECKS` empty: executable `_ask/tests/test-*.sh` and `tests/test-*.sh`; `npm test` if `package.json` has `"test"` and `npm` exists; `pytest` if `pyproject.toml` or `pytest.ini` and `pytest` exists; `cargo test` if `Cargo.toml` and `cargo` exists.
- Empty `CHECKS` → overall pass (pass-on-empty). Missing tools skip the check (not fail-closed).
- No typecheck, eslint/biome, pyright/mypy, ruff, dependency-architecture, or import-linter discovery.
- JSON result: `{commit_sha, result, checks:[{check, result, code?}]}`. No CheckPlan schema, baseline, or skip-reason.
- Spec §24 (`_ask/spec/04-scripts-and-git.md`): detect package manager, run configured mandatory checks, fail on mandatory failures, print SHA, emit machine-readable output; do not hard-code Nest/Node/Python/Rust into the *core*; provide consumer extension points. Current script hard-codes npm/pytest/cargo discovery in the core.
- 09 contract lists type checks and lint; the script does not implement them.

Investigation recommendation (not a decision): language-neutral core + normalized CheckPlan / VerifyResult; consumer-owned `.starter-kit/verification.yaml`; fail-closed; brownfield baseline. TS preset: typecheck, eslint or biome, tests, optional dependency architecture. Python preset: pyright or mypy, ruff, pytest, optional import-linter.

### Bindings as implemented

- Portable SoT: `_ask/agents/` (stage contracts), `_ask/bindings/` (roles/pools + per-runtime slugs). ADR 0005, ADR 0008, `CONTEXT.md` Bindings.
- Prepared Community Skills: `.agents/skills/` only. `CONTEXT.md` avoids a new `.agent/` root next to that store.
- Generator: `./ask sync` → `.cursor/skills` + `.cursor/commands` from `_ask/agents/`; `sync-runtime-agents.py` → `.cursor/agents`, `.claude/agents`, `.codex/agents`. Runtimes hardcoded: `cursor`, `claude`, `codex`. No `opencode.yaml`, no `.opencode/`.
- Codex adapter: TOML via `agent.toml.tpl`. `runtimes/codex.yaml` notes custom `agent_type` attach has failed on some Codex versions; spawn is best-effort. Review projection has no `readonly` equivalent (Cursor Review gets `readonly: true`).
- Moving stage contracts into `.agents/` would split SoT from `_ask/` (install overlay, tests, ADRs, `./ask sync`) and mix generated skill bodies with kit protocol.

Investigation recommendation (not a decision): keep `_ask` as the canonical package and one generator pipeline; add `.opencode/agents` from `_ask/bindings/runtimes/opencode.yaml`; improve Codex projection; keep `.agents/skills/` as the shared skill store.

## Decisions so far

- ASK remains the outer governance protocol. Do not replace Grill / Spec / Challenge / Plan / Verify / Accept.
- Do not import cc-sdd or Spec Kit as a second SDLC. Borrow inner-loop mechanisms only.
- TypeScript and Python are the only languages in this workstream.
- Concurrent subagents must isolate work and aggregate evidence deterministically.
- Generate Cursor, Codex, and OpenCode bindings from one portable source.
- `codebase-design` is in play for the inner-loop seam.
- Do not build a custom model runtime (v1 “what not to build”).
- Do not weaken dirty-tree, dedicated branch, SHA evidence, or human Accept.
- Do not auto-deploy or merge to `main`/`master` from this workstream.

## Not yet specified

Load-bearing frontier (Explore grilling, ADR 0016). Numbered questions only. Defaults OK covers the assume-list.

### Extra skills (before Qs)

See Notes. Default: no further prepare.

### Numbered questions

❓ **Q1** - **Canonical portable source of truth**: Where do stage contracts and binding tables live as the one editable source?

- **A.** Keep `_ask/` (`_ask/agents/`, `_ask/bindings/`). One `./ask sync` pipeline. Add `runtimes/opencode.yaml` → `.opencode/agents`. Strengthen Codex under `.codex/agents`. `.agents/skills/` stays prepared Community Skills only.
- **B.** Move stage contracts and bindings into `.agents/` (human suggestion “perhaps `.agents`”). Rewire generator, ADRs, install overlay, tests, `CONTEXT.md`. Mix protocol with prepared skill trees.
- **C.** Dual-write `_ask` and `.agents` as two sources.

Hard to reverse: install path, every runtime projection, every kit test that greps `_ask/agents` / `_ask/bindings`.

➡️ **A.** Matches ADR 0005/0008 and `CONTEXT.md`. `.agents/` is already the skill store; using it as protocol SoT loses locality. OpenCode is a fourth adapter at the existing bindings seam, not a new SoT.

❓ **Q2** - **Concurrency isolation**: How may inner-loop nodes run at the same time on one `agent/<work-id>` branch?

- **A.** One worktree. TaskGraph nodes declare owned paths. Overlap → refuse or serialize. Deterministic aggregation from `state.json`.
- **B.** Git worktree (or clone) per concurrent node.
- **C.** A plus optional worktrees when the human opts in for overlapping paths.
- **D.** Unconstrained parallel writes.

cc-sdd’s documented loop is one task per iteration (fresh implementer), not an unconstrained DAG. The request is concurrent subagents *inside* ASK. Kit policy already forbids overlapping *workstreams*; this question is in-workstream tasks.

Hard to reverse: state schema, adapter spawn, conflict tests. Blocks debugger/retry design.

➡️ **A** for this workstream. Highest locality; avoids a second isolation model (already an open gap vs Cursor worktrees). Worktrees can be a later card. **D** is out.

❓ **Q3** - **Verification contract and failure policy**: How do TypeScript and Python checks enter `./ask verify` without hard-coding those languages into the core?

- **A.** Language-neutral core (CheckPlan / VerifyResult). Consumer `.starter-kit/verification.yaml`. TS and Python presets. Fail-closed (configured mandatory check missing or tool missing → fail, unless a recorded brownfield baseline explicitly allows skip). Replace pass-on-empty.
- **B.** Keep sourcing `.starter-kit/verify.conf` as a bash `CHECKS` array. Add TS/Python command discovery inside `verify.sh`.
- **C.** **A**, plus deprecated read of `verify.conf` during migration.

Spec §24 already wants a language-neutral core and consumer extension points. Current `verify.sh` violates that by inlining npm/pytest/cargo and passing when nothing runs.

Hard to reverse for consuming repos. Recommendation might be wrong if existing overlay users depend on pass-on-empty.

➡️ **A.** No `.starter-kit/verify.conf` in this repo, so no in-tree migration debt. Kit’s own verify path stays explicit (kit shell tests listed in yaml or discovered as the kit preset). Brownfield consumers record a baseline rather than inheriting skip.

### I’ll assume (Defaults OK covers these)

- Inner-loop **module** lives at `_ask/inner-loop/` if Q1=A (or under the chosen SoT). **Interface**: TaskGraph + `work/<id>/inner-loop/state.json`. Tests hit that interface, not stage-contract prose.
- Runtime **adapters** spawn implement / review / debug. They do not own scheduling.
- 09 Verify (repo checks) and 10 Accept stay outer-loop. Inner-loop node “checks” are per-task evidence, not a substitute for `./ask verify`.
- TDD is not a kit protocol requirement. Nodes may list tests as checks. Consumer TS/Python presets supply the tools.
- Debugger is an inner-loop role adapter after bounded repeated failure, not a new 00–10 stage.
- Codex remains generated TOML; “strengthen” means projection completeness, tests, and documented spawn limits — not a second Codex SoT.
- OpenCode is a fourth runtime adapter in `RUNTIMES` / `OUT_DIRS`, format following OpenCode’s agent files at implement time.
- Stage contracts stay in `_ask/agents/` and keep 06–08 as protocol; they call the inner-loop module rather than inlining a DAG.
- Failure-convergence (Phase 3) is in scope only as bounded retry/debug inside the module, not a transcript database.
- Ready-to-launch means this workstream implements after Grill→Spec→Plan on `agent/inner-loop-hardening` and push is a later human ask. Explore does not implement product code.
- No languages beyond TypeScript and Python. No auto-merge to default branch.

### Later frontier (blocked on Q1–Q3)

- Exact TaskGraph fields and evidence schema.
- Retry count, cancellation, and resume after kill.
- OpenCode agent file format details.
- Whether kit-repo verify yaml lists `_ask/tests/test-*.sh` or a named `ask-kit` preset.
- Acceptance test matrix across Cursor, Codex, and OpenCode (spawn may stay best-effort on Codex).
- Migration story if a consumer already has `verify.conf` (none in this repo).

## Out of scope

- Custom model runtime or centralized state database replacing Git.
- Languages other than TypeScript and Python.
- Replacing OpenSpec (when present) or weakening worktree / verification / Accept gates.
- Installing cc-sdd, Spec Kit, or Learn Harness as the SDLC.
- Automatically deploying or merging product changes.
- Filling Intent in this Explore pass.

## Handoff to Intent

Pending Q1–Q3. Destination is **STILL_FOGGY**. Do not enter `01 Grill` until those answers (or an explicit Defaults OK covering the recommendations and assume-list) are recorded here.

Gate: **STILL_FOGGY**
