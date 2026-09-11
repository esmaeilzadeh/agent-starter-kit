# Examples, AGENTS, and Cursor Binding

# 31. Minimal complete example

## 31.1 Foggy / R&D first (Explore)

For a large unclear effort `payments-v2`:

```text
Human
  → foggy destination

00 Explore
  → work/payments-v2/explore-map.md
  → research + grilling tickets
  → DESTINATION_CLEAR handoff

01 Grill
  → work/payments-v2/intent.md

… then continue as in 31.2
```

## 31.2 Clear intent (skip Explore)

For `cancel-order`:

```text
Human
  → states What/Why

01 Grill
  → work/cancel-order/intent.md

02 Spec
  → specs/proposals/cancel-order.md

03 Spec Challenge
  → work/cancel-order/spec-challenge.md

Human
  → accepts spec

05 Plan
  → work/cancel-order/plan.md

06 Implement
  → branch agent/cancel-order
  → commit C1

07 Review
  → work/cancel-order/review.md

08 Refactor
  → commit C2

09 Verify
  → work/cancel-order/verification.json

10 Accept
  → work/cancel-order/acceptance.md

Human approval
  → only where policy requires it
```

If review discovers:

```text
"Current specification is semantically wrong"
```

do not patch the spec silently.

Instead:

```text
04 Spec Change
  → work/cancel-order/spec-change.md
  → decision
  → revised spec
  → affected implementation
  → verification
```

If the problem is not a local semantic fix but the destination itself is wrong, return to `00 Explore`.

---

# 32. Analytics and specification evolution example

Suppose a performance analysis reveals:

```text
Current behavior:
API blocks while payment provider completes.

Analysis:
User only needs immediate acknowledgement.
```

The system should not automatically rewrite the current spec.

Instead:

```text
Analytics result
→ proposed semantic change
→ Spec Change Agent
→ Spec Challenge
→ human decision
→ accepted spec revision
→ implementation
→ verification
```

The experiment result must reference the exact commit it evaluated.

---

# 33. Acceptance example

For a low-risk refactor:

```text
review findings resolved
unit tests pass
type checks pass
integration tests pass
no scope expansion
commit identified
```

Policy may return:

```text
AUTO_ACCEPT_ELIGIBLE
```

For a destructive migration:

```text
verification passes
```

but policy may still require:

```text
HUMAN_APPROVAL_REQUIRED
```

This demonstrates the separation between evidence and authority.

---

# 34. Root `AGENTS.md` contract

The root file should remain short and operational (about ≤30 lines of checklist).

It should instruct every agent that:

```text
This repository uses the AI Engineering Starter Kit.

If the destination is foggy:
- run 00 Explore (kit stage — not Cursor’s built-in Explore subagent) until handoff is clear;
- prepare Community Skills from part-engineering/skills/manifest.yaml (do not vendor by default).

Before independent Engineering Pipeline work:
- require a clean working tree;
- use a dedicated branch;
- identify work-id;
- identify accepted specification;
- read relevant policies;
- prepare pinned skills needed for the role.

During work:
- stay within assigned scope;
- do not silently change What/Why or acceptance criteria;
- follow escalation policy;
- preserve workstream isolation;
- commit meaningful states.

Before claiming completion:
- run configured verification;
- record exact commit SHA;
- leave required structured artifacts.
```

Do not copy the entire guide into `AGENTS.md`.

---

# 34a. Thin Cursor Binding

Cursor-only adapter layer. Protocol under `part-engineering/` remains source of truth.

**Must ship so Cursor honors the kit:**

```text
AGENTS.md                              # ≤~30 lines; prepare; Explore name caveat
.cursor/rules/*.mdc                    # bootstrap: point at protocol — do not duplicate policy text
.cursor/hooks.json                     # beforeShellExecution → wrappers
.cursor/hooks/*.sh                     # thin wrappers calling scripts/check-*.sh
.cursor/skills/ or commands/           # generated projections of 00–10 (see sync)
.agents/skills/                        # prepared Community Skills (gitignore bodies)
```

**sync-cursor-binding.sh** (or prepare step): generates/refreshes Cursor-honored projections under `.cursor/` from `part-engineering/agents/*.md` (skill wrappers and/or slash commands; optional generated agents). Do not hand-maintain eleven Cursor subagents as a second SoT.

**Rules:** rules *point*; protocol *owns* text. Logic for Git guardrails lives in `scripts/`; `.cursor/hooks` are mandatory entrypoints. Anything Cursor must honor must exist under `.cursor/` even if a portable source also lives under `part-engineering/` or `.agents/`.

Do not treat protocol files alone as auto-loaded Cursor stages. Defer Cursor Plugins packaging for v1.

---

# 34b. Optional install-into-existing

Provide:

```text
scripts/install-kit.sh <target-repo>
```

**Primary distribution** remains: clone/copy this template repo.

**Overlay (default) copies:**

```text
part-engineering/     # protocol + guide/ + spec/ modules
scripts/              # including prepare-skills + sync-cursor-binding
.cursor/              # complete Cursor-honored projection
AGENTS.md             # merge/append unless --force
skills-lock.json      # if present
```

**Never touches by default:** consumer `docs/`, application `src/`, unrelated product specs.

**Does not copy** `.agents/skills/` bodies; runs `prepare-skills.sh` + `sync-cursor-binding.sh` after overlay unless `--skip-prepare`.

**Flags:** `--dry-run`, `--force` (overwrite kit-owned paths), `--skip-prepare`. Refuse if target is not a git repo. No interactive prompts on the agent path.

---

# 34c. Kit upgrade and consumer overrides

Provide:

```text
scripts/upgrade-kit.sh --version <tag-or-sha>
```

The kit repository **dogfoods** its own `part-engineering/` and Cursor Binding.

**Kit-owned** (safe to refresh on upgrade): stock stage contracts, templates, guide/spec modules, stock scripts, generated `.cursor` projections.

**Consumer-owned** (never clobber by default): `part-engineering/skills/manifest.yaml`, policies (or local policy tree), local `AGENTS.md` sections, `.cursor/rules/local/`, `part-engineering/agents/*.local.md` (per-stage overlays merged at sync time).

Upgrade pulls an **explicit kit version/tag** (not blind `main`), refreshes kit-owned files, then runs prepare + sync unless `--skip-prepare`. Community Skill updates remain separate deliberate manifest pin bumps.

---
