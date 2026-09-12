# Workflow is guidance, not a lock

The default path (Explore → … → Accept) is how the kit guides engineering labor. It must not trap the human in per-stage ceremony, and it must not let “on the kit” mean empty artifacts.

**On the path:** prepare each stage document. Skip extra *approvals* after one “defaults are OK”; **Accept** is the second confirm. Missing spec/plan → prepare from those defaults, do not jump to code.

**Off the path:** only when the human explicitly leaves (“just code”). Warn once and follow.

**Still hard:** dirty tree, silent stash/reset, fake verify/accept, silent What/Why change.

`./ask check-workstream` exiting non-zero means default path incomplete, not forbidden. Policy: `_ask/policies/workflow.md`.
