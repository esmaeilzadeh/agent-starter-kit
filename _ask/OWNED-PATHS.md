# Kit-owned vs consumer-owned paths

Version tags: use explicit kit releases as Git tags `vMAJOR.MINOR.PATCH` (or annotated tags pointing at a release commit). `./ask upgrade --version <tag-or-sha>` refreshes from an explicit version — never blind `main`.

## Kit-owned (safe to refresh on upgrade)

- `_ask/guide/` modules
- `_ask/spec/` modules
- `_ask/agents/*.md` **except** `*.local.md`
- `_ask/templates/`
- Stock `_ask/policies/*.md` when the consumer has not replaced the policy tree
- `_ask/scripts/*.sh`
- `_ask/tests/`
- `_ask/docs/` (kit-author ADRs, demo, research)
- Generated `.cursor/` projections (skills/commands/hooks wrappers produced by sync)
- Root `ask` dispatcher
- Monolith stubs (`ai-agent-engineering-guide.md`, `ai-agent-starter-kit-spec.md`)

## Consumer-owned (never clobber by default)

- `_ask/skills/manifest.yaml`
- Policies when customized (or a local policy overlay tree)
- Local sections of root `AGENTS.md`
- `.cursor/rules/local/`
- `_ask/agents/*.local.md` (per-stage overlays merged at sync time)
- Product `docs/`, `scripts/`, `tests/`, `src/`
- Product `specs/`, `work/` (engineering state)
- Prepared `.agents/skills/` bodies (regenerated; gitignored)

## Related

- ADR-0011 kit namespaced / no collision
- ADR-0012 root `ask` dispatcher
- ADR-0009 kit upgrade and overrides
- `./ask upgrade` / `./ask sync` (scripts remain under `_ask/scripts/`)
