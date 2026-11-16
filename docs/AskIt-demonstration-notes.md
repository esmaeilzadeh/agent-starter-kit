# AskIt — 90-minute presentation and facilitator guide

40 slides · exactly 90 scheduled minutes · developer audience · explanation, a real repository case study, exercises and Q&A.

This replaces the earlier short walkthrough. Time windows appear on every slide and in PowerPoint speaker notes. Durations are facilitation targets, not a guarantee of live execution time. Repository sources were inspected on 2026-11-06; source HEAD was `8d96ffd`, with unrelated local installation/test edits left untouched.

## Session outcomes

Participants should be able to route bug/feature/mixed requests, find canonical artifacts, explain human checkpoints, trace a measured claim to its source, recognize stale review evidence, and distinguish technical outcomes from acceptance authority.

## Run of show

| Time | Section | Minutes | Slides |
| --- | --- | ---: | --- |
| 00–10 | Foundations | 10 | 1–5 |
| 10–20 | Repository tour | 10 | 6–10 |
| 20–32 | Route and intent | 12 | 11–16 |
| 32–44 | Contract and plan | 12 | 17–22 |
| 44–66 | Real case study | 22 | 23–31 |
| 66–76 | Guardrails and recovery | 10 | 32–35 |
| 76–83 | Evidence and adoption | 7 | 36–38 |
| 83–88 | Questions | 5 | 39–39 |
| 88–90 | Final reconstruction | 2 | 40–40 |

## Central case evidence index

All paths are relative to the repository. Numerical slides read their totals from these actual JSON records.

| Case step | Evidence |
| --- | --- |
| Goal and constraints | `work/shorter-hashes/intent.md` |
| First failed measurement | `work/shorter-hashes/benchmark/results/fab05ca/report.json` |
| Withheld approval | `work/shorter-hashes/final-verification.json` |
| Diagnosis and authorized redesign | `work/shorter-hashes/projection-redesign-authorization.md` |
| Final accepted-candidate replay | `work/shorter-hashes/benchmark/results/direct-acceptance/report.json` |
| Reviews, checks and authority | `work/shorter-hashes/direct-acceptance.json`, `review.md`, `acceptance.md` |
| Preserved failed historical result | `work/shorter-hashes/result.json` |

The final replay records candidate `36b06f3bfa846e6d168a74ebb57aaf8c9fa62a95`, baseline `9a3d25d035baafc23508f242020d46fae7ff5b14`, tiktoken `0.12.0` with `cl100k_base`, three equivalent-evidence journeys and 60 byte-identical retained outputs. Tokens fell 14.58%; JSON bytes fell 21.25%; non-JSON bytes rose 23.86%. No benchmark or historical test suite was rerun to produce this deck.

## Preparation before the audience arrives

- For the central case, use a read-only repository browser at source revision `8d96ffd` or saved offline views of the case evidence index. No training dependencies or benchmark rerun are needed for the 22-minute retrospective.
- Prepare tabs for the actual intent, failed report, diagnosis/authorization, final report, direct-acceptance record, review and acceptance. Keep the original commits, dates, identities and failed outcomes visible.
- Use a disposable consumer/demo repository for the short clean-tree guard demonstration. It should begin clean. Create and remove only the scratch file you own; leave user edits untouched.
- If doing the optional two-moons follow-up outside the 90-minute session, install its dependencies and prepare the genuine workstream authorizations beforehand. Rehearse in a fresh disposable checkpoint, preserve actual evidence, and do not reset completed history just to replay it.
- The kit remains disabled while editing AskIt. If enabling dogfooding, first record a separate frozen copy location and exact commit. Agents must not run the human-only `./ask setup` wizard.
- Use a visible clock and a file browser. Save an offline PDF and local evidence views so the session can proceed without network access.

## Pacing and recovery

The 90 minutes include audience work and five minutes of Q&A; there is no separate break. The real case is `shorter-hashes`, traced through its actual intent, failed measurement, redesign authorization, accepted-candidate replay and direct acceptance. Its normal kit completion remained unestablished; explain the self-development exception explicitly. Announce any venue-required break and reduce or reschedule content explicitly. The recorded case study occupies 44–66. The optional two-moons experiment is follow-up material in this guide and adds time if executed; do not add it to the scheduled 90 minutes without replacing another segment.

At 44 minutes, open the shorter-hashes evidence records in a file browser or the prepared offline screenshots. Limit unexpected setup/debugging to 60 seconds, then use saved actual artifacts. At 66 minutes, move to guardrails even if the case discussion has more questions; save them for Q&A. At 83 minutes, start Q&A; at 88 minutes, use the final reconstruction. If behind, shorten presenter explanation and case file-browsing time while keeping the exercise debriefs and final distinction between demonstrated and unexecuted claims.

