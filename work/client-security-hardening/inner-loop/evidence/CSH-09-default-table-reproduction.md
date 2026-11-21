# Existing default-table defect at CSH-09 entry

Route: existing-contract bug prerequisite within the shared model decision helper consumed by the orchestrator gate. CSH-009 requires confirming the displayed complete resolved table without silently changing defaults. CSH-09 owns model-decisions.py; repair is serialized before handoff integration and changes no accepted criterion.

Reproduction run on ead0e1d using the real helper in a disposable ClientTests fixture: write only `risk: HIGH` to .agents/ask.local/bindings/models.yaml, show the decision, then submit {runtime: codex, submission: confirm, implementation_policy: latest-accessible} with no work risk or override.

Observed show: reported risk LOW, Review gpt-6-astra.
Observed submit: reported risk LOW, Review gpt-6-luna.
Thus confirmation changed the displayed inherited default. Expected effective risk uses explicit decision, work, project, environment, default precedence, and save/show/resolve agree. Reproduced before regression or source changes.
