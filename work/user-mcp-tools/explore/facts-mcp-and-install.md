# Facts: MCP layout, tracker servers, existing install

Research for `user-mcp-tools` Explore. Not a decision record.

## Cursor MCP files

Primary: [Cursor MCP docs](https://cursor.com/docs/mcp).

- Project: `.cursor/mcp.json` in the workspace.
- Global: `~/.cursor/mcp.json`.
- Same server name: project overrides global. Defining the same name in both can duplicate in the UI.
- Interpolation in `command` / `args` / `env` / `url` / `headers`: `${env:NAME}`, `${userHome}`, `${workspaceFolder}`.
- VS Code-style `inputs` / `${input:...}` are not honored. Prefer `${env:...}` so tokens stay out of git.

This machine (names only, no secrets printed):

- Global `~/.cursor/mcp.json` exists with servers `codebase-memory-mcp`, `mcp-atlassian`.
- This repo has no `.cursor/mcp.json`.
- `~/.local/bin/codebase-memory-mcp` exists. `uvx` and `gh` exist. `glab` does not.

## Tracker MCP (official)

| Tracker | Bind | Auth |
| --- | --- | --- |
| GitHub | Hosted `https://api.githubcopilot.com/mcp/` or Docker `ghcr.io/github/github-mcp-server`. Deprecated npm `@modelcontextprotocol/server-github`. Docs: [install-cursor.md](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-cursor.md) | PAT (`${env:GITHUB_TOKEN}`). |
| GitLab | Official HTTP `https://<host>/api/v4/mcp` ([GitLab MCP docs](https://docs.gitlab.com/user/model_context_protocol/mcp_server/)) | OAuth in browser after save. Self-managed: replace host. |
| Jira | Community/Atlassian `mcp-atlassian` (this user already runs `uvx mcp-atlassian`) | URL + personal token. Never commit. |

This kit repo’s tracker doc is GitHub + `gh` CLI: `_ask/docs/agents/issue-tracker.md`. That is CLI convention, not MCP.

## Already-built repo (existing mechanism)

`./ask install <target-repo>` already overlays the kit into an existing git repo (spec §34b, ADR-0006).

- Copies `_ask/`, `.cursor/`, merge-safe `AGENTS.md`, `ask`.
- Does **not** touch consumer `docs/`, `scripts/`, `tests/`, `src/`.
- **No interactive prompts on the agent path.**
- Then `./ask prepare` + `./ask sync` unless `--skip-prepare`.
- Primary distribution is still clone/copy of this template.

A human wizard must not turn `install` into an interactive agent command. Keep install non-interactive; wizard is a separate human-run path that may *call* install.

## Wizard method

Community skill `wizard` (mattpocock): interactive bash, hidden secret entry, `.env` upserts, confirm gates. Ephemeral unless the repo wants a repeatable setup path.
