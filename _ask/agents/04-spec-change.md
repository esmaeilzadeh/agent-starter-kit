# Kit Protocol: 04 Spec Change

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Output: `_ask/templates/spec-change.md` instance. Never silently rewrite the canonical accepted spec.

## 15.4 04 Spec Change Agent

Purpose:

```text
Turn discovered semantic problems into explicit specification-change proposals.
```

Triggers:

```text
analytics reveals new intended behavior
implementation exposes a requirement conflict
review reveals semantic mismatch
acceptance criteria are discovered to be wrong
```

Must:

```text
preserve the current accepted spec
show why a change is proposed
identify impact
identify alternatives
request the required decision
```

Must not:

```text
rewrite current specs silently
change acceptance criteria merely to make tests pass
change business semantics without the required authority
```

---

## Kit emphasis

- Forbidden: silent rewrite of the canonical accepted specification.
- Kit path: `_ask/policies/workflow.md` — a spec change is a new decision, not covered by an older defaults-OK. Prepare the change artifact and get a confirm.
- Before finishing the change artifact, read the prepared `writing-for-agents` skill and follow it in embedded mode (`.agents/skills/writing-for-agents/SKILL.md`; `./ask prepare` if missing). Do not apply `humanizer` to the change artifact. ADR: `_ask/docs/adr/0017-humanizer-docs-specs.md`.
- Marked OpenSpec pilot (`Engine: openspec` in intent): change semantics through the active `openspec/changes/<work-id>/`. If that change is already openspec-archived, create a new active directory with the same work-id; leave the archived copy under `openspec/changes/archive/`; record the new change in intent.
