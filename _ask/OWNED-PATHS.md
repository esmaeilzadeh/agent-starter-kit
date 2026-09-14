# Kit-owned vs consumer-owned paths

Version tags: use explicit kit releases as Git tags `vMAJOR.MINOR.PATCH` (or annotated tags pointing at a release commit). `./ask upgrade --version <tag-or-sha>` refreshes from an explicit version — never blind `main`.

## Kit-owned (safe to refresh on upgrade)

- `_ask/guide/` modules
- `_ask/spec/` modules
- `_ask/agents/*.md` **except** `*.local.md`
- `_ask/templates/`
- Stock `_ask/policies/*.md` when the consumer has not replaced the policy tree
- `_ask/scripts/*.sh` and `_ask/scripts/*.py`
- `_ask/openspec-pin.yaml`
- `_ask/tests/`
- `_ask/docs/` (kit-author ADRs, demo, research)
- `_ask/cursor-commands/` (session-mode Cursor commands; `./ask sync` copies into `.cursor/commands/`)
- `_ask/bindings/` **except** consumer `models.yaml` (portable defaults, runtime slug tables, templates)
- Generated `.cursor/` projections (skills/commands/hooks wrappers and `.cursor/agents` produced by sync)
- Generated `.claude/agents/` and `.codex/agents/` (from `./ask sync`)
- Stock kit Cursor rules under `.cursor/rules/` **except** `.cursor/rules/local/` (e.g. bootstrap, commit-step-discipline)
- Root `ask` dispatcher
- Monolith stubs (`ai-agent-engineering-guide.md`, `ai-agent-starter-kit-spec.md`)

## Consumer-owned (never clobber by default)

- `_ask/skills/manifest.yaml`
- Policies when customized (or a local policy overlay tree)
- Local sections of root `AGENTS.md`
- `.cursor/rules/local/`
- `_ask/agents/*.local.md` (per-stage overlays merged at sync time)
- `_ask/bindings/models.yaml` (optional consumer model overlay)
- Product `docs/`, `scripts/`, `tests/`, `src/`
- Product `specs/`, `work/`, `openspec/` (engineering state)
- Prepared `.agents/skills/` bodies (regenerated; gitignored)

## Related

- ADR-0011 kit namespaced / no collision
- ADR-0012 root `ask` dispatcher
- ADR-0009 kit upgrade and overrides
- ADR-0018 OpenSpec pin and consumer-owned `openspec/`
- `./ask upgrade` / `./ask sync` (scripts remain under `_ask/scripts/`)
