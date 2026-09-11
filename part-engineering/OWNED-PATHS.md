# Kit-owned vs consumer-owned paths

Version tags: use explicit kit releases as Git tags `vMAJOR.MINOR.PATCH` (or annotated tags pointing at a release commit). `./pek upgrade --version <tag-or-sha>` refreshes from an explicit version — never blind `main`.

## Kit-owned (safe to refresh on upgrade)

- `part-engineering/guide/` modules
- `part-engineering/spec/` modules
- `part-engineering/agents/*.md` **except** `*.local.md`
- `part-engineering/templates/`
- Stock `part-engineering/policies/*.md` when the consumer has not replaced the policy tree
- `part-engineering/scripts/*.sh`
- `part-engineering/tests/`
- `part-engineering/docs/` (kit-author ADRs, demo, research)
- Generated `.cursor/` projections (skills/commands/hooks wrappers produced by sync)
- Root `pek` dispatcher
- Monolith stubs (`ai-agent-engineering-guide.md`, `ai-agent-starter-kit-spec.md`)

## Consumer-owned (never clobber by default)

- `part-engineering/skills/manifest.yaml`
- Policies when customized (or a local policy overlay tree)
- Local sections of root `AGENTS.md`
- `.cursor/rules/local/`
- `part-engineering/agents/*.local.md` (per-stage overlays merged at sync time)
- Product `docs/`, `scripts/`, `tests/`, `src/`
- Product `specs/`, `work/` (engineering state)
- Prepared `.agents/skills/` bodies (regenerated; gitignored)

## Related

- ADR-0011 kit namespaced / no collision
- ADR-0012 root `pek` dispatcher
- ADR-0009 kit upgrade and overrides
- `./pek upgrade` / `./pek sync` (scripts remain under `part-engineering/scripts/`)
