# Specification Challenge

## Specification

`specs/current/promote-kit-specs.md`

## Ambiguities

“Move” could mean delete product specs. Default: keep the files as pointers so workstream provenance stays.

## Missing failure cases

Inserting a full copy of `demo-nn-train` (trainer/viewer) into the Build Spec. Guarded as a non-goal.

## Over-constraint risks

Requiring `_ask/MAPPING.md` update is slightly beyond “only `_ask/spec/`” but §38 already requires the companion map to stay aligned.

## Under-constraint risks

Leaving product specs intact as a second full SoT. Challenge: pointers are required.

## Recommended clarifications

None — defaults are enough.

## Challenge verdict

PASS
