# Plan

## Specification

Exactly one accepted spec: `specs/current/inner-loop-hardening.md`
(Status CURRENT; identical to `specs/proposals/inner-loop-hardening.md` after
Spec Change 2026-09-20). Do not redefine What/Why or acceptance criteria.

## Approach

Parent 06 is the coordinator on `agent/inner-loop-hardening`. One writer at a
time. This workstream does **not** dogfood the runner against its own graph
(editing the runner while it spawns writers is `glob_too_narrow` risk). Later
workstreams call `./ask inner-loop run`.

Per task: implement on the coordinator checkout → spawn kit-07 Review for that
task’s diff vs its globs → record `TaskResult` under
`work/inner-loop-hardening/inner-loop/results/<id>.json` → next ready task.
Debug spawn only on the spec’s 2+2 cap.

Machine graph (globs, `depends_on`, exemptions, roles):
`work/inner-loop-hardening/inner-loop/tasks.yaml`.
Load that file before any writer. The table below is seams and done-when only.

### Plan encodings (spec Open questions)

| Choice | Encoding |
| --- | --- |
| Checkout | Coordinator worktree only. Runner still implements optional FF-only task worktrees; no node in *this* graph sets them. |
| CLI | `./ask inner-loop run\|resume\|status\|cancel [task_id\|all]`. 06 calls `run` when `tasks.yaml` exists **and** the caller is not this bootstrap workstream. |
| Changelog | Create repo-root `CHANGELOG.md` (none exists). |
| Glob expand | Python stdlib: `fnmatch` plus `**` → `.*` regex, paths relative to repo root. Inputs: `git ls-files -co --exclude-standard` and staged names. Renames: old and new names must both match or `glob_too_narrow`. No extra package. |
| Seam field | TaskGraph adds `seam` (string). Confirmed by this Plan (`seam_at: plan`). |
| Generator cutover | Dual-read in one commit series: prefer `.agents/ask/` when `stages/` exists, else `_ask/agents` + `_ask/bindings`. Then move files, leave `_ask/agents/*.md` and `_ask/bindings/` as pointers, update tests/`OWNED-PATHS.md`. No lasting dual SoT. |
| Brownfield fixture | `_ask/tests/fixtures/brownfield-mixed/` (TS workspace with eslint **and** biome). Scaffold must stop with a choice. Not a live Nest app. |
| Cancel | Explicit `cancel` only. Sequential writer ⇒ no intersecting running tasks to auto-cancel. `resume` aborts in-progress Git back to last `coordinator_sha` when that SHA is an ancestor of HEAD; else escalate. |
| Debug pool | Same bindings pool as 07 Review. Missing pool → spawn fails, task `blocked`. |
| `ask-kit` preset | Named preset whose checks are the executable `_ask/tests/test-*.sh` files. |
| Live spawn | File-shape tests mandatory (Cursor, Claude, Codex, OpenCode). Live Codex/OpenCode spawn: skip unless `ASK_LIVE_SPAWN` is set; document as best-effort. |

### OpenCode pin (AC 2)

- Doc: https://opencode.ai/docs/agents
- Retrieved: 2026-09-20
- Project files: `.opencode/agents/<name>.md` (filename = agent name)
- File-shape keys to emit and test: `description` (required), `mode: subagent`, `model`
- Review/debug: `permission.edit: deny`
- Do not emit deprecated `tools` / `maxSteps`
- If the live doc adds a new **required** key, refresh this pin in Plan (Spec Change only if AC 2 cannot be met)

### E2E mapping

This kit: `e2e: not_applicable` — journeys are `_ask/tests/test-*.sh` via
`ask-kit`, not a product E2E category (spec). Isolation:
`no_production_datastore: true`, empty production-engine adapter list in
committed `.agents/verification.yaml`.

Product rules still apply inside fixture tests (mandatory E2E category unless
`not_applicable`+reason).

Every task below uses `e2e: inherit`.

## Work breakdown

Execute in dependency order, then task id. One writer.

**t1-canonical-ask** — seam: `./ask sync` reads `.agents/ask/` and writes
Cursor/Claude/Codex projections; `_ask/agents` and `_ask/bindings` are pointers.
Done when: existing sync tests pass against the new SoT; `OWNED-PATHS.md` lists
`.agents/ask/`.

**t2-opencode-projection** — depends `t1-canonical-ask`. seam: fourth runtime
dir `.opencode/agents` from the OpenCode pin. Done when: file-shape test asserts
frontmatter keys; live spawn not required.

**t3-runner-graph** — seam: `load_graph` / `validate_graph` / CAS `state.json`
(`cycle`, `path_conflict`, worker cannot write state, second writer refused).
Done when: `_ask/tests/test-inner-loop.sh` covers those operations.

**t4-commit-allowlist** — depends `t3-runner-graph`. seam: Git stage/commit
reject outside expanded globs; `git diff --name-only` vs globs;
`extras` vs `glob_too_narrow`. Done when: harness tests pass; filesystem is
not reduced to `owned_paths`.

**t5-retry-resume** — depends `t4-commit-allowlist`. seam: 2 implement
remediations then debug (fresh context) ×2 then `blocked`; FF integrate only;
`resume` repair. Done when: AC 3 retry/FF/resume rows are red-then-green.

