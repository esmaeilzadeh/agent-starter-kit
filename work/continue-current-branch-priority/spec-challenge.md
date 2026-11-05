# Specification Challenge

## Model

- **Model:** gpt-6.1-sol
- **Runtime:** Codex
- **Parent model:** gpt-6.1-sol

## Specification

`specs/current/continue-current-branch-priority.md` and its JSON criteria.

## Ambiguities

The original fallback wording allowed relevant authorization evidence to
conflict without requiring clarification when only one target remained.
The original explicit-target rule did not say what to do when that target could
not be resolved.

## Missing failure cases

- Checkout and workstream artifacts identify one target, but stage or
  authorization evidence conflicts.
- An explicitly named target is missing or ambiguous while the checkout points
  to another workstream.
- No work branch or matching artifacts identify a target.

## Over-constraint risks

Treating every live workstream as a plausible continuation target would restore
the original unnecessary chooser. The checkout rule must stay scoped to an
unqualified continuation request and a matching `agent/<work-id>` branch.

## Under-constraint risks

Choosing the matching branch despite unresolved authorization evidence could
resume work beyond its accepted scope. A terminal result must report its
endpoint without inferring permission to start a later stage.

## Recommended clarifications

- Resolve an explicit target first; if it is ambiguous or unavailable, ask
  about that target and do not silently substitute the checkout.
- For unqualified continuation, use remaining evidence to resolve target and
  authorized endpoint. Ask when no target is identifiable, multiple targets
  remain plausible, or stage or authorization evidence conflicts.
- Add a fallback acceptance criterion for non-work branches, missing artifacts,
  multiple candidates, and unresolved authorization.

## Initial challenge verdict

REVISION REQUIRED

## Follow-up

**PASS.** The revised behavior and JSON criteria close the findings:

- Unresolved stage or authorization conflicts require clarification even when
  only one target exists.
- Zero identifiable targets now explicitly requires clarification.
- `CONT-004` covers fallback recovery, including missing artifacts, multiple
  targets, unresolved conflicts, and successful recovery from remaining
  evidence.
- `CONT-003` covers unavailable or ambiguous explicit targets and prohibits
  substituting the checkout.

The Markdown fallback acceptance criterion was aligned with `CONT-004` so an
unmatched checkout does not automatically force clarification when remaining
evidence resolves one target.
