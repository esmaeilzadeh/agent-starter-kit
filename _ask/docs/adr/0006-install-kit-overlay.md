# install-kit.sh overlays without touching consumer docs/

Template clone remains primary. Optional overlay (`./ask install`, implementation `install-kit.sh`) copies the kit package (`_ask/`, including kit scripts) plus `.agents/ask/`, complete `.cursor/`, merge-safe `AGENTS.md`, and root `ask`. It never touches consumer `docs/`, `scripts/`, `tests/`, or app `src/` by default. By default it runs prepare + sync (`--skip-prepare` for air-gap). Conflicts refuse unless `--force`; `--dry-run` supported; no interactive prompts on the agent path.
