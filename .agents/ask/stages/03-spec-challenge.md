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

When the challenge writes prose, read the prepared `writing-for-agents` skill and follow it in embedded mode (`.agents/skills/writing-for-agents/SKILL.md`; `./ask prepare` if missing). Do not apply `humanizer` to the challenge artifact. ADR: `_ask/docs/adr/0017-humanizer-docs-specs.md`.

## Model spawn (required)

Spawn the generated Spec Challenge subagent for the current runtime. Present that runtime’s picker list from `_ask/bindings/runtimes/<runtime>.yaml` (default highlighted). The human confirms. If the pick is the same family as Spec on that runtime, warn once; continue after a second confirm. Record `model`, `runtime`, and `parent_model` (or Spec model) on `spec-challenge.md`. Do not author the challenge only in the parent context.
