# Final candidate review: workflow-routing-and-authority

- Candidate: `d25ce7527181ca401a2576955f2ab53323eb8a06`
- Reviewed delta: `ed8e5ce3..d25ce752`, with the immediately preceding cache correction at `845d087f..ed8e5ce3` inspected as part of final review
- Frozen kit authority: `0e303265ceae1fbcdc9b2261bd922b003ab68924`
- Requested/resolved reviewer model: `gpt-6-luna`
- Self-reported backend identity: unavailable
- Runtime: Codex
- Parent model: GPT-6
- Verdict: **APPROVED**

## Findings

No findings.

## Review basis

The model-status cache now stores only stable commit facts: a present blob, a missing tree entry, or an unsafe tree entry. Git tree/cat-file read failures become `unreadable-blob`; `_model_status_fact` raises on those, so the LRU does not retain them, while `_model_status` preserves the existing current-refresh display fallback (`missing`). The regression exercises a transient error followed by success under the same key, and checks that a failed `ls-tree` is reported as unreadable.

Live status now comes from one fresh `for-each-ref --no-merged=<resolved-default-commit>` batch. The full refs listing remains separate and fresh for work-ID grouping and current-branch selection. Comparing full tip object IDs preserves the prior rule: a work branch is live exactly when its tip is not an ancestor of the resolved default commit; merged refs remain archived. A failed batch yields no unmerged tips, matching the prior fail-closed behavior where ancestry failures caused affected candidates to be skipped. The previous cached ancestry helper is removed, so refs or graph state are reconsidered each refresh.

The launcher validates arguments before execution, then invokes the installed Streamlit CLI entry function directly through one Python process. `main(prog_name="streamlit")` receives the same `run`, app path, and validated arguments via `python -c` argument placement. Import failure keeps the actionable install message and exit code 127. The test additions cover one interpreter invocation and the unavailable-module path; existing launch tests cover listener address and argument behavior. This removes the redundant version precheck while keeping the launcher’s validation behavior.

I inspected the exact delta and `git diff --check`; both were clean. I did not run tests or broad suites. Coordinator-supplied evidence reports six inventory cases and four client-workbench tests passing, with final CheckPlan and expanded-suite runs still pending. Those results are not represented here as independently executed, and this review does not make a workstream acceptance decision.
