# Specification Challenge

## Specification

`specs/current/user-mcp-tools.md`

## Ambiguities

`~/.cursor/mcp.json` merge could clobber an existing server of the same name. Spec: merge by server key; keep other servers.

## Missing failure cases

Wizard runs in a non-git directory. Prefer: refuse unless inside a git repo (setup configures a clone).

## Over-constraint risks

Requiring a TTY on both stdin and stdout. `--help` is exempt. Piped stdout still refuses the interactive path — acceptable.

## Under-constraint risks

No test that `mcp.json` never receives raw tokens (hard to test without running the wizard). Static: writers use `${env:...}` only.

## Recommended clarifications

Refuse setup outside a git work tree. Merge MCP servers by name.

## Challenge verdict

PASS
