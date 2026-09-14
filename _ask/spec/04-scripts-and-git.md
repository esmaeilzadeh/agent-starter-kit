# Git Guardrails, Scripts, and Workstreams

# 22.9 Root dispatcher (`ask`)

Humans and agents invoke kit operations via a single root command named `ask` (Agent Starter Kit). Implementation stays under `_ask/scripts/` and `_ask/skills/prepare-skills.sh`. Do not introduce a generic root `scripts/` for kit commands.

Provide:

```text
./ask <command> [args]
```

Mapped commands:

```text
./ask check-clean              → _ask/scripts/check-clean-worktree.sh
./ask start-work <work-id>     → _ask/scripts/start-work.sh
./ask check-workstream <id>    → _ask/scripts/check-workstream.sh
./ask status [--work-id id] [--json] [--later-only] [--work-only]  → _ask/scripts/status.sh
./ask verify [--work-id id]       → _ask/scripts/verify.sh
./ask openspec-archive <id>       → _ask/scripts/openspec-archive.sh
./ask record-result …          → _ask/scripts/record-result.sh
./ask record-run …             → _ask/scripts/record-run.sh
./ask sync                     → _ask/scripts/sync-cursor-binding.sh
./ask install <repo>           → _ask/scripts/install-kit.sh
./ask upgrade --version <tag>  → _ask/scripts/upgrade-kit.sh
./ask prepare                  → _ask/skills/prepare-skills.sh
./ask setup                    → _ask/scripts/setup.sh   # human-only; refuse without a TTY
```

Unknown command names that match an executable `_ask/scripts/<name>.sh` are exec'd. `install-kit` / `upgrade-kit` copy and refresh root `ask` as kit-owned adapter alongside `AGENTS.md` and `.cursor/`.

## 22.10 Human-only setup (`./ask setup`)

Implementation: `_ask/scripts/setup.sh`. **Agents must not run it.** Refuse when stdin or stdout is not a TTY (except `--help`). `./ask install` stays non-interactive; setup may call install when the human gives another repo path.

Tracker menu: `gitlab` | `github` | `jira` | `none`. `none` skips URL/key; the next action is go back and choose again.

Prefills (all editable): Jira `https://jira.partcorp.ir/` (labeled default, can clear); GitHub `https://github.com/` or `git remote`; GitLab `https://gitlab.com/`.

Binds that tracker’s proper tooling:

- GitLab: official MCP `https://<host>/api/v4/mcp` + browser OAuth. URL only.
- GitHub: official hosted MCP + `GITHUB_TOKEN` via `${env:GITHUB_TOKEN}`.
- Jira: `mcp-atlassian` + `JIRA_URL` / `JIRA_PERSONAL_TOKEN` via env.

Writes gitignored `.ask.env` from committed `.ask.env.example` (placeholders only). Writes gitignored `.ask/tracker-context.md` (current epic/story). Writes `.ask/tracker.md` (type + public URL; safe to commit). Merges MCP stubs into `~/.cursor/mcp.json` using `${env:...}` only — never write token values into that file.

Memory menu: `codebase-memory-mcp` (default `${userHome}/.local/bin/codebase-memory-mcp`), skip, or custom command.

After those stages, setup runs `_ask/scripts/ensure-openspec.sh`: install the pin in `_ask/openspec-pin.yaml` to `$HOME/.local` when `node` and `npm` are on `PATH`; skip with a warning when they are missing or the install fails. OpenSpec skip/warn does not itself fail setup. `./ask install` and `askit` overlay/self-install do not install OpenSpec.

# 23. Git guardrails


## 23.0 Worktree, branch, and commit policy

Canonical policy file:

```text
_ask/policies/worktree.md
```

Hard rules:

```text
never start labor on an unclean working tree
if dirty: stop and grill the human on uncommitted/untracked paths
do not stash/reset/absorb changes silently
one plan / workstream → one dedicated branch (agent/<work-id>)
that branch is the safety boundary — stepwise commits stay off main/master
commit after each meaningful step on the workstream branch
do not wait for the human to ask before committing (kit overrides “only commit when asked”)
do not run multiple related branches in parallel when they modify shared files
```

`./ask check-clean` is the deterministic gate (`check-clean-worktree.sh`); agent grilling is required whenever it fails.

## 23.1 `./ask check-clean` (`check-clean-worktree.sh`)

Behavior:

```text
exit 0 → working tree clean
exit non-zero → working tree dirty
```

It must not stash, reset, or absorb user changes.

