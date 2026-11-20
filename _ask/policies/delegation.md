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
