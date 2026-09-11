# Kit-owned vs consumer-owned paths

Version tags: use explicit kit releases as Git tags `vMAJOR.MINOR.PATCH` (or annotated tags pointing at a release commit). `upgrade-kit.sh` refreshes from an explicit `--version <tag-or-sha>` — never blind `main`.

## Kit-owned (safe to refresh on upgrade)

- `part-engineering/guide/` modules
- `part-engineering/spec/` modules
- `part-engineering/agents/*.md` **except** `*.local.md`
- `part-engineering/templates/`
- Stock `part-engineering/policies/*.md` when the consumer has not replaced the policy tree
- Stock `scripts/*.sh`
- Generated `.cursor/` projections (skills/commands/hooks wrappers produced by sync)
- Monolith stubs (`ai-agent-engineering-guide.md`, `ai-agent-starter-kit-spec.md`)

## Consumer-owned (never clobber by default)

- `part-engineering/skills/manifest.yaml`
- Policies when customized (or a local policy overlay tree)
- Local sections of root `AGENTS.md`
- `.cursor/rules/local/`
- `part-engineering/agents/*.local.md` (per-stage overlays merged at sync time)
- Product `docs/`, `src/`, and unrelated application specs
- Prepared `.agents/skills/` bodies (regenerated; gitignored)

## Related

- ADR-0009 kit upgrade and overrides
- `scripts/upgrade-kit.sh` (ticket 28)
- `scripts/sync-cursor-binding.sh` merges `*.local.md` (ticket 29)
