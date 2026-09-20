# Explore Map: Concurrent inner-loop hardening

## Destination

Ownable What/Why for one workstream that:

1. Adds a resumable concurrent subagent runner inside ASK Implement→Refactor (06–08), borrowing cc-sdd task dispatch and Learn Harness Engineering’s instructions/state/verification/scope/lifecycle checks, without importing a second SDLC.
2. Makes TypeScript and Python verification deterministic (presets behind a language-neutral core).
3. Adds an OpenCode runtime adapter and strengthens the Codex adapter, generated from one portable source of truth.

Human authority, dirty-tree refusal, dedicated `agent/<work-id>` branch, evidence SHA, and Accept stay outer-loop.

## Notes

- Kit Explore, not Cursor’s built-in Explore subagent.
- `codebase-design` is pinned (`mattpocock/skills` `v1.2.3`, role `inner-loop-seam-design`) and prepared. Vocabulary in this file: module, interface, depth, seam, adapter, leverage, locality.
- `tdd` is pinned at the same revision, required, and prepared after the human made RED→GREEN mandatory for implementation.
- `diagnosing-bugs` and `prototype` remain unprepared; neither is needed to resolve the current frontier.
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

Investigation shape (not a decision): a deep inner-loop module whose interface is a TaskGraph (nodes: dependencies, owned paths, role configs, checks, status/evidence). Persistent state: `work/<id>/inner-loop/state.json`. Runtime adapters spawn implement / review / debug. Final 09 Verify and 10 Accept stay outer-loop. Its canonical path now depends on the chosen `.agents/` layout.

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

Human decision: replace the shell-overlay model with a language-neutral verification scaffolder and normalized CheckPlan / VerifyResult. After project scaffold/init, the consuming repository has a concrete verification set for its detected TypeScript and/or Python stack. Compatibility with `.starter-kit/verify.conf` is not required. Exact artifact ownership, regeneration, and tool-install behavior remain open.

### Bindings as implemented

- Portable SoT: `_ask/agents/` (stage contracts), `_ask/bindings/` (roles/pools + per-runtime slugs). ADR 0005, ADR 0008, `CONTEXT.md` Bindings.
- Prepared Community Skills: `.agents/skills/` only. `CONTEXT.md` avoids a new `.agent/` root next to that store.
- Generator: `./ask sync` → `.cursor/skills` + `.cursor/commands` from `_ask/agents/`; `sync-runtime-agents.py` → `.cursor/agents`, `.claude/agents`, `.codex/agents`. Runtimes hardcoded: `cursor`, `claude`, `codex`. No `opencode.yaml`, no `.opencode/`.
- Codex adapter: TOML via `agent.toml.tpl`. `runtimes/codex.yaml` notes custom `agent_type` attach has failed on some Codex versions; spawn is best-effort. Review projection has no `readonly` equivalent (Cursor Review gets `readonly: true`).
- `.agents/skills/` is currently a generated, gitignored Community Skill store. Moving canonical protocol into `.agents/` therefore requires explicit sibling namespaces and distinct ownership rules so install/upgrade cannot confuse kit-owned contracts with prepared or consumer-owned files.

