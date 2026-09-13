# Intent: humanizer on human-facing docs only

Explore skipped: destination already clear.

## What

Fail-closed apply-scope for prose skills:

1. **Human-facing** Markdown is the only set that goes through `humanizer` (`blader/humanizer` @ `v3.0.0`): root `README.md`, `_ask/guide/`, `_ask/docs/demo/`.
2. **Machine-first** Markdown goes through `writing-for-agents` (`mattpocock/skills` @ `v1.2.3`) and does not go through `humanizer`. That set is every spec and every agent-consumed `.md` (stage contracts, policies, templates, `AGENTS.md`, `CONTEXT.md`, `work/` artifacts, `_ask/spec/`, `_ask/docs/adr/`, generated `.cursor` projections of those sources).
3. Pin `writing-for-agents` in `_ask/skills/manifest.yaml` (`role: agent-docs`, `required: true`). Keep the `humanizer` pin.

## Why

`humanizer` rewrites for human voice. On a spec or stage contract that costs `must` / `must not` precision and makes the file worse for the agent that executes it. Machine-first files need a method that keeps process language checkable. Human-facing files still need `humanizer`.

## Non-goals

- Rewriting existing spec, Guide, ADR, or README prose in this workstream
- Vendoring skill trees
- `revision: latest`
- Dropping the `humanizer` pin
- Changing code, commands, paths, YAML metadata, or link targets for voice

## Known assumptions

- Default for any `.md` not in the human-facing set is machine-first (`writing-for-agents`, no `humanizer`).
- Generated `.cursor/skills` and `.cursor/commands` follow their `_ask/agents/` source.
- This is a spec-change on `specs/current/pin-humanizer.md` (ADR 0017). The workstream spec is `specs/current/humanizer-human-docs-only.md`.
- `stage-model-subagents` stays on its own accepted history on `main`; this branch starts from current `main`.

## Open questions

None.

## Human decisions

- **Q1-A:** Fail-closed. Humanizer runs only on the explicit human-facing set.
- **writing-for-agents:** Pin and apply on all specs and agent docs.
- **Q2-B:** New workstream now (`humanizer-human-docs-only`). Pause further labor on `agent/stage-model-subagents`.
- **Q3-A:** Humanizer set is README, `_ask/guide/`, `_ask/docs/demo/`. ADRs stay machine-first.
- **go till end:** defaults OK. Later artifacts proceed without re-bless until Accept.
