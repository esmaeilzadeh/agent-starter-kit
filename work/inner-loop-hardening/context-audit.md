# Context-engineering audit

Workstream: `inner-loop-hardening`.
Accepted spec: `specs/current/inner-loop-hardening.md` (Context-engineering audit).
Plan: `work/inner-loop-hardening/plan.md` (`t13-context-audit`, CE-01..CE-06).
Pointer/wording repairs after first audit: commit `e9adbcd` on `agent/inner-loop-hardening`.

## Independence

This spawn did not Implement t1–t12 files (parent applied pointer repairs after the first audit). It wrote only this artifact.

## Closed set

| ID | Check | Verdict |
| --- | --- | --- |
| CE-01 | Instruction hierarchy: AGENTS.md → policies → `.agents/ask/stages` | pass |
| CE-02 | 06–08 point at the runner; they do not inline a DAG | pass |
| CE-03 | 01 Grill still requires expanded load-bearing questions | pass |
| CE-04 | Fail-closed verify is reachable from 09 without shell-overlay language | pass |
| CE-05 | One-writer + dirty-tree gates still visible from always-on pointers | pass |
| CE-06 | Compressed grilling/protocol pointers from this workstream are repaired | pass |

Open IDs: none.

---

## CE-01

**Verdict:** pass

**Evidence:**

- `AGENTS.md:5`: Protocol SoT for stages, bindings, and verification is `.agents/ask/`. `_ask/agents` and `_ask/bindings` are pointers.
- `AGENTS.md:15`: Read `_ask/policies/` (`delegation.md`, `risk.md`, `verification.md`, `worktree.md`, `workflow.md`, `git-flow.md`).
- `AGENTS.md:11`: `./ask sync` so `.cursor/skills` and `.cursor/commands` match `.agents/ask/`.
- `.cursor/rules/starter-kit-bootstrap.mdc:6-8`: Protocol SoT is `.agents/ask/` (stages, bindings, verification) plus `_ask/` (guide, spec, policies). Before labor: `AGENTS.md`, then `_ask/policies/`, then stage contracts under `.agents/ask/stages/`.
- `CONTEXT.md:71-72`: Kit Protocol File example `.agents/ask/stages/01-grill.md`; `_ask/agents/*.md` are pointers to those stages.
- Generated Cursor agents name the stage files: `.cursor/agents/kit-01-grill.md` → Protocol: `.agents/ask/stages/01-grill.md` (same pattern for 00–10).

**Finding:** Always-on `AGENTS.md` and bootstrap name `.agents/ask/` then policies then `.agents/ask/stages/`; generated skills/agents load those stage files.

---

## CE-02

**Verdict:** pass

**Evidence:**

- `.agents/ask/stages/06-implement.md:52-56`: Inner-loop section. When `work/<work-id>/inner-loop/tasks.yaml` exists, run `./ask inner-loop run` (or `resume`). Scheduling, retry, CAS, and evidence fold live in `_ask/scripts/inner_loop/`. Quote: `This contract does not copy the DAG.`
- `.agents/ask/stages/07-review.md:33`: When that TaskGraph file exists, review the current writer only (`./ask inner-loop status`).
- `.agents/ask/stages/08-refactor.md:38`: Invoke `./ask inner-loop` for this writer; do not start a second task.

Grep of `.agents/ask/stages/{06-implement,07-review,08-refactor}.md` for `TaskGraph|inner-loop|DAG|tasks.yaml`: hits are the CLI/module pointers and the `tasks.yaml` path as the graph file to load. No task ids (`t1-` …). No YAML DAG (`depends_on:` lists, node tables).

**Finding:** 06–08 call `./ask inner-loop` / `_ask/scripts/inner_loop/`; they do not inline a DAG.

---

## CE-03

**Verdict:** pass

**Evidence:**

- `.agents/ask/stages/01-grill.md:20`: `expand each numbered question before resolution (alternatives, tradeoffs, failure modes — not bare A/B/C alone)`
- `.agents/ask/stages/01-grill.md:27`: `never treat “all ok” as valid if a load-bearing question was never expanded`
- `.agents/ask/stages/01-grill.md:48-54`: Grilling Expansion. Two blocks: (1) expanded load-bearing questions; (2) short “I’ll assume…”. Never treat “all ok” as valid if a load-bearing question was never expanded.
- `CONTEXT.md:31-33`: Grilling Expansion — alternatives, tradeoffs, and failure modes visible before resolution.

**Finding:** 01 Grill still requires expanded load-bearing questions before “all ok”.

---

## CE-04

**Verdict:** pass

**Evidence (09 names `./ask verify` fail-closed CheckPlan):**

