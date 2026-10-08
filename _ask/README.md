# _ask

Portable protocol root for the AI Engineering Starter Kit. Branded on purpose — not a generic `engineering/` docs folder — so the kit stays recognizable inside consuming repos.

Root `AGENTS.md` is the short operational entrypoint. This tree holds the durable contracts.

## What’s here

| Path | Role |
| --- | --- |
| `guide/` | Modular Guide (Division of Engineering Labor concepts) |
| `spec/` | Modular Build Spec (implementation contract; name-stable with Guide) |
| `agents/` | Pointers to `.agents/ask/stages/` (`00-explore.md` … `10-accept.md`) |
| `bindings/` | Pointers to `.agents/ask/bindings/` |
| `policies/` | Delegation, risk, verification, worktree, workflow, Git-flow |
| `skills/` | Skill Manifest (`manifest.yaml`) + `prepare-skills.sh` |
| `scripts/` | Kit guardrails (clean tree, start-work, verify, install, upgrade) |
| `tests/` | Tests of the kit, not of the product |
| `docs/` | Kit-author ADRs, demo, research |
| `templates/` | Workstream templates (explore-map, intent, spec, plan, …) |
| `decisions/` | Optional kit-level decision records |

## Sibling roots (the product)

```text
_ask/   # this kit package
ask AGENTS.md .cursor/  # thin adapter (ask = Agent Starter Kit CLI)
.agents/ask/        # stage/binding/verification SoT
specs/ work/        # product engineering state
docs/ scripts/ …    # product-owned (kit never overlays these names)
.agents/skills/     # prepared Community Skill bodies (gitignored)
```

## Skills

Community Skills are pinned in `skills/manifest.yaml` and prepared into `.agents/skills/` — not copied into the kit as a vendored tree. See the Build Spec skill-manifest section once `spec/` modules are split.

## Start here

1. Read root `AGENTS.md`
2. Invoke kit operations via `./ask` (not a generic `scripts/` folder)
3. If foggy → `.agents/ask/stages/00-explore.md` + `templates/explore-map.md`
4. Else → pipeline from `.agents/ask/stages/01-grill.md` onward with relevant `policies/`
5. Facilitator demo (start→accept): [`docs/demo/end-to-end-plan.md`](docs/demo/end-to-end-plan.md)

## Guide ↔ Spec map

See [MAPPING.md](MAPPING.md) for Explore and pipeline stage mapping.