For the central case, inspect saved records without rerunning benchmarks or modifying historical state. If the optional live checks fail, describe the failure and use the saved walkthrough. Never record a passing result to preserve the timetable. If no saved executed artifacts exist, label the segment as a narrated command walkthrough and avoid showing invented outputs.

## Complete experiment sequence

Optional two-moons follow-up, outside the 90-minute schedule. Prepare a disposable consumer repo with the shipped trainer and requirements, develop, configured Git identity, and genuinely approved intent plus reviewed contracts. Agents must not run the human-only setup wizard.


Run this block after those prerequisites, on `agent/demo-moons-run`, from a clean tree. It uses new run IDs; existing run directories or registry IDs must not be overwritten. The extra commit after training preserves the generated output and satisfies the dirty-tree guard. The source recorded by `record-run` is that output-bearing HEAD.

```bash
set -euo pipefail
./ask check-clean
for variant in narrow wide; do
  run_id="moons-$variant"
  hidden=8
  if [ "$variant" = wide ]; then hidden=32; fi
  test ! -e "results/$run_id"
  mkdir -p "results/$run_id"
  cat > "results/$run_id/config.yaml" <<YAML
seed: 0
n_samples: 200
noise: 0.25
hidden_layer_sizes: [$hidden]
learning_rate_init: 0.01
max_iter: 400
YAML
  git add "results/$run_id/config.yaml"
  git commit -m "Experiment $run_id: hidden=$hidden"
  ./ask check-clean
  python3 scripts/train_moons.py --run-id "$run_id"
  git add "results/$run_id/train_output.json"
  git commit -m "Capture $run_id training output"
  metric=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["accuracy"])' "results/$run_id/train_output.json")
  ./ask record-run --run-id "$run_id" \
    --commit-sha "$(git rev-parse HEAD)" --metric "$metric"
  git add results/
  git commit -m "Record $run_id provenance"
done
```

Inspect `results/RUN_REGISTRY.md`, then use the actual numeric reference:

```bash
./ask refs show repository-runs/run/<actual-number>@1 --integrity
```

Replace the placeholder before running. Source bindings live in `results/references/integrity.json`. Numeric references are backed by Git authority refs; copying a JSON manifest alone is not a complete provenance transfer. The loop above is a prepared demonstration sequence; it was not executed while creating this deck.




## Closing command reference

Run completion commands only for a real, prepared workstream with valid current evidence. These commands do not replace missing contract review, execution records or human approval.

```bash
./ask verify
./ask traceability check-completion demo-moons-run
./ask check-workstream demo-moons-run --acceptance
./ask record-result --work-id demo-moons-run \
  --commit-sha "$(git rev-parse HEAD)" --result pass
```

Prepare `acceptance.md` and `context-audit.md`, cite evidence and commit identity, and obtain the required submitted acceptance decision. A failed check must be resolved or reported, never relabeled as pass.

## Slide-by-slide facilitation notes

### 01 — Delegate work. Keep the judgment.

TIME: 00:00–02:00 (2 minutes)

EXPLAIN
Introduce AskIt as the AI Engineering Starter Kit. The session mixes explanation, exercises and a real case study of shorter-hashes. A teammate should be able to reconstruct the purpose, exact source and evidence without reading the original chat. Ask for one example of an engineering handoff that was hard to reconstruct.

FACILITATE
Use the first minute to introduce the outcome. In the second minute, take one brief example of a handoff that was hard to reconstruct.

DEBRIEF / ANSWER KEY
We will judge the demonstration by reconstructability, rather than a model score or the volume of generated code.

Repository sources: README.md; CONTEXT.md

### 02 — The next 90 minutes

TIME: 02:00–04:00 (2 minutes)

EXPLAIN
Explain the timed agenda: foundations and repository tour, routing and contract preparation, a 22-minute real repository case, guardrail exercises and the evidence handoff. The central case is a retrospective of actual saved records. It does not require a live training run; the two-moons experiment is an optional follow-up in the presenter guide.

FACILITATE
One minute: show the time blocks. One minute: introduce the case and clarify which activities are exercises, recorded evidence inspection or optional demonstrations.

DEBRIEF / ANSWER KEY
At minute 90, participants should be able to locate the intent, source identity, measured outcomes, review limits and acceptance authority.

Repository sources: _ask/docs/demo/end-to-end-plan.md

### 03 — A useful result needs a durable story.

TIME: 04:00–06:00 (2 minutes)

