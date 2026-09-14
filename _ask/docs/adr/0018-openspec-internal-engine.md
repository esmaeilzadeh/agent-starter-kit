# OpenSpec as a pinned internal engine; `openspec/` is consumer state

The kit uses `@fission-ai/openspec` revision `1.13.0` (pin: `_ask/openspec-pin.yaml`; never `latest`). Gated commands fail closed on a missing executable or version mismatch for a marked pilot (`Engine: openspec` in `work/<id>/intent.md`). `install-kit.sh` does not require Node or OpenSpec. Human-only `./ask setup` installs that pin under `$HOME/.local` when Node/npm are present, and warns and continues when they are not.

`openspec/` sits at repo root as consumer-owned engineering state, same class as `specs/` and `work/` in ADR-0011: upgrade must not rewrite it. Kit code stays under `_ask/` (helper `_ask/scripts/openspec_cli.py`, command `./ask openspec-archive`). Default setup (`openspec init --tools none --no-animation --profile core` on 1.13.0) must leave no OpenSpec-generated command or skill files; kit `./ask` remains the promoted surface.

Agents must not follow the CLI's `npm install … @latest` advice. Schema `spec-driven` and profile `core` are recorded in the pin; `openspec config` is global-only on 1.13.0.

## Related

- ADR-0011 kit namespaced / no collision
- `specs/current` pointer: `openspec/changes/openspec-governance-integration/`
