# Cursor Binding Surfaces — Research

**Question:** What Cursor-native surfaces should the Starter Kit’s thin **Cursor Binding** use?

**Scope:** Primary sources only — [cursor.com/docs](https://cursor.com/docs).  
**Kit context:** [CONTEXT.md](../../CONTEXT.md) defines **Cursor Binding** as how the kit is expressed inside Cursor (skills, rules, `AGENTS.md`, hooks) *without becoming the protocol itself*. The kit remains a portable repository protocol; Cursor is the first-class runtime binding.

---

## Summary

A **thin Cursor Binding** should use Cursor’s **Customize** component model as a small adapter layer on top of portable **Kit Protocol Files**, not as a second copy of the workflow.

| Use in binding | Cursor surface | Role for the kit |
| --- | --- | --- |
| **Yes — core** | Root `AGENTS.md` | Short operational entry; context-assembly pointer to kit protocol |
| **Yes — core** | `.cursor/hooks.json` + scripts | Deterministic Git/workstream guardrails (call kit shell scripts) |
| **Yes — core** | Prepared Community Skills in `.agents/skills/` | Pinned external methods from `part-engineering/skills/manifest.yaml` |
| **Yes — optional thin** | `.cursor/rules/*.mdc` | Scoped triggers (“when in `work/`…”, “before implement…”) pointing at protocol files |
| **Yes — optional thin** | `.cursor/commands/` | Slash shortcuts that kick off kit stages (`/grill`, `/verify`) |
| **Yes — optional** | `.cursor/worktrees.json`, CLI `--worktree`, `/worktree` | Cursor-native isolation complementary to kit branch convention |
| **Defer / minimal** | `.cursor/agents/` subagents | Only for Cursor-specific isolation (e.g. readonly verifier); do **not** mirror all 11 kit roles |
| **Defer v1** | Cursor Plugins (`.cursor-plugin/`) | Distribution packaging, not required for in-repo protocol |
| **Out of binding** | Kit policies, agent contracts, templates, scripts, manifest | Stay as **Kit Protocol Files** |

**Precedence takeaway:** Team Rules beat Project Rules beat User Rules; nested `AGENTS.md` beats parent `AGENTS.md` for files in that subtree. Hooks merge all sources with Enterprise → Team → Project → User priority. Rules and hooks are **steering + enforcement layers**; kit shell scripts remain the portable source of truth for Git hygiene.

---

## Findings (with citations)

### 1. Customize — the surface catalog

Cursor documents six composable extension components managed from **Customize**: Plugins, Rules, Skills, Subagents, Hooks, and Commands. Plugins bundle these; each can also be added standalone.  
**Source:** [Customize Cursor](https://cursor.com/docs/customize-cursor)

This is the authoritative menu of Cursor-native surfaces relevant to a thin binding.

---

### 2. Skills — discovery and `SKILL.md` requirements

#### Automatic discovery

On startup, Cursor discovers skills from skill directories and exposes them to Agent; the agent decides relevance from context. Skills can also be invoked via `/skill-name` in chat.  
**Source:** [Agent Skills](https://cursor.com/docs/skills)

#### Discovery locations (project and user)

| Location | Scope |
| --- | --- |
| `.agents/skills/` | Project |
| `.cursor/skills/` | Project |
| `~/.agents/skills/` | User (global) |
| `~/.cursor/skills/` | User (global) |

For compatibility, Cursor also loads `.claude/skills/`, `.codex/skills/`, and user-level Claude/Codex paths.  
**Source:** [Agent Skills — Skill directories](https://cursor.com/docs/skills)

Additional discovery behaviors relevant to the kit:

- **Recursive walk:** Cursor walks skill roots recursively and picks up any `SKILL.md`; category folders are organizational only.  
  **Source:** [Agent Skills — Nested skill directories](https://cursor.com/docs/skills)
- **Nested project dirs:** A `.cursor/skills/` or `.agents/skills/` folder anywhere in the repo is discovered; skills in nested dirs are auto-scoped to that directory (similar to the `paths` frontmatter field).  
  **Source:** [Agent Skills — Nested skill directories](https://cursor.com/docs/skills)
- **CLI / multi-root:** Skills load in interactive, headless, and editor-integration modes; nested `.cursor/skills` in subdirectories are discovered; skill scans skip hidden dot-directories; symlinks are followed.  
  **Source:** [CLI Changelog](https://cursor.com/docs/cli/changelog)

#### `SKILL.md` format (required fields)

Each skill is a folder containing `SKILL.md` with YAML frontmatter:

| Field | Required | Notes |
| --- | --- | --- |
| `name` | Yes | Lowercase, numbers, hyphens; **must match parent folder name** |
| `description` | Yes | Used for agent relevance |
| `paths` | No | Glob scope (comma-separated string or list) |
| `disable-model-invocation` | No | If `true`, only via explicit `/skill-name` |
| `icon`, `color`, `metadata` | No | Custom Mode styling / extra metadata |

Optional directories: `scripts/`, `references/`, `assets/`.  
**Source:** [Agent Skills — SKILL.md file format](https://cursor.com/docs/skills)

#### Cloud / personal skills

- Personal skills in `~/.cursor/skills/` stay local unless **Sync Skills for Cloud Agents** is enabled (only `~/.cursor/skills/` syncs; project skills and `~/.agents/skills/` stay local).  
  **Source:** [Agent Skills — Use personal skills with Cloud Agents](https://cursor.com/docs/skills)
- To share with teammates, publish to team marketplace (distinct from sync).  
  **Source:** [Agent Skills — Team admin controls](https://cursor.com/docs/skills)

#### Implication for kit Skill Preparation

- **`part-engineering/skills/manifest.yaml`** = Kit Protocol (pins, roles) — not a Cursor discovery path.
- **Prepared Community Skills** should materialize as standard `SKILL.md` trees under **`.agents/skills/`** (Agent Skills open-standard path, also read by Cursor) rather than vendoring into kit-owned protocol paths.
- Kit Protocol Files (`part-engineering/agents/*.md`) must **not** be copied into skill folders; they are workflow contracts, not Community Skills.

---

### 3. Rules, `AGENTS.md`, and instruction precedence

#### Four rule types

Cursor supports: **Project Rules** (`.cursor/rules`), **User Rules**, **Team Rules**, and **`AGENTS.md`**.  
**Source:** [Rules](https://cursor.com/docs/rules)

#### Project rules (`.cursor/rules/*.mdc`)

- Must use `.mdc` extension with frontmatter (`description`, `globs`, `alwaysApply`).
- Plain `.md` in `.cursor/rules` is **ignored** (no frontmatter → not a rule). Use `AGENTS.md` for plain markdown instead.  
  **Source:** [Rules — Project rules](https://cursor.com/docs/rules)

Rule application modes: Always Apply, Apply Intelligently (description), Apply to Specific Files (globs), Apply Manually (`@`-mention).  
**Source:** [Rules — Rule anatomy](https://cursor.com/docs/rules)

#### Cross-scope precedence (explicit)

> Rules are applied in this order: **Team Rules → Project Rules → User Rules**. All applicable rules are merged; **earlier sources take precedence** when guidance conflicts.

**Source:** [Rules — Team Rules](https://cursor.com/docs/rules)

Team Rules can be enforced (non-disableable). User Rules apply to Agent (Chat) globally but **not** Inline Edit (Cmd/Ctrl+K). Rules do **not** affect Cursor Tab.  
**Source:** [Rules — FAQ](https://cursor.com/docs/rules)

#### `AGENTS.md`

- Plain markdown alternative to `.cursor/rules` for simple, readable instructions.
- Supported at **project root and in subdirectories**.
- Nested files combine with parents; **more specific (deeper) instructions take precedence**.  
  **Source:** [Rules — AGENTS.md](https://cursor.com/docs/rules)

#### CLI / Cloud

- CLI loads `.cursor/rules` and also reads root **`AGENTS.md`** and **`CLAUDE.md`**, applying them as rules alongside project rules.  
  **Source:** [Using Agent in CLI — Rules](https://cursor.com/docs/cli/using)
- Cloud Agent best practices recommend committing project skills and using `AGENTS.md` for cloud-specific setup sections.  
  **Source:** [Cloud Agent Best Practices](https://cursor.com/docs/cloud-agent/best-practices)

#### Precedence gap (open)

Official docs state Team → Project → User precedence and nested `AGENTS.md` specificity, but **do not explicitly rank `AGENTS.md` vs `.cursor/rules/*.mdc` at the same directory level**. Treat them as merged project-level instruction sources; avoid duplicating the same policy in both.

#### Steering vs enforcement

Rules are **LLM steering** (non-deterministic). Security docs recommend combining rules with **enforcement hooks** for must-follow constraints.  
**Source:** [LLM Safety and Controls — Two approaches to safety](https://cursor.com/docs/enterprise/llm-safety-and-controls)

---

### 4. Hooks — Git guardrails and workstream hygiene

#### What hooks are

Hooks observe, control, or extend the agent loop via `hooks.json` + scripts communicating JSON over stdio. They can observe, block, or modify behavior at defined lifecycle points.  
**Source:** [Hooks](https://cursor.com/docs/hooks)

Configurable at: project (`.cursor/hooks.json`), user (`~/.cursor/hooks.json`), team (Enterprise dashboard), enterprise (MDM).  
**Source:** [Hooks — Quickstart / Configuration](https://cursor.com/docs/hooks)

#### Hook priority (explicit)

When responses conflict: **Enterprise → Team → Project → User** (highest to lowest). All matching hooks from every source run.  
**Source:** [Hooks — Configuration](https://cursor.com/docs/hooks)

#### Agent-relevant hook events

Includes `sessionStart`, `beforeShellExecution` / `afterShellExecution`, `preToolUse` / `postToolUse`, `subagentStart` / `subagentStop`, `beforeReadFile`, `afterFileEdit`, `beforeSubmitPrompt`, `stop`, etc. Tab has separate hooks; `workspaceOpen` is IDE lifecycle.  
**Source:** [Hooks — Hook categories](https://cursor.com/docs/hooks)

#### Git / shell guardrails (kit-aligned)

**`beforeShellExecution`** — called before shell commands; returns `permission`: `allow` | `deny` | `ask`, with optional user/agent messages. Supports `matcher` against the command string. Default fail-open; `failClosed: true` for security-critical gates.  
**Source:** [Hooks — beforeShellExecution](https://cursor.com/docs/hooks)

Enterprise docs show blocking raw `git` usage via `beforeShellExecution` (deterministic enforcement, independent of LLM compliance).  
**Source:** [LLM Safety and Controls — Enforcement hooks](https://cursor.com/docs/enterprise/llm-safety-and-controls)

**`sessionStart`** — fire-and-forget; can inject `additional_context` or session `env` vars (passed to subsequent hooks). Does not block session creation. **Not available in Cloud Agents** (deferred).  
**Source:** [Hooks — sessionStart; Cloud agent support](https://cursor.com/docs/hooks)

**`subagentStart`** — control Task-tool / subagent execution (useful to gate parallel labor).  
**Source:** [Hooks — Hook categories](https://cursor.com/docs/hooks)

#### Cloud Agents

Project hooks in `.cursor/hooks.json` run in Cloud Agents once writable; supported hooks include `beforeShellExecution`, `afterShellExecution`, `beforeReadFile`, `afterFileEdit`, tool hooks, and lifecycle hooks. User-level `~/.cursor/hooks.json` is **not** available in cloud VMs.  
**Source:** [Hooks — Cloud agent support](https://cursor.com/docs/hooks); [Cloud Agents](https://cursor.com/docs/cloud-agent)

#### Kit mapping for Git guardrails

| Kit requirement | Portable layer | Cursor binding layer |
| --- | --- | --- |
| Clean worktree before work | `scripts/check-clean-worktree.sh` | Hook calls script on `beforeShellExecution` (e.g. matcher for `git commit`, `git checkout`, or kit `start-work.sh`) |
| Refuse dirty `start-work` | `scripts/start-work.sh` | Same — hook denies or routes to script; script remains canonical exit codes |
| Workstream preconditions | `scripts/check-workstream.sh` | `beforeShellExecution` matcher or `sessionStart` context injection listing active `work-id` |
| Verification / result SHA | `scripts/verify.sh`, `record-result.sh` | Optional `afterShellExecution` audit; not a substitute for scripts |

Hooks **wrap** kit scripts; they should not reimplement Git logic in hook-only form (keeps Codex/CLI portability).

---

### 5. Subagents — use sparingly in a thin binding

Subagents are delegated assistants with isolated context windows; Agent uses built-in **Explore**, **Bash**, and **Browser** subagents automatically.  
**Source:** [Subagents](https://cursor.com/docs/subagents)

Custom subagents live in `.cursor/agents/` (project) or `~/.cursor/agents/` (user); `.cursor/` takes precedence over `.claude/` / `.codex/` compat paths. Format: markdown + YAML frontmatter (`name`, `description`, `model`, `readonly`, `is_background`).  
**Source:** [Subagents — Custom subagents](https://cursor.com/docs/subagents)

Docs contrast subagents vs skills: subagents for long/multi-step/isolated work; skills for single-purpose repeatable actions.  
**Source:** [Subagents — When to use subagents](https://cursor.com/docs/subagents)

**Kit implication:** The kit’s **Engineering Agents** (`00`–`10`) are **Kit Protocol Files**, not a 1:1 `.cursor/agents/` tree. A thin binding should **not** clone eleven subagents (that would be a bespoke runtime). Optional: one readonly **verifier** or **research** subagent where Cursor isolation helps; stage contracts stay in `part-engineering/agents/`.

---

### 6. Commands — optional slash entry points

Commands are reusable prompts invoked with `/` in Agent chat; stored as markdown under **`.cursor/commands`**.  
**Sources:** [Customize Cursor — Commands](https://cursor.com/docs/customize-cursor); [Deeplinks — Command deeplinks](https://cursor.com/docs/reference/deeplinks)

Plugin reference: command files support `.md`, `.mdc`, `.markdown`, `.txt` with optional frontmatter (`name`, `description`).  
**Source:** [Plugins reference — Commands format](https://cursor.com/docs/reference/plugins)

Commands are **steering** (prompt packaging). Prefer commands that say “read `part-engineering/agents/06-implement.md` and run `scripts/check-workstream.sh`” rather than duplicating protocol text.

`/migrate-to-skills` can convert slash commands to skills with `disable-model-invocation: true`.  
**Source:** [Agent Skills — Migrating rules and commands to skills](https://cursor.com/docs/skills)

---

### 7. Worktrees — complementary isolation (not a kit substitute)

Cursor supports isolated Git checkouts via Agents Window worktrees, IDE `/worktree` and `/best-of-n`, CLI `-w` / `--worktree`, and `.cursor/worktrees.json` setup scripts (`setup-worktree`, OS-specific variants).  
**Sources:** [Worktrees](https://cursor.com/docs/configuration/worktrees); [Using Agent in CLI — CLI worktrees](https://cursor.com/docs/cli/using)

Machine settings `cursor.worktreeCleanupIntervalHours` and `cursor.worktreeMaxCount` control cleanup.  
**Source:** [Worktrees — Worktrees cleanup](https://cursor.com/docs/configuration/worktrees)

Kit convention remains `agent/<work-id>` branches via `start-work.sh`. Cursor worktrees add **runtime isolation**; the kit branch/work-id model adds **protocol identity and artifacts**. Use both consciously; do not replace `start-work.sh` with `/worktree` alone.

---

### 8. Plugins — defer for v1 binding

Cursor Plugins (`.cursor-plugin/plugin.json`) and Agent Plugins (`plugin.json`) bundle rules, skills, subagents, commands, hooks, MCP.  
**Sources:** [Plugins](https://cursor.com/docs/plugins); [Plugins reference](https://cursor.com/docs/reference/plugins)

Kit CONTEXT explicitly avoids assuming “Cursor plugin” as the distribution form unless decided later. For v1, ship binding **files in-repo** rather than a marketplace plugin.

---

## Recommended binding split

### Kit Protocol Files (portable — stay out of `.cursor/` except pointers)

| Artifact | Path | Why protocol, not Cursor config |
| --- | --- | --- |
| Agent stage contracts | `part-engineering/agents/00-explore.md` … `10-accept.md` | Runtime-agnostic labor definitions |
| Policies | `part-engineering/policies/*.md` | Authority/delegation/risk — not Cursor-specific |
| Templates | `part-engineering/templates/*` | Artifact schemas |
| Skill pins | `part-engineering/skills/manifest.yaml` | Dependency lockfile, not skill bodies |
| Skill prep script | `part-engineering/skills/prepare-skills.sh` | Portable install entry |
| Deterministic guardrails | `scripts/check-clean-worktree.sh`, `start-work.sh`, `check-workstream.sh`, `verify.sh`, `record-result.sh` | Enforceable without Cursor |
| Work artifacts | `work/<work-id>/`, `specs/` | Canonical engineering state |
| Root bootstrap | `AGENTS.md` (short) | Portable entry read by Cursor CLI and other agents; **points to** protocol files |

### Cursor-only config (thin binding layer)

```
.
├── AGENTS.md                          # Short: kit identity + context assembly order + “prepare skills from manifest”
├── .agents/
│   └── skills/                        # Prepared Community Skills (SKILL.md trees from manifest)
└── .cursor/
    ├── rules/
    │   └── starter-kit-bootstrap.mdc  # alwaysApply or intelligent: load policies + active work context
    │   └── workstream-scope.mdc       # globs: work/**, specs/** — cite stage contracts
    ├── hooks.json                     # beforeShellExecution → kit Git guardrails
    ├── hooks/
    │   └── git-guardrails.sh          # Thin wrapper: calls scripts/check-*.sh, returns deny/allow JSON
    ├── commands/                      # Optional: /start-work, /verify-workstream
    │   └── start-work.md
    └── worktrees.json                 # Optional: deps setup for isolated agent runs
```

#### Design rules for the thin layer

1. **`AGENTS.md` ≤ ~30 lines** — operational checklist only (per kit spec §34); link to `part-engineering/` rather than inlining policies.
2. **One bootstrap rule** — `alwaysApply: true` rule that encodes context assembly order (mirrors kit spec §20) and tells Agent to read relevant protocol files, not everything in repo.
3. **Hooks call scripts** — never duplicate clean-tree logic only in hooks; scripts remain testable without Cursor (`check-clean-worktree.sh` negative path is a kit acceptance test).
4. **Skills = Community Skills only** — prepare pinned skills into `.agents/skills/<name>/SKILL.md`; keep kit stage docs out of skill folders.
5. **No eleven subagents** — use kit protocol files + optional readonly subagent for review isolation if needed.
6. **Commands optional** — useful for human slash entry; stage truth stays in `part-engineering/agents/`.

#### Example hook wiring (conceptual)

```json
{
  "version": 1,
  "hooks": {
    "beforeShellExecution": [
      {
        "command": ".cursor/hooks/git-guardrails.sh",
        "matcher": "git (commit|push|checkout|merge|rebase|reset|stash)"
      }
    ],
    "sessionStart": [
      { "command": ".cursor/hooks/inject-workstream-context.sh" }
    ]
  }
}
```

Hook script invokes `scripts/check-clean-worktree.sh` or `scripts/check-workstream.sh` and maps exit codes to `{ "permission": "deny", ... }` per [Hooks — beforeShellExecution](https://cursor.com/docs/hooks).

---

## Open gaps

| Gap | Impact | Mitigation for kit |
| --- | --- | --- |
| **`AGENTS.md` vs `.cursor/rules` precedence** not documented when both exist at project root | Possible duplicate/conflicting instructions | Keep `AGENTS.md` minimal; put scoped triggers in one bootstrap `.mdc` rule; do not duplicate policy text |
| **No official “prepare skills from manifest” API** | Skill Preparation is kit-defined | Document agent steps in `AGENTS.md` + `prepare-skills.sh`; prepared output must conform to [Agent Skills](https://cursor.com/docs/skills) layout |
| **Cloud Agents: `sessionStart` unavailable** | Cannot inject workstream context at true session start in cloud | Rely on `AGENTS.md`, project rules, and `beforeShellExecution` hooks (supported in cloud) |
| **User hooks unavailable in Cloud Agents** | Personal guardrails don’t travel to cloud | Commit project-level `.cursor/hooks.json` for team/cloud parity |
| **Rules/hooks are not security boundaries alone** | LLM may attempt bypass | Keep kit shell scripts + CI as independent enforcement (aligns with kit principle §2.3) |
| **Commands lack a dedicated top-level doc page** | Format details scattered (Customize, Plugins reference, Deeplinks) | Follow plugin reference frontmatter; prefer commands that reference protocol files |
| **Worktrees vs kit `agent/<work-id>` branches** | Two isolation models | Document when to use Cursor worktree (experimental) vs kit `start-work.sh` (delegated workstream) |
| **Built-in Explore subagent vs kit `00 Explore`** | Name collision risk | Kit Explore = protocol stage + artifacts; Cursor Explore subagent = codebase search — distinguish in `AGENTS.md` |
| **`.cursorignore` not a security boundary** | Secrets may leak via shell/MCP | Do not rely on ignore files for policy; use hooks + filesystem permissions per [LLM Safety and Controls](https://cursor.com/docs/enterprise/llm-safety-and-controls) |

---

## Primary source index

| Topic | URL |
| --- | --- |
| Customize (component catalog) | https://cursor.com/docs/customize-cursor |
| Agent Skills | https://cursor.com/docs/skills |
| Rules & AGENTS.md | https://cursor.com/docs/rules |
| Hooks | https://cursor.com/docs/hooks |
| Subagents | https://cursor.com/docs/subagents |
| CLI (rules, worktrees) | https://cursor.com/docs/cli/using |
| CLI Changelog (skills discovery details) | https://cursor.com/docs/cli/changelog |
| Worktrees | https://cursor.com/docs/configuration/worktrees |
| Cloud Agents (hooks in cloud) | https://cursor.com/docs/cloud-agent |
| Cloud Agent best practices | https://cursor.com/docs/cloud-agent/best-practices |
| LLM safety & enforcement hooks | https://cursor.com/docs/enterprise/llm-safety-and-controls |
| Plugins | https://cursor.com/docs/plugins |
| Plugins reference (commands/skills layout) | https://cursor.com/docs/reference/plugins |
| Command deeplinks (`.cursor/commands`) | https://cursor.com/docs/reference/deeplinks |

---

*Research ticket output. Kit-internal definitions: [CONTEXT.md](../../CONTEXT.md), [ai-agent-starter-kit-spec.md](../../ai-agent-starter-kit-spec.md).*
