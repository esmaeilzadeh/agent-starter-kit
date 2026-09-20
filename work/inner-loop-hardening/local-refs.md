# Local reference clones (not in this git)

Do not WebFetch these while the clone exists. They are **read-only
comparisons**. Do not vendor them into ASK.

| Project | Path | Use |
| --- | --- | --- |
| cc-sdd | `/home/mohamad/Projects/UNI/cc-sdd` | Inner-loop borrow: steering, `_Boundary:_`, sequential kiro-impl |

cc-sdd files that matter for this workstream:

- Steering rules: `tools/cc-sdd/templates/shared/settings/rules/steering-principles.md`
- Cursor kiro-impl: `tools/cc-sdd/templates/agents/cursor-skills/skills/kiro-impl/SKILL.md`
- Reviewer boundary check: `.../kiro-impl/templates/reviewer-prompt.md`

Steering is project memory (patterns, not file lists). kiro-impl is one writer
per iteration; `(P)` is not concurrent Git.
