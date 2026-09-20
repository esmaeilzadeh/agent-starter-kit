# Specification Challenge

## Model

| Field | Value |
| --- | --- |
| runtime | cursor |
| model | composer-2.5 (spawn slug: composer-2.5-fast) |
| parent_model | grok-4.6 (Spec authored in parent after kit-02-spec usage limit) |
| kit_default | kimi-k3 (adversarial role; not spawnable in parent Task session) |
| fallbacks | claude-opus-5, gpt-5.6-sol, claude-fable-5-1 (usage limits); Composer chosen as available non-Grok pick |
| human | continue after Grill defaults-OK; do not re-ask bless unless ESCALATE |

## Specification

Challenged artifact: `specs/proposals/inner-loop-hardening.md` (Status PROPOSED).

Grounding sources: `work/inner-loop-hardening/intent.md`, `work/inner-loop-hardening/explore-map.md` (Q1–Q11, DESTINATION_CLEAR), `_ask/templates/spec.md`, and kit implementation:

- `_ask/scripts/verify.sh` — pass-on-empty `CHECKS`, optional skip when tools missing, hard-coded npm/pytest/cargo discovery in core
- `_ask/scripts/start-work.sh` — `./ask check-clean` then branch from `origin/HEAD` / `main` / `master`, not `develop`
- `_ask/policies/worktree.md` — dirty-tree hard gate before delegated labor; one `agent/<work-id>`; no parallel workstreams on overlapping paths
- `_ask/policies/verification.md` — evidence class mapping only; no fail-closed scaffold rules
- `_ask/OWNED-PATHS.md` — SoT still `_ask/agents/`, `_ask/bindings/`; no `.agents/ask/` or `.agents/verification.yaml`
- `_ask/scripts/sync-runtime-agents.py` — reads `_ask/bindings/`; runtimes `cursor`, `claude`, `codex` only
- No `.starter-kit/verify.conf` in this repo

Alignment with Why (intent): the spec targets sequential chat-orchestrated 06–08, nondeterministic verify, and fragmented bindings — consistent with explore-map findings. Scope matches human decisions (TaskGraph, RED→GREEN, Git-flow, `.agents/ask/` canonical).

## Ambiguities

1. **Dirty-tree vs concurrent worktrees.** Outer policy requires `./ask check-clean` before Explore through Accept (`worktree.md`, `start-work.sh`). The spec requires per-task worktrees and cherry-pick onto `agent/<work-id>` but does not state which trees must be clean when (coordinator checkout, task worktrees, parent chat cwd). A cherry-pick stop leaves conflict markers on the coordinator branch — that is a dirty tree under `check-clean-worktree.sh`, yet outer stages forbid starting labor dirty.

2. **`owned_paths` semantics.** Scheduling uses glob overlap for concurrency and `validate_graph` → `path_conflict`, while integration uses “unexpected overlap” on the integrated diff. Glob rules (rename pairs, `**` vs directory moves, generated `.cursor/**` vs source `.agents/ask/**`) are unspecified. Two tasks can declare disjoint globs yet touch the same inode via symlink, generated output, or `./ask sync` rewriting projections.

3. **Overlap without `depends_on`.** Behavior says overlapping paths serialize via the DAG; failure table says “Cycle or overlapping ready writers → Refuse graph.” Unclear whether the coordinator auto-inserts dependency edges or rejects the graph when overlap exists without an explicit edge.

4. **TDD seam confirmation timing.** TaskResult requires a “confirmed seam (human-confirmed at Plan or task brief).” The runner is automated; who records confirmation in machine-readable form, and what fails if Plan omitted the seam but Implement ran?

5. **Reviewer for exemptions and debug bounds.** Typed exemptions need `reviewer_ack: true`. In concurrent task flow, “reviewer” is a spawned adapter, not the human — unclear whether adapter ack satisfies AC 5 or human grill is still required for exemption kinds that include “generated projections” (which still change runtime behavior via sync).

6. **E2E for this kit.** Explore-map and intent require Grill/Spec E2E contract. This repo has no product UI; E2E could mean kit shell tests, stage-journey smoke, or `not_applicable`. AC 6 mandates template and contract changes but the spec’s E2E section does not classify the starter-kit consumer.