EXPLAIN
Use a hypothetical agent message: “I improved the model.” Ask what another engineer needs before citing it. Explain that chat contains useful working context but the kit gives key decisions and evidence durable repository locations. No hypothetical score should be presented as an actual measured result.

FACILITATE
Allow 30 seconds of individual thought, take two answers in 45 seconds, then connect them to the three cards.

DEBRIEF / ANSWER KEY
Intent, source identity and acceptance evidence are separate facts; one cannot substitute for another.

Repository sources: README.md; _ask/docs/demo/end-to-end-plan.md

### 04 — The human owns intent and acceptance.

TIME: 06:00–08:00 (2 minutes)

EXPLAIN
Explain the division of engineering labor. Autonomy works inside an authorized scope. Routine implementation and review corrections can proceed without a new approval at every step; changes to intent, invariants or acceptance need the appropriate decision. Ownership remains even when execution is delegated.

FACILITATE
Ask participants to identify which role decides whether a larger model is worth pursuing. Use their answer to separate a product decision from an implementation choice.

DEBRIEF / ANSWER KEY
The agent may propose a change; the human owns the consequential What and Why decision.

Repository sources: README.md; _ask/policies/delegation.md

### 05 — The numbered stages form a coherent path.

TIME: 08:00–10:00 (2 minutes)

EXPLAIN
Walk through the canonical stage names without implying that every role must be a separate outer pass. With an active TaskGraph, Review and Refactor happen inside the Implement task loop, followed by aggregate verification and acceptance. Explore is conditional and Spec Change is an interrupt. Contracts, scripts, templates and pinned methods support this path.

FACILITATE
One minute: trace a clear feature from Grill to Accept. One minute: show where a foggy goal enters and where a meaning change interrupts.

DEBRIEF / ANSWER KEY
The protocol supplies durable duties and evidence. Runtime bindings project these contracts into the agent environment.

Repository sources: _ask/policies/workflow.md; .agents/ask/task-loop.md; .agents/ask/stages/

### 06 — The repository carries the context.

TIME: 10:00–12:00 (2 minutes)

EXPLAIN
Show the layered layout in a file browser. Distinguish protocol source from package machinery, product state and runtime projection. This separation matters when upgrading: consumer code remains in ordinary product paths and the kit owns a defined set of files.

FACILITATE
Tour the five paths in order. Ask which directory the audience would inspect to understand the Implement stage contract.

DEBRIEF / ANSWER KEY
The stage contract is under .agents/ask/stages/, while generated runtime files point back to the canonical protocol.

Repository sources: README.md; CONTEXT.md

### 07 — Follow one workstream through its files.

TIME: 12:00–14:00 (2 minutes)

EXPLAIN
Open one prepared workstream in the disposable demo repo. The screen should show actual files and their status. Keep example content clearly marked if the workstream has not been executed. Explain why a plan cannot replace intent and why a pass statement cannot replace execution evidence.

FACILITATE
Let participants name the artifact they would use to answer “why does this task exist?” and “what test proves this criterion?”

DEBRIEF / ANSWER KEY
Use intent for purpose, the spec for behavior, and the mapped test evidence for proof.

Repository sources: _ask/templates/plan.md; _ask/docs/spec-test-traceability.md; .agents/ask/stages/10-accept.md

### 08 — The command surface is intentionally small.

TIME: 14:00–16:00 (2 minutes)

EXPLAIN
Explain that each command does a narrow job and does not automatically grant authority for later stages. status is useful across workstreams without substituting an unrelated checkout for the target. verify and record-result are separate operations, as are experiment recording and workstream acceptance.

FACILITATE
Run ./ask --help in the prepared repo. Locate the command for an experiment and the command for a workstream result.

DEBRIEF / ANSWER KEY
record-run captures an individual experiment; record-result captures the workstream outcome.

Repository sources: README.md; _ask/docs/workflow-references.md

### 09 — Prepare methods. Generate bindings.

TIME: 16:00–18:00 (2 minutes)

EXPLAIN
Explain that Community Skills provide methods, while kit stage contracts define workflow duties. Skill pins make dependencies reviewable. sync projects canonical stages into runtime locations. Do not promise that sync prepares all external dependencies or that prepare regenerates every binding.

FACILITATE
Open the manifest and a generated stage side by side with its canonical source. Spend one minute on each relationship.

DEBRIEF / ANSWER KEY
Change canonical source or supported overlays, then regenerate projections. Upgrade kit versions deliberately.

Repository sources: README.md; _ask/docs/codex-integration.md; CONTEXT.md

