# Explore Map: Structured, Interactive Agentic Development Environment

## Destination

Make the handoff's product direction clear enough to own What/Why for a bounded next experiment in the starter kit. Establish which uncertainty that experiment resolves, its authority boundary, its representative workstream, and what evidence would justify continuing, revising, or abandoning it.

This destination is provisional until the human answers **Choose the first proof**. The broader product thesis is a development environment organized around intent, behavior, decisions, work, implementation, and evidence, with the developer directing and challenging construction.

## Notes

- Stage: **00 Explore — STILL_FOGGY**. Implementation has not started. Seeded Intent/Plan/Review/Accept files are templates, not approvals or prepared downstream artifacts.
- Original input: `/home/mohamad/Downloads/Handoff — Structured, Interactive Agentic Development Environment.md`; durable copy: [source handoff](source-handoff.md). Original SHA-256: `fbd82c2e7b1eddbffb4670616c104cc56b8ebe623ab20cf3429cf51a440674dd`. The copy adds only a final newline; its text is otherwise unchanged.
- Work branch: `agent/structured-agentic-environment`. Initial base was `develop` at `ed6fa62`; after the human clarified that completed harness-review belongs on both branches and main is latest, local `develop` was fast-forwarded to local `main` at `4a1967a`. This work branch then incorporated that baseline. No push occurred.
- `./ask prepare` completed for the existing explicit manifest pins. `./ask sync` completed. Pinned wayfinder and grilling guide decision work; the kit overrides tracker authority and exhaustive question expansion. This file is canonical; a tracker mirror is optional and has not been created.
- Extra skill proposed before decision questions: domain-modeling, to clarify requirement/scenario/evidence/authority terminology. Human choice is pending; it has not been added or invoked. Continue with existing pins unless accepted; accepted additions must receive an explicit repository pin before preparation.
- Human product decisions, source observations, and agent recommendations are recorded separately below. A recommendation is not a resolved decision.

## Tracker map (optional)

No tracker mirror. Continue from this file and its decision sections.

## Decisions so far

- **Run Explore** — the human explicitly invoked kit-00-explore with the handoff. Do not infer permission to implement the eventual environment.
- **Use the completed harness baseline** — the human confirmed harness-review is done and should be applied on main and develop, with main latest. Local branch reconciliation is complete; runtime locks were preserved.
- No experiment scope, architecture, schema, or product acceptance criteria have been approved yet.

## Direction supplied by the handoff

These are input commitments to carry into the discussion, rather than newly approved implementation requirements.

- One structured Engineering Model should support both machine use and human inspection. Markdown and UI are projections of that model.
- Definition belongs with its code revision. Evidence retains provenance and revision binding. Runtime activity has a separate lifecycle.
- Each fact has an authority: engineering definitions, actual code, executed test results, and runtime assignments need not share physical storage.
- Semantic mutation and independently runnable validation should protect model invariants, including broken references and duplicate identities.
- Progress should derive from inspectable evidence. A declared test link or passing process alone does not establish behavioral coverage.
- Human navigation centers on persistent engineering work. Human attention centers on consequential decisions and uncertainty.
- Prove value incrementally for both agents and developers. The handoff suggests one existing bounded workstream and a minimal human projection; it also offers a model-first phase sequence. Choosing how to balance these is still open.
- Persistence format, full object taxonomy, UI architecture, assertion mapping, merge semantics, orchestration, and authorization details remain undecided.

## Repository facts

Observed by reading committed source at baseline `4a1967a`; source inspection is not a new execution or a comparative usability result.

| Observation | Source | Implication for Explore |
| --- | --- | --- |
| Canonical criterion IDs and Given/When/Then already exist in JSON. | `specs/current/harness-review.json`, `_ask/docs/spec-test-traceability.md` | Assess reuse before defining a competing criterion registry. |
| Plans link cases to criteria, required test types, scenarios, expected assertions, runners, and source paths. | `.agents/ask/verification/traceability/coverage.py` | Traceability is an existing substrate, not a completely missing capability. |
| Completion reloads accepted contracts, recorded semantic review, source bindings, case outcomes, and execution logs for a candidate. | `.agents/ask/verification/traceability/completion.py`, `service.py` | A UI should preserve these authorities and reasons rather than infer success from links or arbitrary status fields. |
| Independent review assesses assertion adequacy and counterexamples; validation enforces structure and provenance. | `_ask/docs/spec-test-traceability.md` | A generic validator cannot prove that an assertion captures the developer's intended behavior. Keep that judgment visible. |
| The present runner supports explicit Python unittest cases and refuses unsupported evidence. | `.agents/ask/verification/traceability/coverage.py`, `cli.py` | A pilot can stay within current supported evidence; broader framework adapters would expand scope. |
| The existing workstream inventory reads refs and exposes artifact stages. | `_ask/scripts/status.sh` | Investigate how work-centric views extend existing inventory before inventing another runtime authority. |
| The earlier review refers to a companion decision-review note, but that note was not found in the inspected repository. | `work/harness-review/harness-reliability-review-handoff.md` | Use the supplied handoff as the available direction; do not invent details of the absent proposal. |

The current completion graph is narrower than the handoff's proposed Engineering Model. The inspected files do not establish a general feature/story/decision model, semantic edit interface, or interactive Control Room. These are candidate gaps, subject to the selected experiment.

### Coverage of the handoff's proposed phases

The human prompted an explicit check for already completed parts of the plan. The following maps existing source to the handoff's phase sequence; partial coverage does not imply the broader product goal is complete.