7. **Isolation in a kit-only repo.** AC 10 mandates production-engine ephemeral resources for integration/E2E. This checkout has no production database; only `_ask/tests/test-*.sh`. Unclear whether kit verify uses universal `not_applicable`, empty declarations, or fake engine metadata.

8. **Git-flow vs current scripts and inventory.** Spec: `start-work` from `develop` only. Today: `start-work.sh` uses default branch (`main`/`master`). Explore-map pins later cards on `origin/develop` while this workstream runs on `agent/inner-loop-hardening` (likely from `main`). `./ask status` archive semantics reference default branch, not `develop`.

9. **OpenCode acceptance vs deferral.** AC 2 requires OpenCode output to match documented agent-file shape “at implement time.” Open questions defer frontmatter to implement time. Intent assumed format resolution during Spec/Plan — three-way tension.

10. **Context-engineering audit.** AC 12 refuses Accept if the audit task is missing or open and requires addressing “compressed grilling/protocol pointers.” No schema for audit evidence, pass/fail, or independence (same agent family that compressed context).

11. **Brownfield baseline.** “Discovered existing tools become the committed baseline” vs mandatory categories and fail-closed when tools missing — for a repo with eslint and biome both present, scaffold stops; if human never runs interactive scaffold, is verify permanently fail until a human session?

12. **`_ask/` vs `.agents/ask/` during transition.** Spec: stage SoT moves; `_ask/` remains dispatcher/scripts/tests. `OWNED-PATHS.md` and upgrade docs still kit-own `_ask/agents/`. Single `./ask sync` generator must read new paths while tests and ADRs still cite old paths until migration completes — ordering not specified.

## Missing failure cases

| Gap | Kit-grounded counterexample |
| --- | --- |
| Crash mid-cherry-pick | Coordinator `agent/<work-id>` has partial cherry-pick; `state.json` revision not incremented; invariant “coordinator_sha matches HEAD after integrate” false. `resume()` behavior unspecified (abort cherry-pick vs finish vs escalate). |
| Dual writers on state | Parent Implement chat manually edits `state.json` while runner CAS-loops — revision conflict is specified; human edit on coordinator branch during run is not. |
| Task branch ahead, coordinator behind | Worker commits on `agent/<id>/task/t2` while integrate of `t1` fails; stale-base cancel covers running tasks but not queued tasks whose `base_sha` was never updated. |
| Worker violates protocol | Worker writes `state.json` — “Reject; treat as protocol violation” — no required escalation artifact or graph halt scope. |
| Glob false negative | Task A `owned_paths: [_ask/scripts/*.sh]`, Task B `[ask]` — parallel ready if graph only globs `ask` under a path pattern; both mutate dispatcher entrypoint. |
| Glob false positive | Task A owns `**/*.md`, Task B owns `work/**/plan.md` — serialized entirely though plans could be disjoint work-id paths under one workstream. |
| Generated projection exemption | Task marks `exemption: generated projections` for `.cursor/agents/*`; sync output changes spawn behavior — reviewer ack without `./ask sync` diff review misses behavior change. |
| RED not production | Task proves RED on a throwaway test deleted before green — AC 5 says behavior-changing tasks need red/green; no invariant ties red command to `owned_paths` or seam file set. |
| verify.yaml absent brownfield | Motivating consumer: NestJS + legacy TS, eslint and biome configs, no `.agents/verification.yaml`. Fail-closed verify always fails; scaffold requires TTY choices — agent session cannot complete AC 9 without human at keyboard. |
| Pass-on-empty regression | Today `verify.sh` exits 0 when `CHECKS` empty. Spec fail-closed — good — but AC 13 adds `ask-kit` preset; until scaffold runs, kit repo must ship committed yaml or first `./ask verify` fails — migration beat unspecified. |
| Concurrent workstreams policy | `worktree.md` forbids parallel workstreams on overlapping protocol paths. Inner-loop task branches are in-workstream but still parallel git worktrees touching `_ask/scripts/verify.sh` and `.agents/ask/` — outer policy text does not carve an exception. |
| `develop` missing locally | Spec fail-closed `start-work` — branch exists on origin in this repo; fresh clone without `develop` checkout fails all new work until human creates branch — acceptable but undocumented in failure table. |

