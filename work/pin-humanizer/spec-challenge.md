# Specification Challenge

## Specification

`specs/current/pin-humanizer.md`

## Ambiguities

“Docs and specs” includes `specs/`, `_ask/guide/`, `_ask/spec/`, `_ask/docs/`, root `README.md` / `AGENTS.md` / `CONTEXT.md`. Plans and review notes are not in the required set; the always-on rule still applies if the agent is writing prose there.

Upgrade does not add the pin to an existing consumer manifest. The stock rule still points at the skill; the agent prepares it only after the consumer pin exists (or this repo’s stock pin does).

## Missing failure cases

Consumer upgrade: rule arrives, pin does not. Acceptable: rule says prepare if the body is missing; consumers add the pin when they want the required install.

## Over-constraint risks

`required: true` fails prepare for this repo if GitHub is unreachable. Same as other required pins.

## Under-constraint risks

Glob-only rule would miss new files not yet on disk. Always-on thin pointer is the tighter fit.

## Recommended clarifications

None that change What. Record the consumer-manifest note as an assumption, already in intent.

## Challenge verdict

PASS
