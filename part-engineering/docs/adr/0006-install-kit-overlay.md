# install-kit.sh overlays without touching consumer docs/

Template clone remains primary. Optional `install-kit.sh` overlays kit-owned paths (`part-engineering/`, kit scripts including prepare + sync-cursor-binding, complete `.cursor/` projection, merge-safe `AGENTS.md`) into an existing git repo. It never touches consumer `docs/` or app `src/` by default. By default it runs prepare-skills + sync-cursor-binding (`--skip-prepare` for air-gap). Conflicts refuse unless `--force`; `--dry-run` supported; no interactive prompts on the agent path.
