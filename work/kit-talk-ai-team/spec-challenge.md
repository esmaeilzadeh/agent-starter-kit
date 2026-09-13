# Specification Challenge

## Specification

`specs/current/kit-talk-ai-team.md`

## Ambiguities

"Exactly one content slide" for the demo is clear. A title/section divider that only says "Demo" would be a second slide if we add one; do not add a divider plus a content slide.

## Missing failure cases

Print-to-PDF is unspecified. Acceptable if unused; do not block on it.

## Over-constraint risks

Banning a CDN is correct for a room with no network. Inlining CSS/JS is enough.

## Under-constraint risks

Slide count is unspecified. 90 minutes with discussion can sit in roughly 20–28 slides; the spec judges by section weight, not a number.

## Recommended clarifications

None that block Plan.

## Challenge verdict

PASS