### 10 — Exercise: find the owner of the answer.

TIME: 18:00–20:00 (2 minutes)

EXPLAIN
Give the audience a short retrieval exercise rather than another explanation. The answers can be described in words; nobody needs a checkout. If using pairs, give them 45 seconds before collecting answers.

FACILITATE
45 seconds: match the four questions. 45 seconds: collect answers. 30 seconds: reveal the answer key verbally.

DEBRIEF / ANSWER KEY
A: intent.md. B: test-plan.json plus executed case evidence. C: current candidate-bound review and passing checks under the accepted contract. D: numeric run reference plus trusted source binding. A file name by itself is not proof that its content is valid.

Repository sources: _ask/docs/spec-test-traceability.md; _ask/docs/workflow-references.md

### 11 — Classify the request before choosing a stage.

TIME: 20:00–22:00 (2 minutes)

EXPLAIN
Use a simple example: recording a run with the wrong HEAD when the contract already forbids it is a bug report. Adding a new output format changes accepted behavior and is feature work. The route is determined by the existing expectation, not the requester’s preferred implementation.

FACILITATE
Spend a minute on the three routes, then ask why “fix it by adding CSV” may contain both a defect report and a feature request.

DEBRIEF / ANSWER KEY
Diagnose the defect against the existing contract; give the new format its own scope.

Repository sources: AGENTS.md; _ask/policies/workflow.md

### 12 — Exercise: route three requests.

TIME: 22:00–24:00 (2 minutes)

EXPLAIN
Ask participants to classify the request without deciding an implementation. Make the distinction between a reported defect and a reproduced defect clear. A reporter can establish the route while reproduction is still needed before production edits.

FACILITATE
Give 45 seconds for classification, 45 seconds for answers, then 30 seconds for the reproduction condition.

DEBRIEF / ANSWER KEY
A: bug route, reproduce the report before regression/fix. B: feature. C: mixed if duplicate handling violates an existing expectation; clarify that expectation if it is unknown.

Repository sources: AGENTS.md; _ask/policies/workflow.md

### 13 — Use Explore when the destination is foggy.

TIME: 24:00–26:00 (2 minutes)

EXPLAIN
Contrast uncertainty about the destination with uncertainty about implementation mechanics. Explore maps decisions, research and prototype findings until the desired outcome is ownable. A clear destination skips 00 for real; the intent records that fact and no empty map is created.

FACILITATE
Read both requests aloud and have the audience choose which needs Explore. Ask what missing decision would make the first request clear.

DEBRIEF / ANSWER KEY
Clarify what is being tracked and what “traceable” must mean before planning an implementation.

Repository sources: AGENTS.md; CONTEXT.md; _ask/policies/workflow.md

### 14 — Grill the decisions that shape the result.

TIME: 26:00–28:00 (2 minutes)

EXPLAIN
Explain grilling as expanding alternatives, trade-offs and failure modes before resolution. Avoid leading with a bare yes/no question. For this demo, per-run configuration and fixed settings support reconstruction. Explain that a fixed seed aids repeatability but does not make performance claims scientifically conclusive.

FACILITATE
Facilitate one example choice: per-run YAML versus a shared mutable file. Ask for a benefit and failure mode of each.

DEBRIEF / ANSWER KEY
The intent should capture the agreed decision and relevant assumptions, not only the selected letter.

Repository sources: CONTEXT.md; _ask/docs/demo/end-to-end-plan.md

### 15 — Worked intent: lower context cost, keep integrity.

TIME: 28:00–30:00 (2 minutes)

EXPLAIN
Show the actual intent.md. Explain that this slide summarizes its approved goal, while the complete artifact also defines project-wide dependencies, immutable revision identity and preservation constraints. The later redesign changed the implementation approach while retaining the goal and thresholds.

FACILITATE
One minute: read the actual What and Why. One minute: identify a constraint that a short-looking implementation might accidentally violate.

DEBRIEF / ANSWER KEY
A reduction is valid only when the measured input still includes equivalent required evidence and the original integrity guarantees remain intact.

Repository sources: work/shorter-hashes/intent.md

### 16 — Approval binds to the complete intent.

TIME: 30:00–32:00 (2 minutes)

EXPLAIN
Show the approved intent and its confirmation artifact in the prepared demo repo if available. Explain stale approval: a decision made against one intent does not cover later changes to its meaning. Do not simulate a human approval by preselecting an option or invoking the command without a submitted choice.

FACILITATE
Show the command as an explanation: ./ask confirm-intent --work-id demo-moons-run --choice approve. Discuss when it is legitimate to run.

