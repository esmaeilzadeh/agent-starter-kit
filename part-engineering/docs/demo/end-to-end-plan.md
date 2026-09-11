# Demo plan: end-to-end with the AI Engineering Starter Kit

**Audience:** a developer who wants to see how this repo turns agent chat into accountable engineering labor.  
**Duration:** ~45–90 minutes for the happy path (Path A). Path B adds ~20 minutes for Explore.  
**Demo feature:** `kit-status` — a tiny script that prints whether this repo’s kit layout is healthy. Small enough to finish in one sitting; real enough to exercise every stage artifact.

Repo overview and doc index: root **[README.md](../../../README.md)**.

This plan is the **script for the demo**. Execute it in Cursor against this repository (or a clone). Protocol truth stays under `part-engineering/`; do not improvise stages from chat memory alone.

---

## What this demo proves

| Without the kit | With the kit |
| --- | --- |
| Chat is the only memory of What/Why | Durable `intent.md` + accepted `specs/` |
| Agent codes on a dirty tree / random branch | Clean-tree gate + `agent/<work-id>` branch |
| “Looks good” is the verification story | `./pek verify` + commit SHA provenance |
| Spec silently mutates mid-flight | Spec Change interrupt or return to Explore |
| Skills copied into the repo by hand | Pinned `manifest.yaml` + `./pek prepare` |

After the demo you can answer: *What were we building? Which spec? Which branch? Which commit passed verify? Who accepted?*

---

## Prerequisites

1. Clone this repo; open in Cursor.
2. Clean worktree: `./pek check-clean`
3. Read root `AGENTS.md` (≤1 minute).
4. Optional but recommended: `./pek prepare` (needs network / skills CLI). If offline, continue with kit protocol files only and note the gap.
5. Sync Cursor projections: `./pek sync`

**Human role in the demo:** own What/Why, answer grilling, accept the spec, accept the final result.  
**Agent role:** run stages `00`–`10` per `part-engineering/agents/*.md`, commit each meaningful step, never silent-stash a dirty tree.

---

## Path A — Clear intent (recommended first run)

Skip Explore. Destination is already sharp: *ship a read-only kit status script*.

### A0. Start the workstream

```bash
./pek check-clean
./pek start-work demo-kit-status
```

Expect: branch `agent/demo-kit-status`, seeded files under `work/demo-kit-status/`.

**Commit after:** workstream scaffold exists (usually already committed when you add real content).

### A1. Grill → Intent (`01`)

Open stage contract: `part-engineering/agents/01-grill.md` (or Cursor skill `kit-01-grill`).

**Human seed (say this to the agent):**

> What: add `scripts/kit-status.sh` that exits 0 and prints OK/MISSING for core kit paths (`AGENTS.md`, `part-engineering/`, `part-engineering/scripts/verify.sh`, `part-engineering/skills/manifest.yaml`).  
> Why: give developers a 10-second confidence check that the starter kit is present after clone/install.  
> Non-goals: no network calls, no modifying files, no CI yet.

**Agent must:** expand Q&A (Grilling Expansion) before “all ok”; write `work/demo-kit-status/intent.md`.

**Human:** confirm Intent.

**Commit:** `Intent for demo-kit-status`.

### A2. Spec (`02`)

Contract: `part-engineering/agents/02-spec.md`.  
Write `specs/proposals/demo-kit-status.md` from `part-engineering/templates/spec.md`.

Minimum behavior to specify:

- CLI: `scripts/kit-status.sh` (no args required)
- Checks listed paths; prints one line per check (`OK` / `MISSING`)
- Exit `0` if all OK, non-zero if any MISSING
- No writes to the filesystem

**Commit:** `Propose demo-kit-status specification`.

### A3. Spec Challenge (`03`)

Contract: `part-engineering/agents/03-spec-challenge.md`.  
Fill `work/demo-kit-status/spec-challenge.md`.

Probe at least:

- What if run outside a kit repo?
- Should untracked `scripts/kit-status.sh` itself be required after implement? (only after it exists)
- Output stability for tests

**Human:** accept challenge outcomes; promote spec to `specs/current/demo-kit-status.md` with `Status: CURRENT` (or move + update status).

**Commit:** `Accept demo-kit-status specification`.

### A4. Plan (`05`)

Contract: `part-engineering/agents/05-plan.md`.  
Write `work/demo-kit-status/plan.md`:

1. Add failing test `tests/test-kit-status.sh` (missing script → fail, or temp dir without kit → non-zero)
2. Implement `scripts/kit-status.sh`
3. Wire discovery so `./pek verify` picks up the new test
4. Run verify; record result

**Commit:** `Plan demo-kit-status implementation`.

### A5. Implement (`06`) — TDD slice

