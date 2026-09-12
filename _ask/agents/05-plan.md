# Kit Protocol: 05 Plan

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Output: `work/<work-id>/plan.md` (template `_ask/templates/plan.md`).

## 15.5 05 Plan Agent

Purpose:

```text
Derive the implementation plan from an accepted specification.
```

Must:

```text
reference exactly one accepted spec
identify affected components
identify dependencies
identify verification steps
identify escalation points
identify possible spec-change triggers
```

Must not redefine the requirement.

---

## Kit emphasis

- Planning assumes a clean worktree and a dedicated `agent/<work-id>` branch (create via `./ask start-work <work-id>` if not already on one).
- The resulting plan must be executed with **one branch only** for that work-id; do not spawn parallel related branches that touch the same files.
- Execution of the plan (Implement onward) must **commit after each meaningful step**, not only at the end — see `_ask/policies/worktree.md`.
