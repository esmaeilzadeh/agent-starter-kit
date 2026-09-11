# Root `pek` dispatcher (not generic scripts/)

Humans and agents invoke kit scripts via a single root command named `pek` (Part Engineering Kit). Implementation stays under `part-engineering/scripts/` and `part-engineering/skills/`. The name is kit-specific so it does not collide with a product `scripts/` directory. `install-kit` / `upgrade-kit` copy and refresh `pek` as kit-owned adapter, alongside `AGENTS.md` and `.cursor/`.