DEBRIEF / ANSWER KEY
The command records a decision already submitted by the human. An implementation request alone is not the kit’s exact-intent confirmation.

Repository sources: AGENTS.md; _ask/policies/workflow.md

### 17 — Specify behavior that can be observed.

TIME: 32:00–34:00 (2 minutes)

EXPLAIN
Treat the IDs on this slide as teaching labels, not actual executed contract entries. The real spec uses stable criterion IDs and observable Given/When/Then statements in specs/current/<work-id>.json. Describe how a reviewer would evaluate each condition independently.

FACILITATE
Ask which criterion is observable without opening the trainer code, then distinguish output inspection from proof of every underlying invariant.

DEBRIEF / ANSWER KEY
An observed successful run is one example; rejection behavior and source integrity need their own explicit evidence.

Repository sources: _ask/docs/spec-test-traceability.md; _ask/scripts/record-run.sh

### 18 — Make one criterion concrete.

TIME: 34:00–36:00 (2 minutes)

EXPLAIN
Explain why “supports provenance” is too broad for a single test assertion. This example describes one observable guard. Use a non-HEAD full SHA in the real test. Include setup and output assertions so an unrelated import failure cannot be misreported as a successful guard test.

FACILITATE
Spend one minute on Given/When/Then and one minute asking what a false-positive test would look like.

DEBRIEF / ANSWER KEY
A test that merely sees any non-zero exit could pass because of missing setup. The assertion must establish the intended rejection.

Repository sources: _ask/scripts/record-run.sh; _ask/docs/spec-test-traceability.md

### 19 — Challenge before implementation.

TIME: 36:00–38:00 (2 minutes)

EXPLAIN
Explain the Spec Challenge role and independent perspective. Under the current stage contract it uses a generated runtime subagent and a submitted model choice, with attribution recorded. This presentation explains that process; it is not running a stage or creating independent review evidence.

FACILITATE
Invite one additional counterexample, then point out which criterion or assumption would need clarification.

DEBRIEF / ANSWER KEY
Challenge checks alignment with Why, observable criteria and required test scope before implementation makes the wording expensive to change.

Repository sources: .agents/ask/stages/03-spec-challenge.md; _ask/docs/spec-test-traceability.md

### 20 — A plan assigns outcomes and evidence.

TIME: 38:00–40:00 (2 minutes)

EXPLAIN
Open the plan template. Explain that tasks describe outcomes rather than arbitrary file counts. One task is valid for a cohesive deliverable when the reason is explicit. Distinct results may deserve separate tasks, while tasks that touch shared files need sequencing.

FACILITATE
Use two hypothetical tasks: add a recording guard and add a viewer field. Ask whether they can proceed independently when both change a shared schema.

DEBRIEF / ANSWER KEY
Shared schema changes create a dependency; task ownership alone does not make conflicting work safe.

Repository sources: .agents/ask/stages/05-plan.md; _ask/templates/plan.md

### 21 — Map criteria to tests before coding.

TIME: 40:00–42:00 (2 minutes)

EXPLAIN
Explain the evidence chain from spec to planned cases to reviewed obligations to actual execution. The current traceability interface uses canonical JSON and coordinator records. A candidate cannot make itself complete by changing a pass field. Task results do not automatically satisfy final workstream obligations.

FACILITATE
Walk through one criterion-to-case mapping for the wrong-SHA guard. Ask what happens if the candidate silently removes that case.

DEBRIEF / ANSWER KEY
The accepted contract remains the obligation. Altering it requires Spec Change, review and a new accepted pin.

Repository sources: _ask/docs/spec-test-traceability.md

### 22 — Each task earns its integration.

TIME: 42:00–44:00 (2 minutes)

EXPLAIN
Explain the canonical inner loop. Reported bugs reproduce first. Structural cleanup does not need a manufactured Red. If code changes after review, the old approval is stale; rerun applicable checks and obtain fresh review. Aggregate Verify and Accept remain after task integration.

FACILITATE
Ask whether an approval for commit A authorizes a changed commit B. Spend the last minute tracing the necessary correction loop.

DEBRIEF / ANSWER KEY
Approval and checks must describe the current candidate. A prior good result is evidence about a prior revision.

Repository sources: .agents/ask/task-loop.md

### 23 — Real case: reduce workflow context cost.

TIME: 44:00–46:00 (2 minutes)

EXPLAIN
Introduce shorter-hashes as a real workstream from this repository. Its approved goal was lower token cost with exact dependencies and integrity preserved. The feature evolved from compact references to selective projections after the first measured approach failed. We are reading historical evidence; we are not rerunning the feature implementation live.

