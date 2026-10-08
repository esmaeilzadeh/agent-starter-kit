# Context-engineering audit

Workstream: `codex-model-refresh`
Reviewed candidate: `0f937ac90bfbdc49dcbfdfb36871202d4ba87b34`
Scope: accepted specification, Codex runtime binding, generated agents, sync regression, and routing guidance.

| ID | Check | Status | Evidence |
| --- | --- | --- | --- |
| CE-01 | Instruction hierarchy and protocol source of truth | pass | Repository `AGENTS.md` names `.agents/ask/` as protocol source of truth and directs policy reads. The review used the accepted workstream contract and current spec as the criteria authority. |
| CE-02 | Context pointers identify the right source and trigger | pass | The Codex binding points to `_ask/docs/codex-model-routing.md` for selection rationale and override examples. The guide names the source binding, portable stage map, generator, and existing `work/<id>/models.yaml` override mechanism. |
| CE-03 | Load-bearing Grill and challenge decisions remain expanded | pass | The accepted spec records the user’s budget/fit clarification, exact role and pool assignments, risk/complexity distinction, boundaries, and observable criteria. The accepted challenge artifact examines ambiguities and failure cases; this implementation review checks those details against the diff. |
| CE-04 | Changed stage contracts remain accurate and reachable | pass | No canonical stage instructions or portable stage-to-role mappings changed. Generated agents alter only their model field; all eleven stage outputs were checked against the current role assignments. |
| CE-05 | Clean-worktree and one-workstream boundaries are respected | pass | Review began with a clean `agent/codex-model-refresh` worktree. No implementation or unrelated path was changed; the existing sync regression completed and restored generated defaults. No commit was made by the reviewer. |
| CE-06 | Canonical bindings, generated projections, and verification pointers align | pass | Codex source pins and all eleven generated Codex model fields agree. The existing sync regression passes default, HIGH-risk, and explicit role-override checks. Other runtime sources and generated outputs have no delta. |

Open IDs: none. This audit and review describe the pre-final candidate above. The runtime review-input record must be refreshed against the parent-provided final candidate SHA after these source artifacts are committed.
