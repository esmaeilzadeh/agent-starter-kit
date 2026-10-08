# Handoff: Codex workflow parity

## Objective

Continue `inner-loop-hardening` so Codex offers the same ASK 00–10 workflow as
Cursor through Codex-native repository skills and project subagents.

Behavioral parity means the same stage contracts, gates, artifacts, local
overlays, model resolution, and human approval boundaries. It does not require
Codex to accept Cursor's literal `/00-explore` through `/10-accept` spellings.

## Starting state

- Repository: `agent-starter-kit`
- Branch: `agent/inner-loop-hardening`
- Expected starting commit: resolve and record the actual HEAD before labor;
  this handoff itself may be a later commit than `78f541a`.
- Worktree must pass `./ask check-clean` before labor.
- The workstream is already reviewed. Its accepted spec is
  `specs/current/inner-loop-hardening.md`.
- Existing `work/inner-loop-hardening/spec-change.md` records an older accepted
  change. Preserve it; create a dated or otherwise distinct new change artifact.
- `./ask sync` currently generates:
  - `.cursor/skills/kit-*` and `.cursor/commands/*`;
  - `.cursor/agents/*`, `.claude/agents/*`, `.codex/agents/*.toml`, and
    `.opencode/agents/*`.
- Missing Codex surface: checked-in ASK stage skills discoverable from
  `.agents/skills/`.
- `.agents/skills/` is currently also the prepared Community Skill store and is
  broadly ignored, so ownership and ignore rules need an explicit design.

## Confirmed human decision

Implement behavioral parity using Codex-native skills:

- expose `kit-00-explore` through `kit-10-accept` as repository-local skills;
- preserve generated `.codex/agents/*.toml` stage subagents;
- make the Codex skills discoverable in Codex's skill selector/slash menu and
  explicitly invocable as `$kit-<stage>`;
- retain the canonical stage source at `.agents/ask/stages/`;
- generate projections; do not introduce a second hand-maintained protocol;
- do not promise unsupported literal Cursor slash-command names.

## Authoritative product facts

Revalidate these against current official OpenAI documentation if the work is
resumed later:

- Codex scans repository skills under `$REPO_ROOT/.agents/skills`.
- Project-scoped custom agents live under `.codex/agents/` and require `name`,
  `description`, and `developer_instructions`.
- Enabled skills appear in the slash-command list and are explicitly invoked
  with `$`.

Sources consulted 2026-10-07:

- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/subagents
- https://learn.chatgpt.com/docs/reference/slash-commands

## Required sequence

1. Run `./ask check-clean`. Stop and grill the human on every dirty path.
2. Read `AGENTS.md`, `_ask/policies/`, and
   `.agents/ask/stages/04-spec-change.md`.
3. Run `./ask prepare`; treat network failure as explicit evidence, not success.
   Run `./ask sync` after preparation.
4. Create a new 04 Spec Change proposal. Preserve the current accepted spec
   until the human approves the proposal.
5. The proposal must define the ownership boundary between generated ASK stage
   skills and prepared Community Skills under `.agents/skills/`, including
   install/upgrade and `.gitignore` behavior.
6. Ask for the required Spec Change confirmation. Do not implement before it.
7. After confirmation, update the canonical spec and plan/task graph rather
   than editing reviewed acceptance criteria silently.
8. Implement test-first. Capture a failing parity test before changing the
   generator, then capture the passing result.
9. Run `./ask sync`; generated outputs must be deterministic and leave the
   worktree clean after committed projections are current.
10. Commit every meaningful step on `agent/inner-loop-hardening`.
11. Run the required Review, Refactor, Verify, result-recording, and human
    Accept stages. Do not claim completion from generator tests alone.

## Proposed acceptance criteria for the Spec Change

- `./ask sync` emits eleven Codex-discoverable `kit-*` stage skills from
  `.agents/ask/stages/`, with any supported local stage overlay applied.
- Cursor and Codex stage skills resolve to the same canonical stage body.
- Codex skill metadata is concise, unique, and valid (`name`, `description`).
- Generated ASK skills can be checked in while prepared Community Skills remain
  generated dependencies with deliberate ownership and upgrade behavior.
- Install and upgrade flows preserve consumer-owned Community Skills and
  regenerate kit-owned stage projections safely.
- `.codex/agents/*.toml` remains generated and contains the required Codex
  custom-agent fields.
- Tests cover all eleven stages, stale-output cleanup, overlays, ignore rules,
  install/upgrade behavior, and idempotent sync.
- Documentation explains Cursor invocation and Codex `$kit-*` invocation
  without claiming identical UI syntax.
- Existing workflow, dirty-tree, branch, verification, and Accept gates remain
  unchanged.

## Likely implementation seam

Keep `.agents/ask/stages/` as the single source. Extend the binding generator
behind one projection interface that renders runtime-native outputs. Avoid
duplicating stage bodies in a new Codex-only source tree.

The hardest boundary is `.agents/skills/`: it is both Codex's official
repository-skill location and this kit's prepared Community Skill location.
Choose and specify one deterministic ownership convention before coding, such
as a reserved `kit-*` namespace plus selective ignore rules. Tests must prove
that sync neither deletes nor overwrites unrelated prepared skills.

## Completion evidence

The next system is done only when it can provide:

- approved Spec Change artifact and updated canonical spec/plan;
- RED and GREEN commands with outputs for Codex skill parity;
- commits for each meaningful step;
- generated-file/idempotence evidence;
- Review verdict;
- `./ask verify` result tied to the verified commit SHA;
- `./ask record-result` output;
- a human decision at 10 Accept.