FACILITATE
One minute: open work/shorter-hashes/intent.md. One minute: explain the outcome and point to the saved report and decision.

DEBRIEF / ANSWER KEY
This is first-party repository evidence. The benchmark has a specific scope and does not establish general speed, dollar savings or universal model behavior.

Repository sources: work/shorter-hashes/intent.md; work/shorter-hashes/acceptance.md

### 24 — The constraints were part of the feature.

TIME: 46:00–48:00 (2 minutes)

EXPLAIN
Walk through the non-goals and assumptions in the actual intent. Explain why simply truncating hashes would not meet the accepted goal: numeric references need exact resolution and preserved authority. The design had to count lookup overhead and shared metadata rather than optimizing only a pretty display.

FACILITATE
Spend a minute showing the relevant intent paragraphs. Ask which proposed shortcut would invalidate the evidence chain.

DEBRIEF / ANSWER KEY
The goal was less repeated context with exact provenance, not weaker checksums or automatic rebinding of historical evidence.

Repository sources: work/shorter-hashes/intent.md; work/shorter-hashes/plan.md

### 25 — Freeze the questions before measuring.

TIME: 48:00–50:00 (2 minutes)

EXPLAIN
Open the actual benchmark report and show the three journey IDs: resume, review and completion. The baseline source is 9a3d25d035baafc23508f242020d46fae7ff5b14. Tokenization is tiktoken 0.12.0 using cl100k_base and encode_ordinary on UTF-8. Explain that a benchmark is only interpretable when workload and accounting remain stable.

FACILITATE
One minute: show the report header and journey records. One minute: explain why comparing a shorter but incomplete prompt would not count as a success.

DEBRIEF / ANSWER KEY
The reported savings apply to these three frozen, equivalent-evidence journeys, including necessary lookup inputs. They are not an estimate for all future agent conversations.

Repository sources: work/shorter-hashes/benchmark/results/fab05ca/report.json; work/shorter-hashes/benchmark/results/direct-acceptance/report.json

### 26 — The first measured design failed.

TIME: 50:00–53:00 (3 minutes)

EXPLAIN
Open final-verification.json and the fab05ca report. Production checks could pass while the requested savings criterion still failed. This is the central teaching point: implementation correctness and the desired product outcome are distinct. The initial failure is historical evidence, not a result to overwrite after later success.

FACILITATE
One minute: inspect the totals. One minute: invite the audience to explain whether passing tests is enough to accept this feature. One minute: read the saved NOT_APPROVED decision.

DEBRIEF / ANSWER KEY
Passing correctness checks did not establish the requested savings. The outcome remained unapproved until new equivalent-evidence measurements satisfied both thresholds.

Repository sources: work/shorter-hashes/final-verification.json; work/shorter-hashes/benchmark/results/fab05ca/report.json

### 27 — Diagnosis: compact names, oversized reads.

TIME: 53:00–56:00 (3 minutes)

EXPLAIN
Use projection-redesign-authorization.md to trace the diagnosis. Smaller logical IDs alone did not guarantee smaller context. The original replay registered whole-file sources and asked refs show for those complete snapshots. The redesign focused on the query and projection boundary rather than lowering the savings threshold.

FACILITATE
One minute: show the diagnosis paragraph. One minute: compare a whole plan with the relevant task or section. One minute: ask where validation must happen relative to projection.

DEBRIEF / ANSWER KEY
Verify the pinned source before selecting the smaller payload. A small answer without trustworthy source context would violate the original goal.

Repository sources: work/shorter-hashes/projection-redesign-authorization.md; _ask/docs/workflow-references.md

### 28 — Redesign the read; preserve the contract.

TIME: 56:00–59:00 (3 minutes)

EXPLAIN
Show the explicit projection redesign authorization and commit 72f7de0. Explain that the action extended the saved stop boundary for a scoped redesign; it did not itself accept the feature. The implementation handles supported JSON, Markdown tables and TaskGraph YAML forms. It refuses ambiguous or unsupported cases instead of silently guessing.

FACILITATE
One minute: inspect the authorization. One minute: read the documented projection command shape. One minute: connect the immutable source to the selected payload. A command preview is sufficient; no authority-changing mutation is needed.

DEBRIEF / ANSWER KEY
The approved intent and strict acceptance thresholds stayed fixed. The working checkout was the product under development, so the kit workflow was disabled under the self-development rule.

Repository sources: work/shorter-hashes/projection-redesign-authorization.md; _ask/docs/workflow-references.md; git commit 72f7de0

### 29 — The final replay met both savings thresholds.

TIME: 59:00–61:00 (2 minutes)

