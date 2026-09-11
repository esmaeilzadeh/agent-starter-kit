# install-kit.sh overlays without touching consumer docs/

Template clone remains primary. Optional `install-kit.sh` overlays the kit package (`part-engineering/`, including kit scripts) plus complete `.cursor/` and merge-safe `AGENTS.md`. It never touches consumer `docs/`, `scripts/`, `tests/`, or app `src/` by default. By default it runs prepare-skills + sync-cursor-binding (`--skip-prepare` for air-gap). Conflicts refuse unless `--force`; `--dry-run` supported; no interactive prompts on the agent path.