| Handoff phase | Already present | Remaining gap relevant to this direction |
| --- | --- | --- |
| Phase 1: Structured model and validation | Canonical JSON criteria, test-plan schemas, stable identities, reference/type validation, independently callable validation commands. | A broader model for intent/features/decisions and controlled semantic edits is not established by the existing traceability contract. Determine whether the pilot needs any of it. |
| Phase 2: Traceability | Criteria-to-test obligations, declared per-criterion assertions, independent assertion review, actual case outcomes, revision/digest provenance, and rejection of stale or incomplete evidence. | Fine-grained implementation/symbol links and selective semantic dependency invalidation remain open. Existing assertion review is not automatic proof of behavior. |
| Phase 3: Human projection | CLI inventory and machine-readable per-criterion completion reports provide source material. | No interactive scenario/evidence inspection interface was found in the inspected application/source paths. |
| Phase 4: Attention and interaction | Defaults-OK, semantic-change escalation, and independent challenge/review already encode some human-authority rules. | No work-centric attention queue or predict/reveal-style interaction was found. R3-R5 comparative pilots are explicitly outside the accepted traceability feature. |
| Phase 5: Multi-agent Control Room | TaskGraph, coordinator/task roles, single-writer integration, state locks, and candidate-bound task verification provide a runtime foundation. | Richer orchestration and human work-centric runtime views remain unproven; current single-writer rules must be respected. |

**Agent inference:** the strongest new experiment may connect existing machine evidence to meaningful human supervision. Starting by rebuilding generic criteria/test validation would duplicate completed work. This inference informs the recommendation; the human still chooses the next proof.

## Decision frontier

The current human frontier contains **Choose the first proof**. Other precisely stated decisions are blocked until its answer narrows the destination.

| Decision | Blocking decision | Resolution required |
| --- | --- | --- |
| [Choose the first proof](#choose-the-first-proof) | None | What uncertainty must the next experiment settle? |
| Choose the representative workstream | Choose the first proof | Which existing bounded workstream exposes both useful evidence and realistic human judgments? |
| Set the pilot authority boundary | Choose the first proof | Is the pilot isolated from normal gates, or does it replace a defined part of the existing workflow? |
| Define the observable success and failure | Choose the representative workstream; Set the pilot authority boundary | What demonstrates agent reliability and developer supervision benefits, and what would count as failure? |

### Choose the first proof

Status: open; human decision. No answer has been inferred.

**Question:** What should the first experiment primarily prove?

**A — A small complete supervision loop (recommended).** Use one existing workstream to connect a small set of behaviors to real implementation, tests, revision-bound evidence, and unresolved decisions. Present them through a minimal interactive view so the developer can inspect a claim, challenge it, and understand the consequence. Reuse current traceability wherever it fits. This can test both benefits in the handoff, but it needs enough model and UI work to make the loop real. A polished view with no trustworthy evidence would fail.

**B — The missing domain model first.** Extend beyond the completed criterion/test contracts toward explicit work, decisions, assumptions, and semantic mutation, with only the necessary new invariants and textual projections initially. This follows the handoff's Phase 1 ordering without rebuilding existing validation. It can reveal relationship and authority problems early, but leaves the central claim about the developer's experience untested until a later experiment.

**C — The human interaction first.** Explore how the developer navigates work, inspects evidence, and answers consequential questions using an explicitly disposable interactive prototype. Existing records can supply examples; any mocked facts must be visibly identified. This is useful if the biggest uncertainty is whether technical direction feels engaging and effective, but it does not establish trustworthy model mutation or machine hardening.

**Recommendation:** A, bounded tightly enough to demonstrate one inspection-and-challenge journey. The repository already contains substantial traceability machinery, making the connection between that evidence and human judgment a plausible next uncertainty to test. This is a recommendation, not a commitment to skip needed model validation.

**I'll assume unless corrected:** local single-developer use in this repository for the first experiment; preserve Git and existing evidence/approval authority; defer database and multi-host infrastructure; defer framework and persistence choices until the experiment's purpose is chosen. These are reversible scope defaults and do not resolve the open decision.

## Not yet specified

- The exact minimum domain objects and whether Feature/Story/Scenario adds useful meaning beyond existing criteria and test scenarios.
- How a human challenge becomes an attributable decision or proposed definition change, and which existing semantic-change gates apply.
- The smallest scenario-to-implementation reference that is inspectable without overstating proof of satisfaction.
- Which changes invalidate which evidence: whole revision checks are available today; selective semantic dependency invalidation is a separate question.
- How an attention item explains its cause and becomes resolved without repeated approvals.
- What a fair comparison with the current Markdown/CLI workflow looks like, including correctness of answers and human effort. No benefit has been measured.
- Which unknowns need research or a disposable prototype after the first decision. No prototype has been commissioned yet.

## Out of scope

For current Explore labor: production implementation, changing completion/acceptance gates, migrating all existing workstreams, and choosing the full platform architecture. The eventual product may include broader capabilities; they are not authorized deliverables of this stage.

Candidate boundaries for a first pilot, pending the scope decision: multi-host orchestration, authentication infrastructure, production deployment, a graph database, broad test-runner support, points/badges, and a replacement IDE. Revisit only if essential to the owned experiment.

## Handoff to Intent

**NOT READY — STILL_FOGGY.** The broad Why is meaningful human technical direction alongside accountable agent construction. The bounded What remains unresolved: choose the first proof, representative workstream, authority boundary, and observable success/failure before entering 01 Grill.

Continue with **Choose the first proof** above. Once its dependent decisions are resolved, replace this provisional handoff with the human-owned destination, non-goals, decisions and evidence pointers. A non-empty section is not itself evidence that the destination is clear.