EXPLAIN
Open the direct-acceptance benchmark report. Explain the chart values and strict scope. All three journeys preserve equivalent evidence. The accepted-candidate replay compared all 60 fresh outputs byte-for-byte with the retained raw archive. Non-JSON files are reported separately and cannot offset either acceptance threshold. The initial candidate is a historical whole-file design, not the accepted redesign.

FACILITATE
Use a minute to read the chart and a minute to discuss the non-JSON trade-off and why it must be disclosed.

DEBRIEF / ANSWER KEY
These are recorded token and byte measurements, not measured runtime or financial savings. No benchmark was rerun while making this deck.

Repository sources: work/shorter-hashes/benchmark/results/direct-acceptance/report.json; work/shorter-hashes/direct-acceptance.json

### 30 — Acceptance preserved the uncomfortable facts.

TIME: 61:00–64:00 (3 minutes)

EXPLAIN
Open acceptance.md and direct-acceptance.json. The accepted candidate is 36b06f3bfa846e6d168a74ebb57aaf8c9fa62a95. The broad command overall remained fail because its source was not current after a fixture-only correction. A wrapper also exited 1 over two unsupported_subtest diagnostics. The decision used the highest-priority self-development exception plus actual independent reviews and explicit delegated acceptance authority. Reviewer confidence is a judgment, not a measured reliability probability.

FACILITATE
One minute: distinguish individual checks from overall completion. One minute: show authority and limits. One minute: point to the preserved result.json instead of relabeling it.

DEBRIEF / ANSWER KEY
This case demonstrates an accountable direct acceptance with disclosed limits. It is not evidence that normal on-path kit completion gates all passed.

Repository sources: work/shorter-hashes/acceptance.md; work/shorter-hashes/direct-acceptance.json; work/shorter-hashes/review.md; work/shorter-hashes/result.json

### 31 — Exercise: defend the conclusion with evidence.

TIME: 64:00–66:00 (2 minutes)

EXPLAIN
Keep the final report and acceptance record visible. Ask participants to reconstruct the decision without using a chat transcript. They should name both supporting evidence and the bounds of the claim. If someone says “everything passed,” return to the explicit formal-completion limits.

FACILITATE
One minute: pair discussion or audience answers. One minute: show the source paths and the answer key.

DEBRIEF / ANSWER KEY
The direct-acceptance report supports savings across three frozen journeys. The explicit delegated instruction and self-development rule explain authority. Formal kit completion was not established; runtime, dollar savings and universal token reductions were not measured.

Repository sources: work/shorter-hashes/acceptance.md; work/shorter-hashes/direct-acceptance.json; work/shorter-hashes/benchmark/results/direct-acceptance/report.json

### 32 — A refusal can be the correct result.

TIME: 66:00–68:00 (2 minutes)

EXPLAIN
Demonstrate a controlled precondition failure. Start with the demo repo clean, create a uniquely named scratch file and show check-clean refusing. Remove only the file you just created and confirm cleanliness. Explain that real user changes need a submitted choice rather than silent stash or reset.

FACILITATE
30 seconds: create scratch file. 45 seconds: run guard and interpret output. 45 seconds: remove your scratch file and recheck.

DEBRIEF / ANSWER KEY
The guard exposes a state requiring a decision; it does not authorize an agent to erase the state.

Repository sources: _ask/scripts/check-clean-worktree.sh; _ask/policies/worktree.md

### 33 — Exercise: review passed, then the code changed.

TIME: 68:00–71:00 (3 minutes)

EXPLAIN
Give the group a scenario: after approval, an agent changes parsing to handle an extra input form. First ask whether it is a local correction or a contract change. Regardless, A’s review does not approve B. Applicable checks and fresh independent review are needed for the changed candidate.

FACILITATE
One minute: pair discussion. One minute: collect reasoning. One minute: reveal the correction and escalation paths.

DEBRIEF / ANSWER KEY
No stale approval. Local fixes repeat checks/review; existing-spec behavior defects need focused failing regression and Green; contract changes use Spec Change before implementation continues.

Repository sources: .agents/ask/task-loop.md

### 34 — Exercise: the destination changes mid-demo.

TIME: 71:00–74:00 (3 minutes)

EXPLAIN
Contrast a minor implementation correction with a new production service. This scenario adds operational scope and changes assumptions. The agent should preserve existing work and use the Spec Change path rather than silently expanding the demo. Broader unrelated work can be parked as later work under policy.

FACILITATE
One minute: identify changed assumptions. One minute: propose the necessary scope decision. One minute: explain why earlier approval does not cover it.

