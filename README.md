# AI Engineering Starter Kit

Portable repository protocol for delegating engineering labor to AI agents while keeping **human ownership** of intent, policy, and acceptance. Cursor is the first-class runtime binding; the protocol stays copyable into ordinary software repos.

This is **not** a multi-agent runtime product. It is Guide + Build Spec + stage contracts + small scripts + pinned Community Skills.

## Start here

| Step | Action |
| --- | --- |
| 1 | Read **[AGENTS.md](AGENTS.md)** — short operational checklist every agent must follow |
| 2 | Skim **[part-engineering/README.md](part-engineering/README.md)** — where protocol, Guide, Spec, and policies live |
| 3 | Run the facilitator demo **[docs/demo/end-to-end-plan.md](docs/demo/end-to-end-plan.md)** — Grill→Accept (optional Explore) on a tiny `kit-status` feature |
| 4 | Open **[CONTEXT.md](CONTEXT.md)** — domain vocabulary for this kit |

```bash
./scripts/check-clean-worktree.sh
./scripts/sync-cursor-binding.sh
# optional (needs network / skills CLI):
./part-engineering/skills/prepare-skills.sh
```

## What you get

- **Explore (`00`)** when the destination is foggy — durable `work/<work-id>/explore-map.md`, then hand off to Intent
- **Engineering Pipeline (`01`–`10`)** — Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept (Spec Change as interrupt)
- **Pinned Community Skills** via `part-engineering/skills/manifest.yaml` + `prepare-skills.sh` (not vendored skill trees; discovery starts at [skills.sh](https://www.skills.sh/))
- **Thin Cursor Binding** — `AGENTS.md`, `.cursor/hooks`, rules that *point* at protocol, generated stage projections under `.cursor/`
- **Git guardrails** — clean tree, one plan per `agent/<work-id>` branch, commit each meaningful step (`part-engineering/policies/worktree.md`)

## Repository map

```text
README.md                 ← you are here (human entry)
AGENTS.md                 ← agent entry (short checklist)
CONTEXT.md                ← glossary / domain language
part-engineering/         ← kit protocol root (Guide, Spec, agents, policies, templates, skills)
docs/
  demo/                   ← end-to-end facilitator script
  adr/                    ← architecture decision records
  agents/                 ← tracker / triage / domain notes for this repo
  research/               ← research ticket outputs
specs/                    ← product/workstream specifications
work/                     ← per-work-id artifacts
scripts/                  ← check-clean, start-work, verify, install-kit, …
.cursor/                  ← Cursor-honored projections (generated + hooks/rules)
```

Guide and Build Spec are modular under `part-engineering/guide/` and `part-engineering/spec/`. The old monolith filenames at the repo root are **stubs** that point at those modules.

## Quick commands

| Command | Purpose |
| --- | --- |
| `scripts/check-clean-worktree.sh` | Refuse dirty trees |
| `scripts/start-work.sh <work-id>` | Branch `agent/<work-id>` + seed `work/<work-id>/` |
| `scripts/check-workstream.sh <work-id>` | Preconditions before implement |
| `scripts/verify.sh` | Run kit/project checks; print commit SHA |
| `scripts/record-result.sh …` | Provenance record (requires `--commit-sha`) |
| `scripts/sync-cursor-binding.sh` | Regenerate `.cursor` stage projections |
| `scripts/install-kit.sh <repo>` | Overlay kit into another git repo (never touches consumer `docs/` by default) |
| `part-engineering/skills/prepare-skills.sh` | Install pinned Community Skills |

## Documentation index

- **Demo (start→accept):** [docs/demo/end-to-end-plan.md](docs/demo/end-to-end-plan.md)
- **Guide (concepts):** [part-engineering/guide/README.md](part-engineering/guide/README.md)
- **Build Spec (implementation contract):** [part-engineering/spec/README.md](part-engineering/spec/README.md)
- **Guide ↔ Spec map:** [part-engineering/MAPPING.md](part-engineering/MAPPING.md)
- **Kit vs consumer paths / upgrades:** [part-engineering/OWNED-PATHS.md](part-engineering/OWNED-PATHS.md)
- **ADRs:** [docs/adr/](docs/adr/)
- **Issue tracker conventions (this repo):** [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)

## Design stance

Human keeps **Judgment** and **Authority**. Agents supply **Labor** and **Capability** under explicit **Policy**. Evidence comes from verification and Git history — not from “the model said it looked good.”

Phases **1–2** of the Build Spec are what this repository ships. Phase 3+ (richer workflow quality, CI, extra runtimes) is optional later work.