Human decision: canonical stage contracts and binding tables move into `.agents/ask/{stages,bindings,...}`; `.agents/skills/` remains a separate generated Community Skill store. Backward compatibility with `_ask/agents/` and `_ask/bindings/` is not required because ASK has no deployed clients. This permission applies to the current kit shape only: after launch, upgrades must preserve consumer-owned state and configuration unless an explicit migration says otherwise. Cursor, Codex, and OpenCode remain generated runtime projections from the canonical namespaced source.

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
- Canonical kit inputs use the namespaced `.agents/ask/{stages,bindings,...}` layout. `.agents/skills/` remains separate.
- ASK has no deployed clients, so this workstream may break the current kit layout and interfaces without preserving their old shape. Future upgrades still need explicit ownership and lifecycle rules and may not overwrite consumer-owned state or configuration by default.
- Every concurrent writing task gets its own Git worktree and branch. Read-only agents may share a checkout. Integration into `agent/<work-id>` must be deterministic.
- Source-file tasks run according to the dependency DAG. Tasks that own overlapping source paths are serialized; a later task starts from the coordinator SHA after its prerequisites are integrated. Parallel-ready tasks must own disjoint source paths.
- Task branches do not edit shared inner-loop state files. The coordinator owns state transitions and applies versioned compare-and-swap updates from structured task results.
- Ready task commits are integrated in dependency order, then stable task ID. Unexpected conflicts stop and escalate; agents do not resolve them silently.
- Verification starts from a language-neutral scaffolder. Project scaffold/init materializes a concrete verification set for detected TypeScript and/or Python. `.starter-kit/verify.conf` compatibility is out of scope.
- The concrete `.agents/verification.yaml` is consumer-owned and committed. Scaffold creates it only when absent; future upgrades preserve it; explicit re-scaffold produces a reviewable candidate.
- Missing verification tools use interactive provisioning: the human selects the stack before setup mutates product manifests, tool configuration, or lockfiles.
- TDD is mandatory for behavior-changing implementation tasks.
- The workflow must ask the human to define and confirm E2E behavior before implementation, then plan, implement, and verify it.
- Test databases, files, queues, caches, and other mutable state must be isolated from development and production state.
- Before Accept, the plan must include an independent context-engineering audit of these large changes and repair instruction/pointer failures that can cause skipped or compressed protocol steps.
- Git-flow becomes the repository branching and release model. Protected `main` represents releasable state; `develop` is the integration and durable later-work coordination branch. Exact release/hotfix authority remains in the frontier.
- Later-work cards are durable on `develop` and mirrored to tracker issues. The first published set is commit `759731f` on `origin/develop`.

## Not yet specified

Load-bearing frontier (Explore grilling, ADR 0016). Numbered questions only. Defaults OK covers the assume-list.

### Extra skills (before Qs)

See Notes. Default: no further prepare.

### Numbered questions

❓ **Q8** - **Mandatory TDD evidence and exemptions**: What exactly must a task prove before its implementation commit is eligible for integration?

- **A. Vertical RED→GREEN at a confirmed seam:** every behavior-changing task records the confirmed seam, failing test command and failure evidence, then passing command and evidence. Documentation-only, generated projection, and non-behavioral configuration tasks may claim a typed exemption with a reason that the reviewer checks.
- **B. TDD only where tests already exist:** legacy modules without a test seam may implement first and add characterization tests afterward.
- **C. No exemptions:** every task, including generated files and documentation, must produce a red test before modification.

Hard to reverse: task-result schema, reviewer gate, legacy-code adoption, and implementation throughput all depend on the evidence rule.

➡️ **A.** It makes TDD enforceable without manufacturing meaningless tests for artifacts that do not expose behavior.

❓ **Q9** - **E2E contract gate**: Where does the required human definition and confirmation enter the workflow?

- **A. Spec gate:** Grill/Spec asks whether E2E applies and gathers critical journeys, observable outcomes, environment, test data, and reset rules. The human confirms the E2E contract with the specification. Plan maps it to tooling and isolation; Implement builds it; Verify runs it. “Not applicable” requires an explicit reason.
- **B. Plan gate:** the planning agent derives E2E scenarios from the accepted spec and asks for a separate confirmation before implementation.
- **C. Verify gate:** implementation proceeds from unit/integration criteria; E2E is designed after the feature exists.

Hard to reverse: acceptance criteria, the defaults confirmation, plan structure, and what blocks implementation depend on this gate.

➡️ **A.** E2E defines externally observable success, so it belongs in the accepted contract rather than being invented after design.

❓ **Q10** - **Test-state isolation**: What invariant prevents tests from corrupting development or production databases and state?

- **A. Declared isolated resources with a hard guard:** unit tests use no database or an interface-level fake; integration and E2E use an ephemeral isolated instance of the production database engine. `.agents/verification.yaml` names test-only resource adapters and namespace strategy. The runner refuses known development/production identifiers and destructive commands outside the test namespace. Cleanup is idempotent; leaked resources are recorded.
- **B. Transaction rollback only:** tests use the configured database but wrap cases in transactions. This is fast but does not isolate migrations, queues, caches, files, external services, or code that opens another connection.
- **C. Clone development state:** create a disposable copy of development data for each run. Realistic, but risks sensitive-data copying and accidental source mutation.
- **D. Test convention only:** trust environment variables and test code to select safe resources.