## Over-constraint risks

1. **AC 6 + template churn.** Mandating E2E sections in Grill/Spec/Plan/06/09 for every workstream forces this mega-workstream to edit many stage contracts before its own Accept — coupling all future specs to E2E boilerplate even when `not_applicable`.

2. **Fail-closed verify + interactive scaffold.** Correct for product repos; combined with “agents must not skip provisioning,” any delegated Verify stage blocks until a human completes TTY scaffold — conflicts with unattended agent sessions unless scaffold is explicitly human-only outside agent labor.

3. **No compatibility shims.** Breaking `_ask/agents/` without a phased pointer window makes incremental PRs on `agent/inner-loop-hardening` hard to review (every sync touches all projections).

4. **Integration stop on any unexpected overlap.** Attributable commits that touch files outside declared `owned_paths` (e.g. lockfile after provisioning task) stop the graph — may be intended but will fire often unless Plan normalizes owned_paths breadth.

5. **AC 12 Accept gate.** Refusing Accept for an “open” audit task without defining closed state risks permanent block or rubber-stamp closure.

## Under-constraint risks

1. **`validate_graph` vs runtime overlap detection.** Only test-backed operations are listed; no requirement that glob implementation match git diff overlap detection at integrate time — “unexpected overlap” becomes the real gate, late and expensive.

2. **Read-only agents sharing checkout.** Allowed for review/debug; no rule preventing a misconfigured read-only agent from writing via tool use — policy not machine-enforced.

3. **Cherry-pick order only.** No requirement that task commits be single-purpose or squashed — cherry-pick series order across multiple commits per task may still conflict ambiguously.

4. **Consumer overlay merge.** `./ask sync` merges `.agents/ask.local/` after kit source — conflict resolution and test coverage for overlay precedence unspecified.

5. **Codex “complete relative to template”.** Subjective without a golden file test list; spawn best-effort may mask incomplete TOML until live spawn fails.

6. **Later cards on `develop`.** Spec requires commit + tracker issue; no failure case when agent workstream branch targets `develop` PR but later card landed only on remote `develop` — merge-base confusion.

7. **Per-task checks vs outer verify.** Stated non-goal but inner-loop TaskResult “checks” field in explore hints — spec keeps 09 outer; easy for Plan to blur evidence aggregation.

## Recommended clarifications

### Must-fix (Spec Change before Plan)

1. **Dirty-tree contract for inner-loop.** Define clean-tree obligations: coordinator vs task worktrees; whether cherry-pick conflicts must abort to clean state before outer 09/10; whether task worktrees are exempt from `./ask check-clean` at spawn; who runs check-clean (runner vs human).

2. **Resume after partial integrate.** Add failure row + invariant repair: detect in-progress cherry-pick, mismatch between `coordinator_sha` and HEAD, and CAS revision rollback or escalate-only path.

3. **OpenCode AC 2 vs open questions.** Either pin acceptance to a documented schema version in spec (with pointer to external doc revision) or change AC 2 to file-shape tests only and move live-shape parity to optional matrix — remove “at implement time” as the sole acceptance hook.

4. **Interactive scaffold vs agent delegation.** State explicitly: provisioning is a human-in-the-loop wizard (not runnable in standard agent Verify labor), or define a non-interactive `--preset-accept` path forbidden for agents — align AC 9 with `_ask/scripts/verify.sh` replacement behavior.

5. **Kit-repo E2E and isolation (AC 6, 10).** Record in spec behavior: this consumer’s E2E = `not_applicable` with reason **or** named kit journeys; isolation declarations for no-DB kit repo (empty adapter list + explicit waiver).

6. **Path overlap validation rule.** Specify: overlapping `owned_paths` without covering `depends_on` edge → `validate_graph` error (not silent auto-edge), matching failure table wording.

7. **Context-engineering audit done-state.** Require auditable artifact (e.g. `work/<id>/context-audit.md` with checklist IDs) and pass rule; define “independent” (minimum: spawned role or subagent not used for Implement of same files).

