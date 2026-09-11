# Skill Manifest + prepare-skills contract (v1)

Manifest entries use `source`, required `revision` (never `latest`), `skill`, `role`, and optional `required`. Preparation runs manifest-driven `npx skills add source#revision --skill name --agent cursor --yes`, verifies `SKILL.md`, and fails closed on required entries. Commit `skills-lock.json`; gitignore `.agents/skills/`. Cloud/CI must run prepare before agent work; optional `--vendor`/`--copy`+commit is a documented escape hatch, not the default. Symlink install by default; `--copy` when symlinks break; never `-g` for kit prepare.
