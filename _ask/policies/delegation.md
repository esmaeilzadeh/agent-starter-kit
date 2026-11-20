# 16. Delegation policy

File:

```text
_ask/policies/delegation.md
```

The policy must define five things for each relevant task category:

```text
Allowed actions
Forbidden actions
Required evidence
Escalation conditions
Human approval conditions

Request each required confirmation as a question with selectable choices. Never ask the human to write or repeat a prescribed approval sentence. If the active runtime lacks choice controls, offer numbered choices and accept the number or option label. A preselected choice is not approval. For any selected option that authorizes a consequential action, act only within the exact option's stated scope.
```

Conservative default:

### Autonomous by default

```text
file creation/modification within assigned scope
routine refactoring
generated tests
routine review-finding fixes
local verification
documentation directly implied by an accepted change
```

### Escalate

```text
ambiguity in What/Why
acceptance-criteria changes
domain-invariant changes
public API changes not in approved spec
architecture-boundary changes
security-policy changes
destructive database/data operations
production-impacting actions
repeated non-converging fixes
contradictory evidence
insufficient evidence
```

### Model-confidence escalation

When a consequential decision still has material uncertainty, assess confidence
as a subjective judgment. Continue autonomously only when confidence is **above
90%**, and only within already authorized scope. At **90% or below**, consult
the next distinct model/settings rung configured for the active runtime, once
per rung, before asking the human. Give each assessor the decision, scope,
evidence, uncertainty, and earlier assessments. Skip a rung already satisfied
by an earlier assessment of the same decision from that rung or a later rung
in the same configured ladder. Use the runtime's supported model-selection/
spawn mechanism and verify the actual model/settings; unavailable or
unverifiable rungs count as unavailable. Record the assessment, confidence,
and actual model/settings in the existing work artifact; confidence is not a
measured probability or verification evidence.

Use only the active runtime's verified `confidence_escalation` binding. Entries
are native picker names; Codex encodes effort as `model@effort`. The current
Codex ladder is Sol/high → Astra/medium → Astra/high. Claude Code uses
`claude-opus-5-5` → `claude-fable-5-2` when those native model IDs are
available. Cursor and OpenCode have no verified ladder yet; do not infer one
from their diverse/adversarial defaults. Report unavailable rungs as
unavailable.

Model consultation cannot approve a scope or acceptance change, supply human
preference or authority, authorize destructive or production-impacting actions,
override explicit user model restrictions, replace an assigned independent
reviewer, or waive required verification. Ask the human when the configured
ladder is exhausted and uncertainty remains material, or when the decision
requires human authority or preference.

### Never silently do

```text
broaden scope
weaken acceptance criteria
delete constraints because they are inconvenient
overwrite another workstream's uncommitted changes
claim verification without running it
promote observed behavior to canonical specification
rewrite accepted specification to unblock implementation
start labor on a dirty working tree without grilling the human
run overlapping related branches that will conflict on shared files
defer all commits until the entire plan is finished
wait for the human to ask before committing on the workstream branch
skip kit artifacts while claiming to stay on the kit path
skip kit stages silently (on-path: prepare the artifact; off-path: warn once only if they explicitly left)
re-ask approval on every stage after a defaults-OK confirm (until Accept)
```

---
