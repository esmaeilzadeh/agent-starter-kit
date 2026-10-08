# Demo plan: end-to-end with the AI Engineering Starter Kit

**Audience:** a developer who wants to see how this repo turns agent chat into accountable engineering labor.  
**Duration:** ~45–90 minutes for the happy path (Path A). Path B adds ~20 minutes for Explore.  
**Demo feature:** SHA-bound moons MLP experiments — change `results/<run-id>/config.yaml` and/or trainer code, **commit**, train, then `./ask record-run` so each metric cites **path + git SHA**.

Repo overview and doc index: root **[README.md](../../../README.md)**.

This plan is the **script for the demo**. Execute it in Cursor against this repository (or a clone). Protocol truth stays under `.agents/ask/` (stages, bindings, verification) plus `_ask/` (guide, spec, policies). Do not improvise stages from chat memory alone.

---

## What this demo proves

| Without the kit | With the kit |
| --- | --- |
| Chat is the only memory of What/Why | Durable `intent.md` + accepted `specs/` |
| Agent codes on a dirty tree / random branch | Clean-tree gate + `agent/<work-id>` branch |
| “Looks good” / a score with no SHA | `./ask record-run` + `results/RUN_REGISTRY.md` |
| Spec silently mutates mid-flight | Spec Change interrupt or return to Explore |
| Skills copied into the repo by hand | Pinned `manifest.yaml` + `./ask prepare` |

After the demo you can answer: *Which experiment? Which metric? Which git SHA? Which artifact path? Who accepted the workstream?*

---

## Prerequisites

1. Clone this repo; open in Cursor.
2. Clean worktree: `./ask check-clean`
3. Read root `AGENTS.md` (≤1 minute).
4. Optional but recommended: `./ask prepare` (needs network / skills CLI). Includes `developing-with-streamlit` @ `streamlit/agent-skills#v1`.
5. Sync Cursor projections: `./ask sync`
6. Demo Python extras: `pip install -r scripts/requirements-demo.txt`

**Human role in the demo:** own What/Why, answer grilling, confirm defaults OK (covers later prepared artifacts), accept the final result. `/off-path` (or “just code”) leaves the kit for **this chat only**.  
**Agent role:** run stages `00`–`10` per `.agents/ask/stages/*.md`, **prepare each artifact** (do not skip documents), commit each meaningful step on `agent/<work-id>` without waiting to be asked, never silent-stash a dirty tree. `/off-path` is this session only — warn once and follow; a new chat starts on-path.

---

## Path A — Clear intent (recommended first run)

Skip Explore. Destination is already sharp: *record two moons runs whose metrics bind to different HEAD SHAs*.

Shipped vehicle (already in the kit): `scripts/train_moons.py`, `scripts/view_runs.py`, `./ask record-run`.

### A0. Start the workstream

```bash
./ask check-clean
./ask start-work demo-moons-run
```

Expect: branch `agent/demo-moons-run` from `develop` (Git-flow), seeded files under `work/demo-moons-run/`.

### A1. Grill → Intent (`01`)

**Human seed:**

> What: add run `moons-narrow` (`hidden_layer_sizes: [8]`) and run `moons-wide` (`hidden_layer_sizes: [32]`). Each run’s `config.yaml` lives in `results/<run-id>/`. Commit that config (and any trainer edit) before training. Record each metric with `./ask record-run` bound to HEAD.  
> Why: show that a score without path + SHA is not citable.  
> Non-goals: PyTorch, MNIST, changing kit Accept policy.

**Agent must:** expand Q&A before “all ok”; write `work/demo-moons-run/intent.md`.

**Commit:** Intent.

### A2–A4. Spec, challenge, plan

Specify: per-run YAML; commit-before-train; `record-run` refuses dirty tree and SHA ≠ HEAD; registry row is path + SHA + metric. Streamlit viewer lists rows.

### A5. Implement (`06`) — two committed runs

On `agent/demo-moons-run`, clean tree:

```bash
mkdir -p results/moons-narrow
cat > results/moons-narrow/config.yaml <<'YAML'
seed: 0
n_samples: 200
noise: 0.25
hidden_layer_sizes: [8]
learning_rate_init: 0.01
max_iter: 400
YAML
git add results/moons-narrow/config.yaml
git commit -m "Experiment moons-narrow: hidden=8."
python3 scripts/train_moons.py --run-id moons-narrow
./ask record-run --run-id moons-narrow --commit-sha "$(git rev-parse HEAD)" --metric "$(python3 -c 'import json; print(json.load(open("results/moons-narrow/train_output.json"))["accuracy"])')"
```

Repeat for `moons-wide` with `hidden_layer_sizes: [32]` (new commit, then train, then `record-run`).

Do **not** train on a dirty tree. `record-run` will refuse.

### A6–A9. Review, verify, record-result, Accept

`./ask verify` is kit tests (does not require sklearn).  
`./ask record-result --work-id demo-moons-run --commit-sha "$(git rev-parse HEAD)" --result pass` closes the **workstream**.  
Each **experiment** is already in `results/RUN_REGISTRY.md`.

### A10. Punchline

```bash
column -t -s '|' results/RUN_REGISTRY.md || cat results/RUN_REGISTRY.md
streamlit run scripts/view_runs.py
```

Two rows, two SHAs. Narrate: *the registry, not the chat, is the scoreboard.*

---

## Path B — Foggy first (optional Explore showcase)

**Human seed (deliberately vague):**

> “I want to keep track of neural-net experiments so I know which code produced which score.”

### B0–B1

`./ask start-work demo-moons-run`. Create `explore-map.md` from the template (`start-work` does not seed it). Grill: workstream `record-result` vs per-run `record-run`; config-in-run-dir vs shared `configs/`. Handoff: per-run YAML + commit + `record-run`. Then A1–A9.

---

## Interrupts to mention (do not need to run live)

| If this happens | Do this |
| --- | --- |
| Dirty tree before a stage or `record-run` | Stop; grill per `_ask/policies/worktree.md` |
| Agent wants to weaken acceptance criteria | Escalate; forbidden by delegation policy |
| Review finds spec semantically wrong | `04 Spec Change` — never silent rewrite |
| Destination itself was wrong | Return to `00 Explore` |
| Second related feature needs overlapping files | Serialize branches |

---

## Demo checklist (facilitator)

- [ ] Clean tree gate shown failing once
- [ ] Dedicated branch `agent/demo-moons-run` visible
- [ ] Two run dirs, two commits, two `record-run` rows with different SHAs
- [ ] Streamlit viewer shows both configs
- [ ] `./ask verify` prints commit SHA
- [ ] `acceptance.md` cites the workstream SHA
- [ ] Audience can reconstruct the story without the chat

---

## Out of scope for this demo

- Phase 3 workflow-quality machinery
- CI wiring
- PyTorch / MNIST / ILP-Popper
- Real payment/domain product features

---

## Encore (optional, +15 min)

```bash
TMP=$(mktemp -d)
git init "$TMP" && git -C "$TMP" commit --allow-empty -m init
./ask install --dry-run "$TMP"
SKIP_INSTALL=1 ./ask install --skip-prepare "$TMP"
ls "$TMP/_ask" "$TMP/AGENTS.md" "$TMP/ask"
```

---

## References

| Thing | Path |
| --- | --- |
| Agent checklist | `AGENTS.md` |
| `record-run` | `_ask/scripts/record-run.sh` |
| Trainer / viewer | `scripts/train_moons.py`, `scripts/view_runs.py` |
| Results | `results/README.md` |
| This workstream | `work/demo-nn-train/` |
