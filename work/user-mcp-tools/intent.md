# Intent: user MCP + tracker wizard + existing-repo setup

## What

Ship a kit-owned, **human-only** `./ask setup` wizard that:

1. Can attach the kit to an already-built git repo by calling existing `./ask install` (overlay only; no rewrite of that command).
2. Asks the human to choose an issue tracker: GitLab, GitHub, Jira, or none. None skips URL/key stages; the only remaining action is to go back and choose again.
3. Collects instance URL with prefills (Jira `https://jira.partcorp.ir/` labeled as a default they can clear; GitHub `https://github.com/` or `git remote`; GitLab `https://gitlab.com/`). All editable.
4. Binds **that tracker’s proper tooling**: GitLab official MCP + browser OAuth (URL only); GitHub official MCP + PAT via env; Jira `mcp-atlassian` + URL + token via env.
5. Optionally installs memory MCP tools (menu, skip allowed; default `codebase-memory-mcp`).
6. Commits `.ask.env.example` (placeholders only). Writes live secrets to gitignored `.ask.env`. MCP config uses `${env:...}`. Per-repo current issue lives in a gitignored context file. Committed: tracker type + public URL only.

`./ask install` stays non-interactive so agents never block on prompts. Agents must not run `setup`.

## Why

Humans need tracker + optional memory MCP without leaking tokens, and need to drop the kit onto a repo that already has product code.

## Non-goals

- Interactive `./ask install` / `--interactive` on install
- Committing live `.ask.env` or tokens
- Replacing official GitHub/GitLab MCP with Jira tools
- A later-inbox status board
- Implementing Explore leftovers as new product scope (extra memory servers can stay “discover or skip”)

## Known assumptions

- Explore map `work/user-mcp-tools/explore-map.md` is the source of What/Why.
- This machine already has global `codebase-memory-mcp` and `mcp-atlassian`; the wizard must still work on a clean machine.
- Cursor honors `~/.cursor/mcp.json` and `.cursor/mcp.json` with `${env:NAME}`.

## Open questions

- Exact gitignored path for current epic/story (default in Spec: e.g. `.ask/tracker-context.md`).
- Extra memory servers on the menu besides `codebase-memory-mcp` (default: discover or skip).

## Human decisions

Explore Q1–Q8 accepted as recommended (2026-09-13). Ready for defaults-OK, then Spec.