**t6-wire-stages** — depends `t1-canonical-ask`, `t5-retry-resume`. seam: 06/07/08
contracts call the module; they do not inline a DAG. Done when: contracts +
generated skills point at `./ask inner-loop` / the Python module.

**t7-verify-core** — depends `t1-canonical-ask`. seam: language-neutral CheckPlan
in `.agents/ask/verification/`; `./ask verify` fail-closed; kit yaml uses
`ask-kit`; no language CLIs in dispatcher core. Done when: empty plan fails;
kit `./ask verify` runs `ask-kit`; npm/pytest/cargo discovery is gone from core.

**t8-scaffold-wizard** — depends `t7-verify-core`. seam: write
`.agents/verification.yaml` only if absent; re-scaffold writes a candidate;
human-only wizard; `--preset` for tests; mixed-stack fixture stops on
disagreement. Done when: those tests pass; agent Verify names the wizard and
does not run it.

**t9-git-flow** — seam: `./ask start-work` from `develop` or fail closed;
`CHANGELOG.md`; `work/<id>/release-evidence.md` template; hotfix prose. Done
when: start-work tests fail without `develop`; no script merges/tags/pushes
`main`.

**t10-e2e-contracts** — depends `t1-canonical-ask`, `t6-wire-stages`. seam:
intent/spec/plan templates and 01/02/05/06/09 require E2E applicability or
`not_applicable`+reason. Done when: contract tests fail if the section is
missing with no reason.

**t11-worktree-carveout** — depends `t9-git-flow`. seam: `worktree.md` allows
in-workstream optional task worktrees and one writer; still forbids
cross-workstream overlap. Done when: policy text matches spec Constraints.

**t12-kit-docs** — depends `t6-wire-stages`, `t7-verify-core`, `t9-git-flow`,
`t11-worktree-carveout`. seam: Build Spec, CONTEXT, AGENTS.md, ADRs, install/
upgrade, dispatcher help. Exemption: documentation-only. Done when: docs name
`.agents/ask/` as SoT and Git-flow as specified.

**t13-context-audit** — depends `t12-kit-docs`. seam: independent
challenge/review spawn writes `work/inner-loop-hardening/context-audit.md`.
Done when: every ID below is `pass` or linked Spec Change; spawn did not
Implement t1–t12 files.

Audit IDs (closed set):

| ID | Check |
| --- | --- |
| CE-01 | Instruction hierarchy: AGENTS.md → policies → `.agents/ask/stages` |
| CE-02 | 06–08 point at the runner; they do not inline a DAG |
| CE-03 | 01 Grill still requires expanded load-bearing questions |
| CE-04 | Fail-closed verify is reachable from 09 without shell-overlay language |
| CE-05 | One-writer + dirty-tree gates still visible from always-on pointers |
| CE-06 | Compressed grilling/protocol pointers from this workstream are repaired |

## Risks

- Dual-read window leaves tests on `_ask/agents` while files already moved
  (cut over in the same task, not a later PR).
- `ask` dispatcher usage text and install/upgrade path lists drift from
  `.agents/ask/` (t12 must include install tests).
- Fixture eslint+biome disagreement is the only mixed-stack proof; a real
  consumer may still need wizard UX changes (escalate, do not guess).
- Parent 06 skipping per-task kit-07 Review would skip `reviewer_ack` on
  exemptions (t12) and boundary `git diff` (t4).

## Verification approach

Each behavior-changing task: failing test command captured, then passing
command captured, SHA on `agent/inner-loop-hardening`. Outer `./ask verify`
after t7 once `.agents/verification.yaml` exists (fail-closed `ask-kit`);
before t7, run the executable `_ask/tests/test-*.sh` set as today.

09 Verify runs `./ask verify` on HEAD. 10 Accept needs this Plan’s audit file
with no `open` IDs plus recorded SHA.

## Escalation points

Stop and grill (or Spec Change) when:

- A required edit is outside the task glob (`glob_too_narrow`).
- `resume` cannot abort to an ancestor `coordinator_sha`.
- OpenCode required frontmatter and the pin disagree.
- Wizard would need to run inside agent Verify/Implement.
- Audit ID cannot pass without changing What/Why.
- `develop` is missing and creating it is a human Git decision.

## Spec-change triggers

Stay in Plan/Implement for encodings above. Open Spec Change only if the
requirement must move, including: concurrent Git writers; cherry-pick/rebase
onto the coordinator; extra languages; `_ask/agents` remaining SoT;
compatibility with `.starter-kit/verify.conf`; in-memory production-engine
substitutes; mandatory live Codex/OpenCode spawn; dropping fail-closed verify;
dropping the context-audit Accept gate.

## Out of scope for this plan

Concurrent Git writers. Vendoring cc-sdd / Spec Kit / Learn Harness.
Languages other than TypeScript and Python. Dogfooding `./ask inner-loop run`
on this workstream. Live OpenCode/Codex spawn in default CI. Generic in-memory
DB adapters (already parked in `.later/`). Human merge/tag/push of `main`.
`./ask setup` / verify wizard in agent sessions.