Hard to reverse: verification schema, adapters, CI setup, local developer workflow, and destructive-operation authority depend on the isolation invariant.

➡️ **A.** Isolation must be machine-checkable and cover every mutable state adapter, not only SQL transactions.

❓ **Q11** - **Git-flow authority and release lifecycle**: Which actors may advance work through `develop`, `release/*`, `main`, and `hotfix/*`?

- **A. Human-controlled releases:** `agent/<work-id>` starts from `develop` and returns by PR/approved merge. Agents may prepare `release/<version>` from `develop`, run verification, and assemble release evidence, but a human authorizes merge/tag/push to protected `main`. `hotfix/*` starts from `main`; after human-approved release it is merged back to both `main` and `develop`.
- **B. Agent-controlled integration and releases:** agents merge verified work to `develop`, cut release branches, merge/tag `main`, and back-merge automatically.
- **C. Git-flow names without release automation:** use `develop` and feature branches, but leave release/hotfix/tag behavior undocumented and manual.

Hard to reverse: `start-work`, Accept authority, release provenance, protected-branch rules, versioning, and CI triggers all depend on this split.

➡️ **A.** It preserves ASK’s human authority while allowing agents to prepare every reversible release artifact.

### I’ll assume (Defaults OK covers these)

- The inner-loop **interface** is TaskGraph + `work/<id>/inner-loop/state.json`. Tests hit that interface, not stage-contract prose. Its code path follows the Q4 ownership boundary.
- Runtime **adapters** spawn implement / review / debug. They do not own scheduling.
- 09 Verify (repo checks) and 10 Accept stay outer-loop. Inner-loop node “checks” are per-task evidence, not a substitute for `./ask verify`.
- Debugger is an inner-loop role adapter after bounded repeated failure, not a new 00–10 stage.
- Codex remains generated TOML; “strengthen” means projection completeness, tests, and documented spawn limits — not a second Codex SoT.
- OpenCode is a fourth generated runtime adapter, with format details established from primary documentation at implementation time.
- Stage contracts keep 06–08 as protocol and move to the canonical `.agents/` layout selected in Q4; they call the inner-loop module rather than inlining a DAG.
- Failure-convergence (Phase 3) is in scope only as bounded retry/debug inside the module, not a transcript database.
- Ready-to-launch means this workstream implements after Grill→Spec→Plan on `agent/inner-loop-hardening` and push is a later human ask. Explore does not implement product code.
- No languages beyond TypeScript and Python. No auto-merge to default branch.

### Later frontier (blocked on Q8–Q10)

- Generator entrypoints, local-overlay location, and install/upgrade mechanics.
- Exact TaskGraph fields, branch naming, evidence schema, retry count, cancellation, and resume after kill.
- Failure handling when an integrated task invalidates a still-running task’s base.
- CheckPlan schema, preset provenance, brownfield baseline semantics, and fail-on-empty behavior.
- Detection precedence when TypeScript and Python manifests, monorepos, or multiple tools coexist.
- Interactive provisioning transaction/rollback behavior after the human selects tools.
- Version source, changelog generation, release evidence schema, and tag convention after Q11.
- Optional in-memory database adapters are parked in `.later/in-memory-test-state-adapters.md`; they require contract parity with the production adapter.
- OpenCode agent file format details.
- Whether the kit repository’s own concrete verification config lists `_ask/tests/test-*.sh` directly or uses a named `ask-kit` preset.
- Acceptance test matrix across Cursor, Codex, and OpenCode (spawn may stay best-effort on Codex).

## Out of scope

- Custom model runtime or centralized state database replacing Git.
- Languages other than TypeScript and Python.
- Replacing OpenSpec (when present) or weakening worktree / verification / Accept gates.
- Installing cc-sdd, Spec Kit, or Learn Harness as the SDLC.
- Automatically deploying or merging product changes.
- Filling Intent in this Explore pass.

## Handoff to Intent

Pending Q8–Q10 and the later frontier. Destination is **STILL_FOGGY**. Do not enter `01 Grill` until those answers (or an explicit Defaults OK covering the recommendations and assume-list) are recorded here.

Gate: **STILL_FOGGY**
