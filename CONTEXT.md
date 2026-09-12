# AI Engineering Starter Kit

Portable repository protocol for delegating engineering labor to AI agents while keeping human ownership of intent, policy, and acceptance. Cursor is the first-class runtime binding; the protocol stays copyable into ordinary software repos.

## Language

**Starter Kit**:
The portable repository protocol (agent instructions, policies, templates, scripts, modular docs/specs) that a developer copies into a software repo. It is not a multi-agent runtime product. The entire kit package lives under the branded root `_ask/` (including kit scripts, kit tests, and kit-author docs). Root adapter is `ask` + `AGENTS.md` + `.cursor/`. `ask` is the Agent Starter Kit dispatcher — the only root command; it is not a generic `scripts/` folder.
_Avoid_: agent platform, orchestration framework, agent OS, generic `engineering/` as the kit root

**Guide**:
The conceptual documentation of Division of Engineering Labor and engineering-system ownership. Shipped as multiple modular files under `_ask/guide/`, not one monolith and not under a consumer’s generic `docs/`.
_Avoid_: article (when referring to the shipped docs set), single guide file, root `docs/guide` as the shipped location

**Build Spec**:
The implementation contract for the Starter Kit. Shipped as multiple modular files under `_ask/spec/` that stay name-stable with the Guide.
_Avoid_: single spec file, implementation plan (that is a workstream Plan artifact), root `docs/spec` as the shipped location

**Engineering Agent**:
One of the numbered labor roles in the kit: `00 Explore` (foggy / R&D on-ramp) and `01 Grill` … `10 Accept` (Engineering Pipeline). Names `01`–`10` stay stable with the Guide; Explore is prefixed as `00` rather than renumbering the pipeline.
_Avoid_: bot, assistant (when referring to a kit role), subagent (unless meaning a Cursor runtime mechanism)

**Explore Phase**:
The first-class kit stage for foggy or R&D work: chart a shared map of decisions, research, and prototypes until the destination is clear enough to enter Grill→Spec. It produces decisions and clarity, not accepted product software by itself.
_Avoid_: stuffing R&D into Implement, treating chat exploration as canonical state

**Explore Map**:
The durable Explore artifact at `work/<work-id>/explore-map.md`, **only when 00 ran**. Canonical for consumers; may point at an optional tracker map. Must contain a non-empty `Handoff to Intent` before `01 Grill`. A real skip of 00 leaves no map.
_Avoid_: chat as the map, tracker-only Explore without the workstream file

**Grilling Expansion**:
Before a grilling round is eligible for resolution (“all ok” / accept recommendations), each open question must have been expanded enough that alternatives, tradeoffs, and failure modes are visible—not only a one-line A/B/C. If the human asks to expand, or the stakes are high, the agent re-issues the frontier with tables/scenarios before accepting a decision. This applies to kit `01 Grill` (and Explore grilling tickets), not only meta wayfinding.
_Avoid_: resolving on bare letter choices with no shared understanding of what A/B/C imply

**Engineering Pipeline**:
The post-clarity labor path: Grill → Spec → Spec Challenge → Plan → Implement → Review → Refactor → Verify → Accept (with Spec Change as interrupt). Entered only after Explore Phase has cleared the destination (or the human already had one).
_Avoid_: calling the whole kit “just 01–10” once Explore is in scope

**Workstream**:
An isolated unit of delegated work identified by a `work-id`, with its own branch, `work/<work-id>/` artifacts, and linked specification.
_Avoid_: ticket (unless meaning tracker issue), chat thread, session

**Intent Artifact**:
Clarified human What/Why for a Workstream (`work/<work-id>/intent.md`), not a raw request dump.
_Avoid_: prompt, user story (unless the project already uses that term for something else)

**Specification**:
The explicit engineering contract for a Workstream, with a lifecycle status (`PROPOSED` … `CURRENT`). Lived under `specs/`.
_Avoid_: plan, acceptance criteria alone (those are parts of it)

**Cursor Binding**:
How the Starter Kit is expressed inside Cursor. Includes root `ask`, short `AGENTS.md`, pointing bootstrap rules, mandatory `.cursor/hooks` wrapping kit scripts, prepared Community Skills, and **generated** `.cursor/` projections of stage contracts via `./ask sync` — so Cursor can honor stages without hand-maintained subagent SoT. Portable protocol remains under `_ask/`; anything Cursor must honor also exists under `.cursor/`.
_Avoid_: Cursor plugin (unless we later decide that is the distribution form), protocol-only “hope the model opens the file”, hand-maintained eleven Cursor agents as source of truth

**Skill Manifest**:
`_ask/skills/manifest.yaml` — pinned, reviewable references to external engineering methods. Entries name source (community/main skill repo or package), revision, and role. The consuming repo does not copy skill bodies in by default.
_Avoid_: latest, vendored skill tree, implicit skill pack

**Community Skill**:
A reusable engineering method published in a shared skill repository (npm-like: versioned, referenced, updatable), not authored per product repo. Discovery starts at the open directory [skills.sh](https://www.skills.sh/); install/prepare is done by agent-executable instruction (e.g. skills CLI), not by hand-copying skill bodies into the kit.
_Avoid_: copied skill, inlined prompt pack, latest from main, kit-vendored skill tree

**Skill Preparation**:
The agent-driven (or script-driven) act of installing Community Skills declared in the Skill Manifest into the runtime’s skill locations, at the pinned revision, so labor can proceed. The Starter Kit must instruct how to prepare; it must not require humans to manually vendor skill files.
_Avoid_: “just clone skills into the repo”, silent unpinned install

**Kit Protocol File**:
Portable kit-owned instruction or policy that defines this Starter Kit’s workflow (e.g. `_ask/agents/01-grill.md`, policies, templates). Distinct from a Community Skill: the kit ships these; skills are dependencies.
_Avoid_: calling protocol files “skills” when they are kit contracts

**Kit-owned path**:
Files the Starter Kit may refresh on upgrade (stock stage contracts, templates, guide/spec modules, stock scripts, root `ask`, generated `.cursor` projections). Consumers should not edit these if they want clean upgrades.
_Avoid_: editing stock `_ask/agents/0*.md` in place for local policy

**Consumer-owned path**:
Files upgrade must not overwrite by default: skill manifest, policies (or local policy tree), AGENTS local sections, `.cursor/rules/local/`, and `_ask/agents/*.local.md` stage overlays.
_Avoid_: “customize by forking the whole tree”

**Workflow guidance**:
Every session starts on-path. Artifacts are required to move forward; “skip” means skip extra approvals (one defaults-OK, then Accept). `/off-path` is **this chat only** — warn once and follow; do not persist. Policy: `_ask/policies/workflow.md`.
_Avoid_: locking Implement; a durable off-path git flag; re-asking bless on every stage

**Kit upgrade**:
Deliberate bump to a kit version/tag via `./ask upgrade --version <tag>`, refreshing kit-owned paths only, then prepare + sync. Distinct from Community Skill pin bumps in the manifest.
_Avoid_: blind pull of kit `main`, `skills update` as kit upgrade
