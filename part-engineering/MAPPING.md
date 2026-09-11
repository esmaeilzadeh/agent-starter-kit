# Guide ↔ Build Spec mapping

Index from Guide concepts to kit implementation paths. Prefer modular files under `part-engineering/`.

| Guide concept | Guide module | Kit implementation |
| --- | --- | --- |
| Explore / wayfinding / R&D on-ramp | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/00-explore.md`](agents/00-explore.md), `explore-map` template, Explore skills in manifest |
| What / Why | [02-workflow](guide/02-workflow.md) | [`work/<work-id>/intent.md`](../work/<work-id>/intent.md) |
| Intent Grilling | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/01-grill.md`](agents/01-grill.md) |
| OpenSpec / Specification | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/02-spec.md`](agents/02-spec.md), `specs/` |
| Specification Challenge | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/03-spec-challenge.md`](agents/03-spec-challenge.md) |
| Specification Change | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/04-spec-change.md`](agents/04-spec-change.md) |
| Planning | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/05-plan.md`](agents/05-plan.md) |
| Delegated implementation | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/06-implement.md`](agents/06-implement.md) |
| Structured review | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/07-review.md`](agents/07-review.md) |
| Delegated refactor | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/08-refactor.md`](agents/08-refactor.md) |
| Verification | [02-workflow](guide/02-workflow.md) | [`part-engineering/agents/09-verify.md`](agents/09-verify.md), [`part-engineering/scripts/verify.sh`](../part-engineering/scripts/verify.sh) |
| Acceptance | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/agents/10-accept.md`](agents/10-accept.md), `acceptance.md` |
| Guide (modular) | [guide/README](guide/README.md) | [`part-engineering/guide/`](guide/) |
| Build Spec (modular) | [spec/README](spec/README.md) | [`part-engineering/spec/`](spec/) |
| Delegation policy | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/policies/delegation.md`](policies/delegation.md) |
| Risk policy | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/policies/risk.md`](policies/risk.md) |
| Verification policy | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/policies/verification.md`](policies/verification.md) |
| Skill provenance + preparation | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/skills/manifest.yaml`](skills/manifest.yaml), `prepare-skills.sh` |
| Decision memory | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/decisions/`](decisions/) |
| Spec state | [guide/README](guide/README.md) | [`specs/current/`](../specs/current/), [`specs/proposals/`](../specs/proposals/), status field |
| Git hygiene | [guide/README](guide/README.md) | `check-clean-worktree.sh`, `start-work.sh`, `check-workstream.sh` |
| Cursor Binding sync | [guide/README](guide/README.md) | [`part-engineering/scripts/sync-cursor-binding.sh`](../part-engineering/scripts/sync-cursor-binding.sh), `.cursor/` |
| Install overlay | [guide/README](guide/README.md) | [`part-engineering/scripts/install-kit.sh`](../part-engineering/scripts/install-kit.sh) |
| Result provenance | [03-methods-governance](guide/03-methods-governance.md) | `record-result.sh`, result schema |
| Escalation | [guide/README](guide/README.md) | policy + workflow gates |
| Acceptance debt | [03-methods-governance](guide/03-methods-governance.md) | evidence/acceptance state records |
| Engineering-system evolution | [guide/README](guide/README.md) | review/verification outputs → rule/skill/check improvements |

See also [spec/06-phases-and-acceptance.md](spec/06-phases-and-acceptance.md) §38.
| Worktree / branch / commit discipline | [03-methods-governance](guide/03-methods-governance.md) | [`part-engineering/policies/worktree.md`](policies/worktree.md), [`part-engineering/scripts/check-clean-worktree.sh`](../part-engineering/scripts/check-clean-worktree.sh) |