- `.agents/ask/stages/09-verify.md:5`: `Evidence via ./ask verify (fail-closed CheckPlan) and _ask/templates/verification.json.`
- `.agents/ask/stages/09-verify.md:15-18`: Run `./ask verify`. The committed CheckPlan is `.agents/verification.yaml`. Empty CheckPlan or zero mandatory checks fails closed. Logic lives in `.agents/ask/verification/`. Language CLIs live in presets, not in this contract and not in `_ask/scripts/verify.sh`.
- `.agents/ask/stages/09-verify.md:20-21`: Do not overlay `./ask verify` with npm, pytest, cargo, or any other language CLI.
- `.agents/ask/stages/09-verify.md:29-30`: Claiming verify without running `./ask verify` or a commit SHA stays hard.

**Evidence (dispatcher core):**

- `_ask/scripts/verify.sh:1-7`: `Run the language-neutral CheckPlan. Logic lives in .agents/ask/verification/.` Then `exec python3 "$ROOT/.agents/ask/verification/run.py"`.
- `.agents/ask/verification/run.py:1`: `Language CLIs live in presets, not here.`
- `.agents/ask/verification/run.py:35-38`: empty CheckPlan or zero mandatory checks → stderr `verify: empty CheckPlan or zero mandatory checks`, return 1.

**Finding:** 09 names fail-closed CheckPlan and forbids language-CLI overlay; `./ask verify` fail-closes in dispatcher core.

---

## CE-05

**Verdict:** pass

**Evidence (always-on → dirty-tree):**

- `AGENTS.md:12`: Clean worktree (hard gate): never start labor on a dirty tree. Run `./ask check-clean`. If dirty, grill the human — do not stash or reset silently. See `_ask/policies/worktree.md`.
- `.cursor/rules/starter-kit-bootstrap.mdc:10`: Worktree (hard): never start on an unclean tree. If dirty, grill the human. See `_ask/policies/worktree.md`.
- `.cursor/rules/workflow-guidance.mdc:5`: Dirty tree, silent stash/reset, and fake verify/accept stay hard. Canonical: `_ask/policies/workflow.md`.
- `_ask/policies/worktree.md:4-17`: Never start dirty. `./ask check-clean`. Grill; no silent stash/reset.

**Evidence (always-on → one-writer):**

- `AGENTS.md:13-15`: One plan → one branch (`./ask start-work` from `develop`). Do not run multiple related branches that touch common files in parallel. Read `_ask/policies/worktree.md`.
- `.cursor/rules/starter-kit-bootstrap.mdc:10`: One plan per `agent/<work-id>` branch; do not run overlapping related branches in parallel. See `_ask/policies/worktree.md`.
- `.cursor/rules/commit-step-discipline.mdc:7-8`: Canonical policy `_ask/policies/worktree.md`. Checklist: root `AGENTS.md`.
- `_ask/policies/worktree.md:52-53`: **One writer.** At most one task may have unintegrated commits. The runner starts the next ready task only after integrate.

**Finding:** Dirty-tree is inlined on always-on `AGENTS.md` and bootstrap; inner-loop one-writer is one hop from those same pointers into `worktree.md`. Pointer repairs in `e9adbcd` left these gates in place.

---

## CE-06

**Verdict:** pass

**Evidence (always-on, after `e9adbcd`):**

- `.cursor/rules/starter-kit-bootstrap.mdc:6`: Protocol source of truth is `.agents/ask/` (stages, bindings, verification) plus `_ask/` (guide, spec, policies). This rule is not SoT.
- `.cursor/rules/starter-kit-bootstrap.mdc:8`: stage contracts under `.agents/ask/stages/`.
- `.cursor/rules/writing-for-agents-machine-docs.mdc:8`: machine-first includes `.agents/ask/` and `_ask/agents/` (pointers).
- `AGENTS.md:5`: SoT is `.agents/ask/`. `_ask/agents` and `_ask/bindings` are pointers.

**Evidence (policy hop repaired):**

- `_ask/policies/workflow.md:12`: See `AGENTS.md` item 1 and `.agents/ask/stages/00-explore.md`.

**Evidence (research snapshot may keep old paths):**

- `_ask/docs/research/cursor-binding-surfaces.md:7`: Path note (2026-09-20): stage-contract SoT is `.agents/ask/stages/` (ADR 0018). Paths below that name `_ask/agents/` are this research snapshot.
- `_ask/agents/00-explore.md` and `_ask/agents/09-verify.md` remain pointers to `.agents/ask/stages/`.

**Finding:** Always-on bootstrap and machine-first rule name `.agents/ask/` as SoT; workflow Explore pointer names `.agents/ask/stages/00-explore.md`; leftover `_ask/agents/` paths are labeled pointers or ADR 0018 research snapshot.
