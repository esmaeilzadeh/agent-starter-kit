# Review

## Model

- model: inherit
- runtime: cursor
- parent_model: cursor-grok-4.6
- Same-family warning: inherit is the same family as Implement (cursor-grok-4.6); defaults-OK already covers a second bless.

This spawn did not Implement t1–t13. Review commits nothing. Per-task `review.verdict` JSON was left PENDING.

## Scope

Outer 07 after t1–t13 on `agent/inner-loop-hardening`. Spec: `specs/current/inner-loop-hardening.md` (CURRENT). Plan: `work/inner-loop-hardening/plan.md`. TaskGraph: `work/inner-loop-hardening/inner-loop/tasks.yaml`. Policies: `_ask/policies/{worktree,git-flow,verification,workflow}.md`. Context audit: `work/inner-loop-hardening/context-audit.md` (CE-01..CE-06 pass).

Checked ACs 1–13, invariants (one writer, fail-closed verify, `.agents/ask/` SoT, FF-only integrate), and named tests (`test-inner-loop.sh`, `test-verify-fail-closed.sh`, `test-start-work-from-develop.sh`, `test-e2e-contract-sections.sh`, `test-sync-canonical-ask.sh`, `test-stages-inner-loop.sh`).

**Met (keep):**

- AC 1 core: `.agents/ask/{stages,bindings,verification}/` exists; `_ask/agents/*.md` and `_ask/bindings/README.md` are pointers; `OWNED-PATHS.md` lists `.agents/ask/`; `_ask/tests/test-sync-canonical-ask.sh` prefers `.agents/ask/stages`.
- AC 2: `_ask/tests/test-sync-runtime-agents.sh` asserts OpenCode `description` / `mode: subagent` / `model`, no `tools`/`maxSteps`, review `edit: deny`. Pin: `work/inner-loop-hardening/plan.md` OpenCode pin (https://opencode.ai/docs/agents, 2026-09-20).
- AC 4 library: `_ask/tests/test-inner-loop.sh` refuses a second `spawn-writer`; `check-index` rejects staged paths outside globs. Filesystem is not reduced to `owned_paths`.
- AC 6: intent/spec/plan templates and 01/02/05/06/09 contain `e2e` and `not_applicable` (`_ask/tests/test-e2e-contract-sections.sh`). This kit: `e2e: not_applicable` via `ask-kit` in `.agents/verification.yaml`.
- AC 7 fail-closed core: missing yaml and empty checks fail (`_ask/tests/test-verify-fail-closed.sh`); `_ask/scripts/verify.sh` execs `.agents/ask/verification/run.py`; no `npm test`/`pytest`/`cargo test` in verify core.
- AC 11 start-work: `_ask/tests/test-start-work-from-develop.sh`; `_ask/scripts/start-work.sh` fails closed without `develop`. No script merge/tag/push of `main`. Hotfix table in `_ask/policies/git-flow.md`.
- AC 13: `.agents/verification.yaml` `presets: [ask-kit]`; `.agents/ask/verification/presets/ask-kit.yaml` glob `_ask/tests/test-*.sh`.
- Inner-loop 06–08: `.agents/ask/stages/{06-implement,07-review,08-refactor}.md` call `./ask inner-loop`; `_ask/tests/test-stages-inner-loop.sh`; no TaskGraph YAML inlined. Worktree one-writer carve-out: `_ask/policies/worktree.md` Inner-loop writers.
- Context-audit artifact closed (CE-01..CE-06 `pass`).
- Upgrade preserves `.agents/verification.yaml` (`_ask/scripts/upgrade-kit.sh` preserve list). `.agents/ask.local/` is not in the refresh list.

**Not met:** AC 3 orchestrator + resume-from-state, AC 5 integrate TDD gate, AC 8/9 scaffolder+wizard+language presets, AC 10 product isolation runner, AC 11 later-card commit/tracker, AC 12 Accept audit refuse, AC 1 dispatcher help SoT.

## Findings

### F1 — `run` / `resume` / `cancel` / `run_until` / `integrate_ready` are stubs (AC 3, Interfaces, 06)

`.agents/ask/stages/06-implement.md` tells 06 to run `./ask inner-loop run` (or `resume`) when `tasks.yaml` exists. `_ask/scripts/inner_loop/__main__.py` registers `run`, `resume`, and `cancel`, then prints `{cmd} not implemented yet` and returns 2.

Spec Interfaces require `run_until`, `cancel(task_id|all)`, `resume(from state.json)`, `integrate_ready()`. Tests hit primitives only (`validate`, `cas-apply`, `spawn-writer`, `next-action`, `integrate --method ff-only`, `resume-repair`). `resume-repair` takes `--coordinator-sha`; it does not load `work/<id>/inner-loop/state.json` or continue the next non-integrated task.

t3 notes said stubs until t5; t5 notes left `run`/`resume`/`cancel` stubbed. No later task implemented the driver. This workstream has no `state.json`.

Commit allowlist is `check-paths` / `check-index` (CLI). There is no git hook and no `run` path that calls them before commit. Spec: Git stage and commit reject outside expanded globs; policy prose is not the gate.

`spawn_writer` raises `SecondWriter`; `__main__.py` does not catch it (traceback still matches the test grep).

### F2 — Integrate does not require TDD or exemption `reviewer_ack` (AC 5, invariant)

`_ask/scripts/inner_loop/integrate.py` `integrate()` is `git merge --ff-only`. No read of TaskResult `tdd` or `exemption.reviewer_ack`. Grep of `_ask/` scripts: no `reviewer_ack`. Missing red/green or unchecked exemption can still land if someone fast-forwards.

TaskResult JSON on this branch records TDD for behavior-changing tasks and `reviewer_ack: true` on t12/t13, with `review.verdict: PENDING`. Harness does not enforce eligibility.

### F3 — Scaffolder/wizard/presets miss AC 8 and AC 9

`_ask/scripts/verify_scaffold.py`: `--preset ask-kit` writes a constant yaml; existing file left in place; `--re-scaffold` writes `.candidate`; eslint+biome at repo root stops. Non-TTY without `--preset` refuses. TTY without `--preset` prints that the interactive wizard is human-only and returns 2 — no preview, confirm, or rollback. Tests: `_ask/tests/test-verify-scaffold.sh`, `_ask/tests/test-setup-human-only.sh`. AC 9: wizard preview + confirm + rollback are tested.

No TypeScript or Python preset files under `.agents/ask/verification/presets/` (only `ask-kit.yaml`). Scaffolder does not inspect `package.json` workspaces, `pnpm-workspace.yaml`, or sibling `pyproject.toml` / `package.json`. Brownfield fixture `_ask/tests/fixtures/brownfield-mixed/` is root eslint+biome + `package.json`, not named workspace sections. AC 8 mixed-stack named sections / workspace-local config win-or-stop is unmet beyond the lint-pair stop.

Missing yaml names the wizard (`plan.py` FileNotFoundError). Verify does not detect a language then fail a missing typecheck/lint/test/E2E category (AC 9).

### F4 — Product isolation runner absent (AC 10)

Kit yaml: `no_production_datastore: true`, `adapters: []` (AC 10 kit half). `run.py` does not refuse listed dev/prod identifiers, confine destructive commands, or record leaks. No product-repo fixture test for that runner. Spec Isolation (product repos) is unmet.

### F5 — Later cards still gitignored; no tracker issue (AC 11)

Spec / `_ask/policies/git-flow.md`: commit `.later/<slug>.md` on `develop` and link a tracker issue.

`.gitignore` lines 16–17: `.later/*` with `!.later/README.md`. `_ask/tests/test-later-inbox-gitignore.sh` asserts cards are ignored. `_ask/docs/adr/0015-later-inbox.md` still says gitignored. `_ask/spec/04-scripts-and-git.md` §23.0a says commit on develop; §23.4 says no issue-tracker sync. Feature is prose plus a contradicting gitignore/test.

### F6 — Accept does not refuse a missing or open context-audit (AC 12)

Spec: Accept refuses if `work/<id>/context-audit.md` is missing or any checklist ID is `open`.

`.agents/ask/stages/10-accept.md` has no audit gate. `_ask/agents/10-accept.md` is a pointer. `_ask/scripts/check-workstream.sh` checks spec/plan, not the audit. `_ask/templates/acceptance.md` has no audit field. This workstream’s audit file exists and is closed; the durable refuse is missing.

### F7 — Dispatcher help still names `_ask/agents` as sync SoT (AC 1)

`ask` `usage()` (sync bullet) says regenerate from `_ask/agents/` and `_ask/bindings/`. Sync implementation prefers `.agents/ask/` (`_ask/scripts/sync-cursor-binding.sh`). t12 notes recorded this as outside the t12 glob. Kit tests/docs match is incomplete while `./ask --help` names the old SoT.

## Suggested fixes

08 stays inside accepted spec (no What/Why change).

1. Implement `run` / `resume` / `cancel` so they call `load_graph`, `validate_graph`, one-writer schedule, `check-index` before commit, `integrate` FF-only, CAS `coordinator_sha`/`revision`, and `resume` from `state.json` (abort to ancestor SHA then next non-integrated task). Catch `SecondWriter`. Tests in `_ask/tests/test-inner-loop.sh` for `run_until` quiescent, cancel, resume-from-state, TDD/exemption refuse (F1+F2).
2. Gate `integrate_ready`: behavior-changing TaskResult needs red then green; exemption needs `reviewer_ack: true`. `glob_too_narrow` does not consume a remediation round (already in `retry.next_action`).
3. Scaffolder: inspect manifests/lockfiles/tool configs; TypeScript and Python presets as files under `.agents/ask/verification/presets/`; mixed workspaces as named sections or stop on disagreement. Interactive wizard: preview, confirm, rollback of mutated product files; tests as AC 9. Agent Verify still does not run the wizard; missing mandatory category names it (F3).
4. Isolation checks in verify (or a called module): refuse listed dev/prod identifiers; record leaks. Fixture tests. Kit `no_production_datastore` path stays (F4).
5. Stop gitignoring `.later/*.md` (keep README kit-owned). Align ADR 0015 and `_ask/spec/04-scripts-and-git.md` §23.4 with git-flow: cards commit on `develop` and link a tracker issue. Replace `test-later-inbox-gitignore.sh` (F5).
6. Add the Accept refuse to `.agents/ask/stages/10-accept.md` (and `./ask sync`). Optionally `check-workstream` warning. Template field on `acceptance.md` (F6).
7. Fix `ask` `usage()` sync text to `.agents/ask/` (F7). t12 glob did not include `ask`; 08 must own that path or queue a glob that does.

## Residual risks

- All 13 files under `work/inner-loop-hardening/inner-loop/results/` have `review.verdict: PENDING`. This outer 07 folds that: per-task boundary `git diff` vs `owned_paths` was not independently recorded as APPROVED. `owned_paths_touched` in those JSON files is inside each task’s globs as declared; extras were not re-diffed here. t12/t13 set `reviewer_ack: true` while verdict is PENDING.
- Plan encoding: this workstream did not dogfood `./ask inner-loop run` (bootstrap). Later workstreams will hit F1 immediately.
- `verification.yaml` has `e2e: not_applicable` with no reason string; the reason lives in the spec. 09 asks for plus reason.
- Glob expand is custom `glob_to_re` (`_ask/scripts/inner_loop/graph.py`), not stdlib `fnmatch` as Plan encoding. Spec allows this encoding.
- Codex/OpenCode live spawn remains best-effort (`ASK_LIVE_SPAWN`); file-shape is tested.
- No `state.json` on this workstream; CAS/resume invariants for this graph were not exercised on the coordinator checkout.
- Review inherit / Implement same family: independence is spawn-separation only, not a second model family.
- `_ask/tests/test-workstream-smoke.sh` calls `start-work` in a temp repo with no `develop` (fails closed after t9). Outer `./ask verify` fails on that check until 08 seeds `develop` in the smoke fixture.

## Review verdict

REJECTED
