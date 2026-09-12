# Plan

## Specification

No separate `specs/` file. Contract lives in kit protocol:

- `_ask/policies/workflow.md` — default path is guidance; skip = warn once + follow
- `_ask/spec/04-scripts-and-git.md` §23.4 — `./ask status` + `code-without-plan` warning
- Stage contracts under `_ask/agents/` must match (guidance, not refuse-for-missing-artifacts)
- Safety refusals stay hard: dirty tree, silent stash/reset, fake verify/accept, silent What/Why change

**Already on this branch (do not redo):** policy file, AGENTS checklist item, Cursor `workflow-guidance.mdc`, Implement/Plan emphasis, delegation “never silently”, status warning + test, spec/MAPPING pointers.

## Approach

Finish the first slice so the *whole kit* tells one story: agents default to the next stage and auto-continue at exit criteria; if the human jumps, warn once and proceed. Align leftover SoT that still reads like a lock (`check-workstream` as “refuse Implement”, spec § implement hard preconditions, Guide, demo, unused stage contracts).

Do **not** add a new lock script. `./ask check-workstream` stays a **check** (exit non-zero = “default path incomplete”). Agents interpret that as warn+ask, not stop-the-human.

## Work breakdown

1. **Align remaining stage contracts** (`00`–`04`, `07`–`10`) with one shared “Kit emphasis” stanza: default next-stage + auto-continue; on skip, warn once / follow; pointer to `workflow.md`. Keep stage-specific must/must-not. Sync Cursor projections.

2. **Soften spec wording that still locks Implement** — `_ask/spec/03-policies-skills-context.md` “Hard preconditions” / “accepted spec + plan” → default preconditions; missing spec/plan is a warning path. `check-workstream` docs: check for the default path, not a padlock.

3. **Guide + demo + CONTEXT** — `_ask/guide/02-workflow.md`: default path, skip-with-warning, auto-continue at human gates only. Demo: one line that a jump is allowed if warned. `CONTEXT.md`: **Workflow guidance** term.

4. **ADR** — short `0013-workflow-guidance-not-lock.md` (default path, warn+follow, what stays hard).

5. **Optional helper (only if it stays thin):** `./ask next` or status `--next` printing recommended next stage + warnings for current `--work-id`. Skip if status output is enough.

6. **Verify + merge** — `./ask verify`; merge `agent/ask-status` to `main` when you accept.

## Risks

- Agents still treat `check-workstream` non-zero as refuse (habit). Mitigation: explicit “not a lock” in the script’s stderr when spec/plan missing vs dirty-tree.
- Warning spam. Mitigation: warn **once** per deviation; status flag is enough after that.
- Scope creep into autoplay `/01`…`/10` as one unattended job. Out of scope — auto-continue is in-conversation, not a batch runner.

## Verification approach

- Existing `_ask/tests/test-status.sh` (`code-without-plan`, merged ≠ live).
- If `check-workstream` message is split: add a test that missing plan exits non-zero with “guidance” wording, not “forbidden”.
- `./ask verify` on this branch.
- Manual: `./ask status` shows `ask-status` live/planned, merged work archived.

## Out of scope for this plan

- Locking Implement or requiring slash commands per stage.
- Committed `work/INDEX.md`.
- Deleting leftover `agent/*` branches automatically.
- External tracker.
- Changing dirty-tree / verify-SHA hard gates.
