# Kit Protocol: 03 Spec Challenge

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Output: `_ask/templates/spec-challenge.md` instance under the workstream.

## 15.3 03 Spec Challenge Agent

Purpose:

```text
Challenge the specification before implementation.
```

Must:

```text
look for ambiguity
look for conflicting constraints
construct concrete counterexamples
challenge acceptance criteria
look for unsupported assumptions
check alignment with Why
```

Output:

```text
work/<work-id>/spec-challenge.md
```

Gate:

```text
PASS → eligible for acceptance
ESCALATE → human decision required
```

---

## Kit path

See `_ask/policies/workflow.md`. Prepare `spec-challenge.md`. After defaults-OK, do not re-ask a bless unless the challenge **escalates**. Off-path only if they explicitly leave the kit.

When the challenge writes prose, read the prepared `humanizer` skill and follow it in embedded mode (`.agents/skills/humanizer/SKILL.md`; `./ask prepare` if missing). ADR: `_ask/docs/adr/0017-humanizer-docs-specs.md`.
