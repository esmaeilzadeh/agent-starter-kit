# AI Engineering Starter Kit

Portable repository protocol for delegating engineering labor to AI agents while keeping **human ownership** of intent, policy, and acceptance. Cursor is the first-class runtime binding; the protocol stays copyable into ordinary software repos.

This is **not** a multi-agent runtime product. It is Guide + Build Spec + stage contracts + small scripts + pinned Community Skills.

## Start here

| Step | Action |
| --- | --- |
| 1 | Read **[AGENTS.md](AGENTS.md)** — short operational checklist every agent must follow |
| 2 | Skim **[_ask/README.md](_ask/README.md)** — where the kit lives |
| 3 | Run the facilitator demo **[_ask/docs/demo/end-to-end-plan.md](_ask/docs/demo/end-to-end-plan.md)** |
| 4 | Open **[CONTEXT.md](CONTEXT.md)** — domain vocabulary for this kit |

```bash
./ask check-clean
./ask sync
# optional (needs network / skills CLI):
./ask prepare
```

## How a product uses this kit

Put `askit` on your PATH (once per machine):

```bash
curl -fsSL https://raw.githubusercontent.com/esmaeilzadeh/agent-starter-kit/main/askit | bash
```

Then in **your** app git repo:

```bash
cd /path/to/your/app
askit
```

If the folder is not a git repo, askit refuses. If it is git but not ask-based (no `_ask/` and `./ask`), it asks whether to add ask capability — it does not overlay silently, and it does not list kit commands until you confirm. After that, `askit` is the same as `./ask`. `askit setup` is the tracker/MCP wizard on an already ask-based repo.

The overlay does not touch `docs/`, `scripts/`, `tests/`, or `src/`.

You can still overlay from a kit clone: `./ask install /path/to/your/app`.

| Layer | Paths |
| --- | --- |
| Kit package | `_ask/` (protocol, scripts, kit tests, kit-author docs) |
| Adapter | `ask`, `AGENTS.md`, `.cursor/` |
| Product state | `specs/`, `work/` (created by start-work) |
| Product code/docs | everything else |

## What you get

- **Explore (`00`)** when the destination is foggy — durable `work/<work-id>/explore-map.md`
- **Engineering Pipeline (`01`–`10`)** — Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept
- **Pinned Community Skills** via `_ask/skills/manifest.yaml` + `./ask prepare` ([skills.sh](https://www.skills.sh/))
- **Thin Cursor Binding** — rules *point* at protocol; generated projections under `.cursor/`
- **`/off-path`** — Cursor command: leave the kit path for **this chat only**; a new chat starts on-path
- **Git guardrails** — `_ask/policies/worktree.md`

## Repository map

```text
README.md                 ← human entry
AGENTS.md                 ← agent entry
ask                       ← Agent Starter Kit command (not scripts/)
CONTEXT.md                ← glossary
_ask/         ← entire kit (guide, spec, agents, policies,
                            templates, skills, scripts, tests, docs)
specs/                    ← product / workstream specifications
work/                     ← per-work-id artifacts
.cursor/                  ← Cursor-honored projections
```

Guide and Build Spec modules live under `_ask/guide/` and `_ask/spec/`. Root monolith filenames are stubs.

## Quick commands

`askit` is the PATH installer and daily command. In a repo that already has the kit, `./ask` is the same dispatcher. Both exec `_ask/scripts/` (and `prepare` → `skills/prepare-skills.sh`). Run `./ask` or `./ask --help` for commands and flags. Tab completion: run `askit` once (installs a `~/.bashrc` / `~/.zshrc` hook and bash-completion files). No `eval`. `sta<Tab>` matches both `start-work` and `status`; type `start<Tab>` for `start-work`.

| Command | Purpose |
| --- | --- |
| `./ask check-clean` | Refuse dirty trees |
| `./ask start-work <work-id>` | Branch `agent/<work-id>` + seed `work/<work-id>/` |
| `./ask check-workstream <work-id>` | Preconditions before implement |
| `./ask status` | Live `agent/*` + archived `work/*` on default (no checkout); later cards from `.later/` on this checkout |
| `./ask verify` | Run checks; print commit SHA |
| `./ask record-result …` | Workstream provenance (requires `--commit-sha`) |
| `./ask record-run …` | Experiment provenance (SHA must be `HEAD`) |
| `./ask sync` | Regenerate `.cursor` projections |
| `./ask install <repo>` | Overlay kit package + adapter only |
| `./ask upgrade --version <tag>` | Refresh kit-owned files |
| `./ask prepare` | Install pinned Community Skills |
| `./ask setup` | **Human-only** tracker + MCP wizard (TTY required; agents must not run it). Installs the pinned OpenSpec CLI under `~/.local` when `node`/`npm` are on PATH. |
| `./ask completion bash\|zsh` | Print tab-completion snippet (debug; `askit` installs this) |

## Documentation index

- **Demo:** [_ask/docs/demo/end-to-end-plan.md](_ask/docs/demo/end-to-end-plan.md)
- **Guide:** [_ask/guide/README.md](_ask/guide/README.md)
- **Build Spec:** [_ask/spec/README.md](_ask/spec/README.md)
- **Guide ↔ Spec map:** [_ask/MAPPING.md](_ask/MAPPING.md)
- **Owned paths / upgrades:** [_ask/OWNED-PATHS.md](_ask/OWNED-PATHS.md)
- **ADRs:** [_ask/docs/adr/](_ask/docs/adr/)
- **Issue tracker (this kit repo):** [_ask/docs/agents/issue-tracker.md](_ask/docs/agents/issue-tracker.md)

## Design stance

Human keeps **Judgment** and **Authority**. Agents supply **Labor** and **Capability** under explicit **Policy**. Evidence comes from verification and Git history.

Phases **1–2** of the Build Spec are what this repository ships.