Contract: `part-engineering/agents/06-implement.md`.  
Preconditions: clean tree, on `agent/demo-kit-status`, CURRENT spec, plan present (`./pek check-workstream demo-kit-status`).

1. **Red:** add `tests/test-kit-status.sh` → commit  
2. **Green:** add `scripts/kit-status.sh` → commit  
3. Do not touch unrelated kit protocol files

### A6. Review (`07`)

Contract: `part-engineering/agents/07-review.md`.  
Write `work/demo-kit-status/review.md` (findings + verdict). Fix trivial issues with commits; if the **accepted spec** is wrong, stop → Spec Change (`04`), do not silent-edit `specs/current/`.

**Commit:** review artifact (+ fix commits if any).

### A7. Refactor (`08`) if needed

Only clarity/structure inside the script/test. Stay inside acceptance criteria.

**Commit:** refactor commit(s) or note “none required” in review/acceptance.

### A8. Verify (`09`)

```bash
./pek verify
./pek record-result --work-id demo-kit-status --commit-sha "$(git rev-parse HEAD)" --result pass
```

Fill `work/demo-kit-status/verification.json` (or rely on verify output + `result.json`).

**Commit:** verification / result artifacts.

### A9. Accept (`10`)

Contract: `part-engineering/agents/10-accept.md`.  
Complete `work/demo-kit-status/acceptance.md` with the **exact** commit SHA.

**Human:** explicit accept (this is authority, not another LLM “LGTM”).

**Commit:** `Accept demo-kit-status @ <sha>`.

### A10. Show the punchline (live)

```bash
./scripts/kit-status.sh
git log --oneline main..HEAD   # or from branch point
ls work/demo-kit-status/
head -30 specs/current/demo-kit-status.md
```

Narrate: *artifacts + SHA, not the chat scrollback, are the record.*

Merge to `main` when ready (local merge + push is fine; no PR required if that is your workflow).

---

## Path B — Foggy first (optional Explore showcase)

Use when you want to demo **00 Explore** before Intent.

**Human seed (deliberately vague):**

> “I want something that tells me if the agent kit is set up right.”

### B0. Start workstream

```bash
./pek start-work demo-kit-status
```

### B1. Explore (`00`)

Contract: `part-engineering/agents/00-explore.md` — **not** Cursor’s built-in Explore subagent.

1. Prepare Explore skills if using Community Skills: `./pek prepare`
2. Chart `work/demo-kit-status/explore-map.md` (template already seeded)
3. Grill options: shell script vs doc-only checklist vs Cursor rule-only
4. Decide: shell script status check (matches Path A)
5. Fill **non-empty** `## Handoff to Intent`

**Commit:** explore-map with handoff.

Then continue from **A1 Grill** through **A9 Accept**.

---

## Interrupts to mention (do not need to run live)

| If this happens | Do this |
| --- | --- |
| Dirty tree before a stage | Stop; grill human per `part-engineering/policies/worktree.md` |
| Agent wants to weaken acceptance criteria | Escalate; forbidden by delegation policy |
| Review finds spec semantically wrong | `04 Spec Change` artifact — never silent rewrite |
| Destination itself was wrong | Return to `00 Explore` |
| Second related feature needs overlapping files | Serialize branches; do not parallelize conflicting workstreams |

---

## Demo checklist (facilitator)

- [ ] Clean tree gate shown failing once (create a junk file → `./pek check-clean` / `./pek start-work` refuse → delete junk)
- [ ] Dedicated branch `agent/demo-kit-status` visible
- [ ] Intent → Spec → Challenge → Plan artifacts on disk
- [ ] At least two implementation commits (red then green), not one mega-commit
- [ ] `./pek verify` prints commit SHA
- [ ] `acceptance.md` cites that SHA
- [ ] Audience can open files and reconstruct the story without the chat

---

## Out of scope for this demo

- Phase 3 workflow-quality machinery
- CI wiring
- `./pek install` into a second toy repo (nice encore if time: dry-run then apply on a temp git repo)
- Real payment/domain product features

---

## Encore (optional, +15 min)

```bash
TMP=$(mktemp -d)
git init "$TMP" && git -C "$TMP" commit --allow-empty -m init
./pek install --dry-run "$TMP"    # show docs/ exclusion story
SKIP_INSTALL=1 ./pek install --skip-prepare "$TMP"
ls "$TMP/part-engineering" "$TMP/AGENTS.md" "$TMP/pek"
```

Shows overlay install without fighting a consumer’s `docs/`.

---

## References

| Thing | Path |
| --- | --- |
| Agent checklist | `AGENTS.md` |
| Stage contracts | `part-engineering/agents/` |
| Worktree policy | `part-engineering/policies/worktree.md` |
| Spec examples | `part-engineering/spec/05-examples-and-binding.md` §31 |
| This workstream (plan authoring) | `work/demo-e2e-plan/` |