8. **Worktree policy carve-out.** Update spec constraints to cite amendment of `worktree.md`: in-workstream task branches/worktrees are allowed; still forbid cross-workstream parallel overlap — or ESCALATE remains until policy file is in scope of What.

### Plan-ok (Plan may encode without Spec Change)

1. Exact glob library (pathspec, git pathspec, manual prefix rules) and rename tracking.

2. CLI surface (`./ask inner-loop run|resume|status`) and CAS file locking implementation.

3. `ask-kit` preset contents mapping to `_ask/tests/test-*.sh`.

4. TaskGraph schema for seam confirmation field (`seam_confirmed_by`, `seam_at_plan_sha`).

5. Cross-runtime acceptance matrix (file-shape mandatory rows per runtime).

6. Migration steps ordering: move `.agents/ask/` first vs dual-read period in `./ask sync`.

7. Brownfield NestJS consumer fixture repo for scaffold integration tests.

8. Auto-cancel algorithm for intersecting running tasks (git diff vs declared globs).

9. Changelog path discovery per product.

10. Debug adapter spawn limits wiring to runtime pools in `.agents/ask/bindings/`.

## Allowlist re-challenge (round 2)

Trigger: human rejected cherry-pick (branch semantics) and merge-conflict recovery;
required a filesystem/Git harness so agents cannot record files outside
`owned_paths`. That encoding is not yet safe.

### Counterexamples

1. **TDD writes that are not the product.** `pytest` / `ruff` / `tsc` write
   caches, coverage, and tmp under the worktree. A write-allowlist equal to
   `owned_paths` makes the first test run a harness failure. Those writes must
   not be committable or integrable.

2. **Test source vs test scratch.** A new test file is the RED evidence and
   belongs in `owned_paths` (committed). A file the agent “tweaks for the test
   without commit” is either scratch (must stay untracked) or a production edit
   smuggled off the branch (breaks TDD and merge safety).

3. **Plan-time file census.** If `owned_paths` is a per-file list, Plan spends
   the workstream enumerating paths and still misses renames, generated files,
   and `__init__.py`. Seam/module globs are the only scale that Plan can
   declare; the harness expands them at spawn.

4. **Mid-task discovery.** Implement finds the bug is in a file outside the
   glob. Auto-expanding the allowlist reintroduces overlapping writers.
   Silent extra commits are the merge disaster. The legal moves are: depend on
   a task that owns that glob, or escalate.

5. **Review/debug.** Spec allows read-only agents to share a checkout. Running
   tests still writes scratch. A shared checkout plus scratch writes can dirty
   a tree another role is reading. Review must not commit. Debug must use the
   same commit allowlist as implement for that task.

6. **Reads.** Import graphs and typecheck need the rest of the repo readable.
   A sparse worktree that omits non-owned files will false-fail `tsc`/`pytest`
   for reasons unrelated to merge safety.

### Spec gap

`owned_paths` is specified as writer globs and, in Spec Change §7, as both
filesystem write-allowlist and Git commit-allowlist with no third set for
uncommitted test output, no glob-vs-file rule, no mid-task discovery rule, and
no per-role write rights.

Until those are decided, §7 is under-constrained: it either blocks TDD or
fails to prevent merge disaster.

## Challenge verdict

**ESCALATE**

Round 1 gaps remain (dirty-tree, resume, OpenCode, provisioning, kit E2E,
overlap edges, audit, worktree carve-out). Round 2: commit-allowlist vs
write-allowlist vs scratch, glob granularity, and out-of-glob discovery are
unset. Grill before applying Spec Change to the proposal file.

**Spec Change before Plan:** yes — round 1 encodings plus allowlist layers
after this grill.

## After Spec Change (2026-09-20)

Human confirmed sequential writers, steering globs, commit-allowlist +
`git diff` review, `extras` vs `glob_too_narrow`, 2+2 then `blocked`. Applied
in `specs/proposals/inner-loop-hardening.md`. Challenge gate for those items:
closed. Remaining: Plan encodings listed under Open questions.

