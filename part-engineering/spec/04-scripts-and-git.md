# Git Guardrails, Scripts, and Workstreams

# 23. Git guardrails

## 23.1 `check-clean-worktree.sh`

Behavior:

```text
exit 0 → working tree clean
exit non-zero → working tree dirty
```

It must not stash, reset, or absorb user changes.

## 23.2 `start-work.sh <work-id>`

Behavior:

```text
1. require clean working tree
2. verify Git repository
3. identify default/main branch
4. create or switch to dedicated work branch
5. create work/<work-id>/ artifacts
6. print current HEAD SHA
7. print active branch
```

Default branch convention:

```text
agent/<work-id>
```

The script must refuse to silently proceed when unrelated local changes exist.

## 23.3 `check-workstream.sh`

Before delegated work, verify:

```text
branch is dedicated to current work-id
working tree is clean or changes are explicitly attributable to current work
accepted spec exists
plan exists
```

This can be called by agent instructions before implementation/review/refactor.

---

# 24. Verification script

Provide:

```text
scripts/verify.sh
```

It should:

```text
detect project/package manager where possible
read project-specific configuration
run configured mandatory checks
fail on mandatory failures
print exact commit SHA
emit machine-readable verification output
```

Do not hard-code NestJS, Node, Python, Rust, or any other specific technology into the core.

Provide extension/configuration points for the consuming repository.

---

# 25. Result recording script

Provide:

```text
scripts/record-result.sh <result-file>
```

It should validate or inject:

```text
current commit SHA
work ID
spec reference
verification reference
```

It must refuse to record a result when no exact commit SHA can be obtained.

A result such as:

```text
"new version is faster"
```

is not valid without an identifiable code state.

---

# 26. Failure convergence

The starter kit must protect against non-converging autonomous loops.

Example:

```text
Review A
→ Refactor
→ Review A
→ Refactor
→ Review A
```

After a configurable number of unsuccessful repair cycles, stop and escalate.

A conservative default is:

```text
2–3 unsuccessful repair cycles
```

Do not treat unlimited retry as free labor.

Retries consume:

```text
compute
latency
human attention
risk budget
```

---

# 27. Conflict resolution

The policy should define precedence among competing constraints.

Suggested starting point:

```text
explicit human requirement
    > domain invariant
    > security/safety constraint
    > accepted specification
    > correctness
    > reliability
    > performance
    > maintainability/style
```

This is a template, not a universal law.

The project must customize it.

Model majority must not be the default authority.

---

# 28. Acceptance debt visibility

The starter kit should be able to expose at least a lightweight signal when work has accumulated without sufficient evidence.

A simple implementation may track:

```text
work items completed
verification records present
acceptance decisions present
unresolved high-risk findings
```

The kit does not need a complex dashboard in v1.

It must at least make it possible to identify:

```text
engineering output without corresponding evidence
```

---

# 29. Provenance and state storage boundaries

The starter kit must distinguish three classes of data.

## 29.1 Durable engineering state

Keep in repository/version control when appropriate:

```text
code
specs
project-specific rules
policies
decisions
skill manifest
acceptance artifacts
verification references
```

## 29.2 Compact execution/provenance records

Keep as repository artifacts or external result records:

```text
run ID
commit SHA
spec reference
policy/skill references
verification ID
result ID
```

## 29.3 Raw execution telemetry

Do not store by default:

```text
full prompts
full context dumps
all tokens
every tool call
all retry transcripts
```

Store those separately only when an explicit audit/security/debugging requirement exists.

---

# 30. Workstream directory convention

For a task `cancel-order`:

```text
work/cancel-order/
├── explore-map.md       # only when Explore ran
├── intent.md
├── spec-challenge.md
├── spec-change.md      # only when needed
├── plan.md
├── review.md
├── verification.json
└── acceptance.md
```

Canonical spec proposal:

```text
specs/proposals/cancel-order.md
```

Canonical current spec after the required lifecycle:

```text
specs/current/cancel-order.md
```

Branch:

```text
agent/cancel-order
```

---
