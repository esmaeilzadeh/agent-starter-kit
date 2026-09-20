# Kit-owned vs consumer-owned paths

Version tags: use explicit kit releases as Git tags `vMAJOR.MINOR.PATCH` (or annotated tags pointing at a release commit). `./ask upgrade --version <tag-or-sha>` refreshes from an explicit version — never blind `main`.

## Kit-owned (safe to refresh on upgrade)

- `.agents/ask/` (stages, bindings, verification presets)
- `_ask/agents/*.md` pointers **except** `*.local.md`
- `_ask/guide/` modules
- `_ask/spec/` modules
- `_ask/templates/`
- Stock `_ask/policies/*.md` when the consumer has not replaced the policy tree
- `_ask/scripts/*.sh`
- `_ask/tests/`
- `_ask/docs/` (kit-author ADRs, demo, research)
- `_ask/cursor-commands/` (session-mode Cursor commands; `./ask sync` copies into `.cursor/commands/`)
- `_ask/bindings/` pointers **except** consumer `models.yaml`
- Generated `.cursor/` projections (skills/commands/hooks wrappers and `.cursor/agents` produced by sync)
- Generated `.claude/agents/`, `.codex/agents/`, and `.opencode/agents/` (from `./ask sync`)
- Stock kit Cursor rules under `.cursor/rules/` **except** `.cursor/rules/local/` (e.g. bootstrap, commit-step-discipline)
- Root `ask` dispatcher
- Monolith stubs (`ai-agent-engineering-guide.md`, `ai-agent-starter-kit-spec.md`)

## Consumer-owned (never clobber by default)

- `_ask/skills/manifest.yaml`
- Policies when customized (or a local policy overlay tree)
- Local sections of root `AGENTS.md`
- `.cursor/rules/local/`
- `.agents/ask.local/` (per-stage and binding overlays merged at sync time)
- `_ask/agents/*.local.md` (legacy overlay path still merged if ask.local file is absent)
- `_ask/bindings/models.yaml` (optional consumer model overlay)
- `.agents/verification.yaml` (committed CheckPlan; scaffold/upgrade leave it)
- Product `docs/`, `scripts/`, `tests/`, `src/`
- Product `specs/`, `work/` (engineering state)
- Prepared `.agents/skills/` bodies (regenerated; gitignored)

## Related

- ADR-0011 kit namespaced / no collision
- ADR-0012 root `ask` dispatcher
- ADR-0009 kit upgrade and overrides
- `./ask upgrade` / `./ask sync` (scripts remain under `_ask/scripts/`)