DEBRIEF / ANSWER KEY
Use 04 Spec Change and a bundled complete-intent decision when What/Why/assumptions change. Do not quietly rewrite the accepted specification to match code.

Repository sources: _ask/policies/workflow.md; _ask/policies/delegation.md

### 35 — Resume the authorized work, not a guess.

TIME: 74:00–76:00 (2 minutes)

EXPLAIN
Explain a concrete interruption: the plan stops after the spec is drafted. A later generic “continue” does not authorize implementation. An explicit later direction can extend the endpoint, while unchanged intent remains byte-identical. If the named workstream is unavailable or conflicting, clarify instead of substituting the checkout.

FACILITATE
Ask the audience what a resumed agent should inspect before coding. Use the three cards as the recovery order.

DEBRIEF / ANSWER KEY
Continuation restores the exact authorized stage and task. It does not infer permission for everything left in the pipeline.

Repository sources: AGENTS.md; _ask/policies/workflow.md

### 36 — Close the workstream with current evidence.

TIME: 76:00–79:00 (3 minutes)

EXPLAIN
Show a prepared completed workstream only if it genuinely has current evidence. Explain ./ask verify, traceability check-completion, check-workstream --acceptance and record-result in their proper roles. The Accept contract requires context-audit.md with no open checklist IDs and evidence cited in acceptance.md. Do not run record-result --result pass unless checks actually pass.

FACILITATE
One minute: inspect verification. One minute: inspect acceptance/context audit. One minute: contrast individual run references with the workstream result and human decision.

DEBRIEF / ANSWER KEY
A recorded metric is not an accepted workstream. A successful shell process is not complete case evidence.

Repository sources: _ask/docs/spec-test-traceability.md; .agents/ask/stages/10-accept.md; README.md

### 37 — Adopt the kit on one bounded change.

TIME: 79:00–81:00 (2 minutes)

EXPLAIN
Give a practical adoption path without doing a live installation. Start with a bounded change so the team can inspect the complete workflow and tune local policy deliberately. The self-development exception used in the real case is specific to changing AskIt itself; normal consumer feature work uses its required workflow and evidence.

FACILITATE
Give participants 30 seconds to choose a real candidate change, then take one example and route it together.

DEBRIEF / ANSWER KEY
A handoff another engineer can reconstruct requires the correct authority as well as current evidence.

Repository sources: README.md; _ask/policies/workflow.md

### 38 — Know what this demonstration establishes.

TIME: 81:00–83:00 (2 minutes)

EXPLAIN
Keep claims precise. The shorter-hashes reports are actual first-party historical records; making this deck did not independently rerun them. They support a result across three frozen journeys. Formal kit completion remained unestablished; direct acceptance used explicit delegated authority under the self-development exception. The optional moons exercise is a separate teaching example.

FACILITATE
One minute: revisit the session objectives. One minute: ask which claims are established by the saved records and which would need new work.

DEBRIEF / ANSWER KEY
Separate measured outcome, correctness evidence, formal workflow status and acceptance authority. Each answers a different question.

Repository sources: work/shorter-hashes/acceptance.md; work/shorter-hashes/direct-acceptance.json

### 39 — Discuss the decisions you would make.

TIME: 83:00–88:00 (5 minutes)

EXPLAIN
Open Q&A. Prefer questions grounded in an actual task or artifact. For speculative features, explain the scope boundary and park the topic. If the room is quiet, ask participants to choose one prompt and apply it to the candidate change from the adoption exercise. Avoid inventing answers about runtime behavior that has not been verified.

FACILITATE
Take two or three questions, roughly 90 seconds each. At minute 88, reserve the final two minutes for the closing reconstruction.

DEBRIEF / ANSWER KEY
Identify the relevant source file or policy for any unresolved technical question rather than guessing.

Repository sources: README.md; _ask/policies/delegation.md

### 40 — Can a teammate reconstruct the work?

TIME: 88:00–90:00 (2 minutes)

EXPLAIN
Return to the real case. Ask the group to reconstruct the original goal, failed first result, authorized redesign, final scoped measurements and acceptance limits using repository artifacts. Close by pointing to the root README, work/shorter-hashes/acceptance.md and the benchmark reports. The optional two-moons commands in the guide offer a follow-up exercise.

FACILITATE
One minute: audience names the evidence chain. One minute: show the source paths and conclude at minute 90.

DEBRIEF / ANSWER KEY
The case becomes defensible when the outcome and the exceptions remain attributable to exact sources; neither a successful metric nor a confident review substitutes for the whole story.

Repository sources: README.md; _ask/docs/demo/end-to-end-plan.md
