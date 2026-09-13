# Plan

## Specification

`specs/current/user-mcp-tools.md`

## Approach

Human-only wizard from the Community wizard library (library above STAGES untouched). Dispatcher + gitignore + example env + tests that do not run the interactive path.

## Work breakdown

1. Spec artifacts (this file, challenge, CURRENT spec)
2. `.ask.env.example`, `.ask/README.md`, gitignore
3. `_ask/scripts/setup.sh` + `ask` `setup` mapping
4. Docs (README, AGENTS, Build Spec §22.9) + install copies `.ask.env.example`
5. Tests: help, non-TTY refuse, gitignore, example has no token-looking values
6. Verify

## Risks

Merging `~/.cursor/mcp.json` on a machine with live config. Merge by key; never print env values.

## Verification approach

`./ask verify`. Do not run the wizard end-to-end (opens browsers, blocks on humans).

## Out of scope for this plan

Interactive install. Extra memory MCP catalog beyond default + skip + custom.
