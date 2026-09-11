# Kit lives only under part-engineering/ (no generic-name collision)

The kit package is `part-engineering/` only: protocol, Guide/Spec, agents, policies, templates, skills, **kit scripts**, **kit self-tests**, and **kit-author docs**.

Root adapter: `pek` (Part Engineering Kit dispatcher; ADR-0012), `AGENTS.md`, `.cursor/`.

Product owns `docs/`, `scripts/`, `tests/`, `src/`, and all other generic names. `install-kit` / `upgrade-kit` never overlay those.

`specs/` and `work/` remain at repo root as **product engineering state** (kit convention, created by `start-work`), not kit code — not nested under `part-engineering/` so upgrades do not rewrite product history.

Rejected: wrapping the app in an outer kit directory; a multi-project factory.
