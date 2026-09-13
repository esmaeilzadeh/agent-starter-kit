# Explore Map: user MCP + tracker wizard + existing-repo setup

## Destination

A **human-run setup wizard** that (1) can attach this kit to an already-built git repo using the existing overlay, (2) lets the human pick an issue tracker (`gitlab` / `github` / `jira` / `none`), (3) collects instance URL and credentials with per-tracker prefills (or skips those stages when `none`), and (4) installs memory MCP tools — without committing secrets.

## Notes

- Seed: `.later/user-mcp-jira-and-memory.md` (human expanded: multi-tracker + wizard + existing repo).
- Skills: wayfinder (file map; no tracker mirror this session), research, grilling. Wizard skill is the likely implementation method later — not used to build yet.
- Local-markdown map is canonical (`explore-map.md`). No GitHub wayfinder issue created.
- Facts: `work/user-mcp-tools/explore/facts-mcp-and-install.md`.

## Tracker map (optional)

None. This file is the Grill handoff.

## Decisions so far

Stated by the human this session (still confirm in Grill if they conflict):

- Tracker is **chosen by the user**, not hardcoded to Jira.
- Options: **GitLab, GitHub, Jira, none**.
- Shape is a **wizard**: choose tracker ↔ URL (prefill per tracker) ↔ API key.
- `none` skips URL/key stages; the remaining action is to **re-ask** (go back and pick a tracker).
- Each tracker uses **that tracker’s proper tooling** (not Jira MCP for GitHub/GitLab).
- Memory MCP tools are installed via **prepare / install script**, not hand-copied.
- Must offer using the kit in an **already-built repo** (document or wrap what already exists).

Facts (not decisions) — see explore research note:

- `./ask install <repo>` already overlays into an existing git repo and is **non-interactive** (agent-safe). Do not break that.
- Cursor MCP: global `~/.cursor/mcp.json`, project `.cursor/mcp.json`; use `${env:NAME}` for secrets.
- This machine already has global `codebase-memory-mcp` and `mcp-atlassian`.
- Official GitHub MCP (hosted or Docker + PAT). Official GitLab MCP (`/api/v4/mcp`, OAuth). Jira via `mcp-atlassian` (URL + token).

## Not yet specified

- Kit product on `main` vs user-local-only scripts (original card said “not kit product unless Grill says so”).
- Command split: new `./ask setup` vs `--interactive` on install vs two commands (recommended split below).
- Where tokens and “current epic/story” live (global MCP vs gitignored per-repo context).
- Memory MCP menu: one default vs optional list vs skip-like `none`.
- Prefill values (Jira `https://jira.partcorp.ir/` was a card default only).
- Whether GitLab uses official OAuth MCP (no PAT in file) vs a PAT-based community server.

## Out of scope

- Storing live tokens in git, cards, or chat examples.
- Replacing `./ask install`’s non-interactive agent contract with a blocking wizard.
- Building a multi-agent runtime or a status board for `.later/`.
- Implementing in this Explore session.

## Handoff to Intent

**STILL_FOGGY.** Destination is named; What/Why cannot be owned until the first Grill round below is answered (product vs local, wizard vs install split, secret/context storage).

Draft Why: humans must configure tracker + memory MCP per machine and per repo without leaking tokens, and must be able to drop the kit onto a repo that already has product code.

Draft What (unapproved): ship a human-only setup wizard; keep `./ask install` as the existing-repo overlay; bind GitHub / GitLab / Jira / none with official-or-documented tooling; write MCP config that interpolates env secrets; optionally write gitignored current-issue context.

Next: answer Explore grilling Q1–Q4. Then rewrite this Handoff as DESTINATION_CLEAR or keep exploring.