## 23.2 `./ask start-work <work-id>` (`start-work.sh`)

Behavior:

```text
1. require clean working tree
2. verify Git repository
3. identify default/main branch
4. create or switch to dedicated work branch
5. create work/<work-id>/ artifacts
6. print current HEAD SHA
7. print active branch
```

Default branch convention:

```text
agent/<work-id>
```

The script must refuse to silently proceed when unrelated local changes exist.

## 23.3 `./ask check-workstream` (`check-workstream.sh`)

Before delegated work, verify:

```text
branch is dedicated to current work-id
working tree is clean or changes are explicitly attributable to current work
accepted spec exists
plan exists
```

Exit non-zero means the **default path is incomplete**, not that labor is forbidden (`_ask/policies/workflow.md`). On-path: prepare the missing artifact. Dirty tree remains a hard safety failure (via `check-clean`).

A workstream is an OpenSpec pilot when `work/<id>/intent.md` matches `^Engine:\s*openspec\s*$`. For that marker, `check-workstream` requires a matching OpenSpec change and targeted `validate <id> --strict` / `status --change <id>` via `_ask/scripts/openspec_cli.py`. Non-pilots keep the spec-and-plan checks above. `--all` is not a gate input.

This can be called by agent instructions before implementation/review/refactor.

## 23.4 `./ask status` (`status.sh`)

Board of kit workstreams **without checking out** other branches:

```text
live = local refs/heads/agent/<work-id> that are not fully merged into the default branch
archive = work/<work-id>/ on the default branch with no unmerged agent/<work-id>
(keeping a leftover agent/* after merge does not keep the workstream “live”)
```

`work/` is branch-local; do not treat the current checkout as the global inventory. Do not write a committed `work/INDEX.md`.

It infers a furthest stage from filled artifacts on that ref (`seeded` … `explored` … `intent` … `planned` … `reviewed` … `recorded` … `accepted`). Flags: `--work-id`, `--json`, `--later-only`, `--work-only`.

Live rows may include a **warning** `code-without-plan` when the branch changed files outside `work/<id>/` and `specs/` before a plan exists. That is guidance (`_ask/policies/workflow.md`), not a failure. For a marked OpenSpec pilot, `openspec/changes/<id>/` (and repo-level `openspec/config.yaml` / `openspec/specs/`) count as recognized prefixes. Meaningful OpenSpec `design.md` or `tasks.md` counts as planned even when kit `plan.md` is a pointer. Current-checkout pilots read targeted OpenSpec CLI state (`status --change <id>`); other live refs use `git show`. Do not check out another branch. Surfaced CLI `nextSteps` are relabeled to kit commands.

After Accept, merge the workstream branch so `main`/`master` becomes the archive.

`.later/` cards are not live. Default `./ask status` prints them as a second block from the current checkout (skip `README.md`). `--later-only` / `--work-only` print one inventory. `--work-id` filters workstreams and omits later. No later-inbox subcommand and no issue-tracker sync.

## 23.5 Session-only `/off-path`

Every new Cursor session starts **on-path**. `/off-path` switches **this chat only**. Warn once, then follow.

Do not write `work/*/kit-path`, flip intent, or add a repo flag. There is no `/on-path` command and no durable off-path flag.

Source: `_ask/cursor-commands/off-path.md`. `./ask sync` copies it to `.cursor/commands/off-path.md`. Install/upgrade treat `_ask/cursor-commands/` as kit-owned.

On-path, artifacts stay required on `01`–`10`. Skip means skip extra *approvals* (one defaults-OK, then Accept). Missing artifacts while still on-path: prepare from defaults, confirm once, continue. Policy: `_ask/policies/workflow.md`.

---

# 24. Verification script

Provide:

```text
./ask verify [--work-id <id>]
```

Implementation: `_ask/scripts/verify.sh`.

It should:

```text
refuse a dirty tree
detect project/package manager where possible
read project-specific configuration
run configured mandatory checks
fail on mandatory failures
print exact commit SHA
emit machine-readable verification output
with --work-id: write work/<id>/verification.json; marked pilots also run targeted strict OpenSpec validation
```

Do not hard-code NestJS, Node, Python, Rust, or any other specific technology into the core.

Provide extension/configuration points for the consuming repository.

## 24.1 `./ask openspec-archive <work-id>` (`openspec-archive.sh`)

Kit-mediated OpenSpec archive. Refuses unless `work/<id>/acceptance.md` contains an accepted commit SHA. Then runs the pinned `openspec archive`. Direct CLI archive remains possible; `check-workstream` / `status` / `verify` detect archive without Accept SHA and fail.

