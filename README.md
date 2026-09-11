# AI Engineering Starter Kit

Portable repository protocol for delegating engineering labor to AI agents while keeping **human ownership** of intent, policy, and acceptance. Cursor is the first-class runtime binding; the protocol stays copyable into ordinary software repos.

This is **not** a multi-agent runtime product. It is Guide + Build Spec + stage contracts + small scripts + pinned Community Skills.

## Start here

| Step | Action |
| --- | --- |
| 1 | Read **[AGENTS.md](AGENTS.md)** — short operational checklist every agent must follow |
| 2 | Skim **[part-engineering/README.md](part-engineering/README.md)** — where the kit lives |
| 3 | Run the facilitator demo **[part-engineering/docs/demo/end-to-end-plan.md](part-engineering/docs/demo/end-to-end-plan.md)** |
| 4 | Open **[CONTEXT.md](CONTEXT.md)** — domain vocabulary for this kit |

```bash
./pek check-clean
./pek sync
# optional (needs network / skills CLI):
./pek prepare
```

## How a product uses this kit

Clone or `install-kit` into **your** app repo. The kit occupies only `part-engineering/` plus a thin Cursor adapter. Your Nest (or other) `docs/`, `scripts/`, `tests/`, and `src/` stay yours.

| Layer | Paths |
| --- | --- |
| Kit package | `part-engineering/` (protocol, scripts, kit tests, kit-author docs) |
| Adapter | `pek`, `AGENTS.md`, `.cursor/` |
| Product state | `specs/`, `work/` (created by start-work) |
| Product code/docs | everything else |

## What you get

- **Explore (`00`)** when the destination is foggy — durable `work/<work-id>/explore-map.md`
- **Engineering Pipeline (`01`–`10`)** — Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept
- **Pinned Community Skills** via `part-engineering/skills/manifest.yaml` + `prepare-skills.sh` ([skills.sh](https://www.skills.sh/))
- **Thin Cursor Binding** — rules *point* at protocol; generated projections under `.cursor/`
- **Git guardrails** — `part-engineering/policies/worktree.md`

## Repository map

```text
README.md                 ← human entry
AGENTS.md                 ← agent entry
pek                       ← Part Engineering Kit command (not scripts/)
CONTEXT.md                ← glossary
part-engineering/         ← entire kit (guide, spec, agents, policies,
                            templates, skills, scripts, tests, docs)
specs/                    ← product / workstream specifications
work/                     ← per-work-id artifacts
.cursor/                  ← Cursor-honored projections
```

Guide and Build Spec modules live under `part-engineering/guide/` and `part-engineering/spec/`. Root monolith filenames are stubs.

## Quick commands

| Command | Purpose |
| --- | --- |
| `part-engineering/scripts/check-clean-worktree.sh` | Refuse dirty trees |
| `part-engineering/scripts/start-work.sh <work-id>` | Branch `agent/<work-id>` + seed `work/<work-id>/` |
| `part-engineering/scripts/check-workstream.sh <work-id>` | Preconditions before implement |
| `part-engineering/scripts/verify.sh` | Run checks; print commit SHA |
| `part-engineering/scripts/record-result.sh …` | Provenance (requires `--commit-sha`) |
| `part-engineering/scripts/sync-cursor-binding.sh` | Regenerate `.cursor` projections |
| `part-engineering/scripts/install-kit.sh <repo>` | Overlay kit package + adapter only |
| `part-engineering/skills/prepare-skills.sh` | Install pinned Community Skills |

## Documentation index

- **Demo:** [part-engineering/docs/demo/end-to-end-plan.md](part-engineering/docs/demo/end-to-end-plan.md)
- **Guide:** [part-engineering/guide/README.md](part-engineering/guide/README.md)
- **Build Spec:** [part-engineering/spec/README.md](part-engineering/spec/README.md)
- **Guide ↔ Spec map:** [part-engineering/MAPPING.md](part-engineering/MAPPING.md)
- **Owned paths / upgrades:** [part-engineering/OWNED-PATHS.md](part-engineering/OWNED-PATHS.md)
- **ADRs:** [part-engineering/docs/adr/](part-engineering/docs/adr/)
- **Issue tracker (this kit repo):** [part-engineering/docs/agents/issue-tracker.md](part-engineering/docs/agents/issue-tracker.md)

## Design stance

Human keeps **Judgment** and **Authority**. Agents supply **Labor** and **Capability** under explicit **Policy**. Evidence comes from verification and Git history.

Phases **1–2** of the Build Spec are what this repository ships.
