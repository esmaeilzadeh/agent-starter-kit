# Guide ↔ Build Spec mapping

Index from Guide concepts to kit implementation paths. Prefer modular files under `_ask/`. Humans and agents invoke kit operations via `./ask` (implementation under `_ask/scripts/` and `skills/prepare-skills.sh`).

| Guide concept | Guide module | Kit implementation |
| --- | --- | --- |
| Explore / wayfinding / R&D on-ramp | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/00-explore.md`](../.agents/ask/stages/00-explore.md), `explore-map` template, Explore skills in manifest |
| What / Why | [02-workflow](guide/02-workflow.md) | [`work/<work-id>/intent.md`](../work/<work-id>/intent.md) |
| Intent Grilling | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/01-grill.md`](../.agents/ask/stages/01-grill.md), ADR 0016 (load-bearing + ask-before-prepare) |
| OpenSpec / Specification | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/02-spec.md`](../.agents/ask/stages/02-spec.md), `specs/` |
| Specification Challenge | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/03-spec-challenge.md`](../.agents/ask/stages/03-spec-challenge.md) |
| Specification Change | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/04-spec-change.md`](../.agents/ask/stages/04-spec-change.md) |
| Planning | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/05-plan.md`](../.agents/ask/stages/05-plan.md) |
| Delegated implementation | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/06-implement.md`](../.agents/ask/stages/06-implement.md) |
| Structured review | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/07-review.md`](../.agents/ask/stages/07-review.md) |
| Delegated refactor | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/08-refactor.md`](../.agents/ask/stages/08-refactor.md) |
| Verification | [02-workflow](guide/02-workflow.md) | [`.agents/ask/stages/09-verify.md`](../.agents/ask/stages/09-verify.md), `./ask verify` |
| Acceptance | [03-methods-governance](guide/03-methods-governance.md) | [`.agents/ask/stages/10-accept.md`](../.agents/ask/stages/10-accept.md), `acceptance.md` |
| Guide (modular) | [guide/README](guide/README.md) | [`_ask/guide/`](guide/) |
| Build Spec (modular) | [spec/README](spec/README.md) | [`_ask/spec/`](spec/) |
| Delegation policy | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/policies/delegation.md`](policies/delegation.md) |
| Workflow guidance (not a lock) | [02-workflow](guide/02-workflow.md) | [`_ask/policies/workflow.md`](policies/workflow.md), `./ask status` warnings |
| Session-only off-path | [02-workflow](guide/02-workflow.md) | [`_ask/cursor-commands/off-path.md`](cursor-commands/off-path.md), `./ask sync` |
| Later inbox | [02-workflow](guide/02-workflow.md) | `.later/`, [`_ask/templates/later-work.md`](templates/later-work.md) |
| Risk policy | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/policies/risk.md`](policies/risk.md) |
| Verification policy | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/policies/verification.md`](policies/verification.md) |
| Skill provenance + preparation | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/skills/manifest.yaml`](skills/manifest.yaml), `./ask prepare` |
| Humanizer on human-facing docs; writing-for-agents on machine-first files | [03-methods-governance](guide/03-methods-governance.md) | manifest `humanizer` + `writing-for-agents` pins, [`.cursor/rules/humanizer-docs-specs.mdc`](../.cursor/rules/humanizer-docs-specs.mdc), [`.cursor/rules/writing-for-agents-machine-docs.mdc`](../.cursor/rules/writing-for-agents-machine-docs.mdc), ADR 0017 |
| Decision memory | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/decisions/`](decisions/) |
| Spec state | [guide/README](guide/README.md) | [`specs/current/`](../specs/current/), [`specs/proposals/`](../specs/proposals/), status field |
| Git hygiene | [guide/README](guide/README.md) | `./ask check-clean`, `./ask start-work`, `./ask check-workstream`, `./ask status` |
| Cursor Binding sync | [guide/README](guide/README.md) | `./ask sync` (reads `.agents/ask/`), `.cursor/` |
| Install overlay | [guide/README](guide/README.md) | `./ask install` |
| Human-only tracker/MCP setup | [guide/README](guide/README.md) | `./ask setup`, `.ask.env.example` |
| Result provenance | [03-methods-governance](guide/03-methods-governance.md) | `./ask record-result`, result schema |
| Experiment run provenance | [03-methods-governance](guide/03-methods-governance.md) | `./ask record-run`, `results/<run-id>/` |
| Escalation | [guide/README](guide/README.md) | policy + workflow gates |
| Acceptance debt | [03-methods-governance](guide/03-methods-governance.md) | evidence/acceptance state records |
| Engineering-system evolution | [guide/README](guide/README.md) | review/verification outputs → rule/skill/check improvements |
| Worktree / branch / commit discipline | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/policies/worktree.md`](policies/worktree.md), `./ask check-clean` |
| Git-flow | [03-methods-governance](guide/03-methods-governance.md) | [`_ask/policies/git-flow.md`](policies/git-flow.md), `./ask start-work` from `develop` |

See also [spec/06-phases-and-acceptance.md](spec/06-phases-and-acceptance.md) §38.