`status` `life: archived` is a different word (work-id on the default branch, no unmerged `agent/*`).

---

# 25. Result recording script

Provide:

```text
./ask record-result …
```

Implementation: `_ask/scripts/record-result.sh`. It accepts a result file or flags (`--work-id`, `--commit-sha`, `--result`).

It should validate or inject:

```text
current commit SHA
work ID
spec reference
verification reference
```

It must refuse to record a result when no exact commit SHA can be obtained.

A result such as:

```text
"new version is faster"
```

is not valid without an identifiable code state.

## 25.1 Experiment run recording (`./ask record-run`)

Workstream Accept stays on `record-result`. Experiment / eval runs use a separate command:

```text
./ask record-run --run-id <id> --commit-sha <sha> --metric <value>
```

Implementation: `_ask/scripts/record-run.sh`. Optional: `--notes`, `--out` (default `results/<run-id>`).

Refuses: missing SHA; dirty tree; SHA ≠ `HEAD`; missing `config.yaml` in the run dir.

Writes: `run_manifest.json` (`eval-run-meta/v1`), `summary.json` (metric + `run_meta`), and a row in `results/RUN_REGISTRY.md` citing path + SHA + metric.

Product trainers or viewers (for example a demo MLP) are not kit protocol. They may call `record-run`; they do not replace it.

---

# 26. Failure convergence

The starter kit must protect against non-converging autonomous loops.

Example:

```text
Review A
→ Refactor
→ Review A
→ Refactor
→ Review A
```

After a configurable number of unsuccessful repair cycles, stop and escalate.

A conservative default is:

```text
2–3 unsuccessful repair cycles
```

Do not treat unlimited retry as free labor.

Retries consume:

```text
compute
latency
human attention
risk budget
```

---

# 27. Conflict resolution

The policy should define precedence among competing constraints.

Suggested starting point:

```text
explicit human requirement
    > domain invariant
    > security/safety constraint
    > accepted specification
    > correctness
    > reliability
    > performance
    > maintainability/style
```

This is a template, not a universal law.

The project must customize it.

Model majority must not be the default authority.

---

# 28. Acceptance debt visibility

The starter kit should be able to expose at least a lightweight signal when work has accumulated without sufficient evidence.

A simple implementation may track:

```text
work items completed
verification records present
acceptance decisions present
unresolved high-risk findings
```

The kit does not need a complex dashboard in v1.

It must at least make it possible to identify:

```text
engineering output without corresponding evidence
```

---

# 29. Provenance and state storage boundaries

The starter kit must distinguish three classes of data.

## 29.1 Durable engineering state

Keep in repository/version control when appropriate:

```text
code
specs
project-specific rules
policies
decisions
skill manifest
acceptance artifacts
verification references
```

## 29.2 Compact execution/provenance records

Keep as repository artifacts or external result records:

```text
run ID
commit SHA
spec reference
policy/skill references
verification ID
result ID
```

## 29.3 Raw execution telemetry

Do not store by default:

```text
full prompts
full context dumps
all tokens
every tool call
all retry transcripts
```

Store those separately only when an explicit audit/security/debugging requirement exists.

---

# 30. Workstream directory convention

For a task `cancel-order`:

```text
work/cancel-order/
├── explore-map.md       # only when Explore ran
├── intent.md
├── spec-challenge.md
├── spec-change.md      # only when needed
├── plan.md
├── review.md
├── verification.json
└── acceptance.md
```

Canonical spec proposal:

```text
specs/proposals/cancel-order.md
```

Canonical current spec after the required lifecycle:

```text
specs/current/cancel-order.md
```

Branch:

```text
agent/cancel-order
```

## 30.1 Mid-work later inbox

When a new job appears during a running workstream, park it — do not start a second live `agent/*` in the same session unless the human explicitly sequences another job.

```text
.later/<slug>.md          # gitignored card (not live)
.later/README.md          # committed; explains the inbox
_ask/templates/later-work.md
```

`.gitignore` ignores `.later/*` except `README.md`. Cards are not committed on the active job’s branch. Start later in a new session with `./ask start-work <new-work-id>`. `./ask status` lists parked cards as a later block from the checkout (`--later-only` / `--work-only`; `--work-id` omits later). No later-inbox subcommand and no issue-tracker sync.

`AGENTS.md` and `work/README.md` tell agents to park here.

---
