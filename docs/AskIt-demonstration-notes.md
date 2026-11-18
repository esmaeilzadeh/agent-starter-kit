# Karband — 90-minute teaching presentation

A worked case study in plain language. This guide matches the deck slide for slide.

The CSV examples teach the workflow; they are not claims of delivered application code. UI demonstrations, if included, identify their actual source and evidence state.

Read the [developer guide](../_ask/docs/developer-guide.md) for flags and recovery, and the [Superpowers comparison](../_ask/docs/askit-vs-superpowers.md) for the inspected versions.

## Before presenting

- Open the deck and the saved full UI screenshots in `docs/askit-demo-ui/`.
- The UI demonstration uses a smaller paid-status export; it does not claim the whole teaching feature is complete.
- Follow the launch instructions in [the demo record](askit-demo-ui/README.md) for the develop-based UI. Use its isolated worktree, not an unrelated checkout.
- Treat commands with `<placeholders>` as examples. Replace them only when running the corresponding authorized step.
- Keep the four-minute exercise and the closing questions within the timings below.

## Session plan

| Slide | Topic | Minutes | Session time |
| --- | --- | ---: | --- |
| 1 | Karband: a worked example | 1 | 00:00–01:00 |
| 2 | What you will learn | 2 | 01:00–03:00 |
| 3 | Case study: filtered orders export | 2 | 03:00–05:00 |
| 4 | Choose the request route | 2 | 05:00–07:00 |
| 5 | Prepare an isolated workstream | 2 | 07:00–09:00 |
| 6 | 00 Explore: find the right destination | 3 | 09:00–12:00 |
| 7 | Explore: test an idea or skip it | 2 | 12:00–14:00 |
| 8 | 01 Grill: settle the important choices | 3 | 14:00–17:00 |
| 9 | Approve the complete intent | 3 | 17:00–20:00 |
| 10 | Define the user journey before coding | 1 | 20:00–21:00 |
| 11 | 02 Spec: turn the agreement into checks | 2 | 21:00–23:00 |
| 12 | 03 Challenge: find cases the spec misses | 3 | 23:00–26:00 |
| 13 | 04 Spec Change: when the agreement changes | 2 | 26:00–28:00 |
| 14 | 05 Plan: divide the case into tasks | 3 | 28:00–31:00 |
| 15 | UI example: the epic and its delivery path | 2 | 31:00–33:00 |
| 16 | UI: choose the workstream and source | 1 | 33:00–34:00 |
| 17 | Connect each task to its tests | 3 | 34:00–37:00 |
| 18 | UI example: a task owns a named test | 2 | 37:00–39:00 |
| 19 | UI: follow the task back to its story | 1 | 39:00–40:00 |
| 20 | 06 Implement: prove the missing behavior | 3 | 40:00–43:00 |
| 21 | Make the smallest correct change | 3 | 43:00–46:00 |
| 22 | 07 Review: inspect the current candidate | 3 | 46:00–49:00 |
| 23 | 08 Refactor: close the findings | 3 | 49:00–52:00 |
| 24 | 09 Verify: check the complete result | 3 | 52:00–55:00 |
| 25 | Read the evidence without overstating it | 2 | 55:00–57:00 |
| 26 | UI example: inspect what the test proves | 2 | 57:00–59:00 |
| 27 | UI: inspect the test source | 1 | 59:00–60:00 |
| 28 | 10 Accept: decide whether to close the work | 3 | 60:00–63:00 |
| 29 | Case variation: repair an existing export | 3 | 63:00–66:00 |
| 30 | Resume the right work after a break | 3 | 66:00–69:00 |
| 31 | Handle unrelated work without losing it | 2 | 69:00–71:00 |
| 32 | Skills and models: two different choices | 3 | 71:00–74:00 |
| 33 | Codex: invoke a kit stage with $ | 1 | 74:00–75:00 |
| 34 | Cursor: use stage commands and local rules | 1 | 75:00–76:00 |
| 35 | Keep project settings through upgrades | 1 | 76:00–77:00 |
| 36 | Optional tools: know what they prove | 2 | 77:00–79:00 |
| 37 | The same export in Superpowers | 3 | 79:00–82:00 |
| 38 | Choosing a workflow for your team | 2 | 82:00–84:00 |
| 39 | Exercise: a late change request | 4 | 84:00–88:00 |
| 40 | A handoff another developer can use | 2 | 88:00–90:00 |
| **40** | **Total** | **90** | **00:00–90:00** |

## 01 — Karband: a worked example

**Our case**

A support team needs a CSV file of filtered orders. We will follow the request through decisions, code, tests and acceptance.

**Your role**

You decide what the feature should do. The agent does the agreed work and keeps evidence.

**Today**

A 90-minute workshop in one case study, with a comparison to Superpowers.

### Presenter notes

01. Karband: a worked example
00:00–01:00 (1 min)

The orders feature is a teaching example, not a claim that an orders application already exists in this repository. CSV is a text file that spreadsheet tools can open. Explain that an agent is the coding assistant. A workstream is one named piece of work with its own branch and records. Intent means the agreed What and Why. The UI demonstration later uses separately identified repository records. Never describe example test results as recorded executions.

Sources:
_ask/docs/developer-guide.md

## 02 — What you will learn

**Choose a route**

Tell a new feature from a defect. Decide when to explore and when the request is already clear.

**Follow the work**

Connect intent, requirements, tasks and tests. Know when a human decision is needed.

**Check a handoff**

Find the exact source version, review, test results and acceptance decision.

### Presenter notes

02. What you will learn
01:00–03:00 (2 min)

Use the workshop as a sequence: request and setup; stages 00–05; task implementation and review; final evidence; recovery and options; Superpowers comparison; a short audience exercise. The notes assign a time to every slide and total 90 minutes. Invite participants to keep one question in mind: could a colleague reconstruct this change next week?

Sources:
_ask/docs/developer-guide.md

## 03 — Case study: filtered orders export

**The request**

Support staff filter orders by status and date. They need those matching orders in a CSV file for analysis.

**Known limits**

Use existing permissions. Do not add scheduled exports, new columns or a new reporting system.

**Open decisions**

Does export mean all matching rows or just this page? What should happen when no rows match?

### Presenter notes

03. Case study: filtered orders export
03:00–05:00 (2 min)

Use a small sample: order A is paid today, B is cancelled today, C is paid last month. The current filter is paid orders today, so only A matches. Add a second matching order on another page to expose pagination. These rows are sample data. Ask the audience which unanswered question could make an otherwise correct implementation unacceptable.

Sources:
_ask/docs/developer-guide.md

## 04 — Choose the request route

**Feature**

Export does not exist yet. Adding it changes what the product can do: use the feature workflow.

**Bug fix**

An existing export promises filtered rows but includes cancelled orders. Reproduce that violation before changing code.

**Mixed request**

“Fix the filter and add scheduled exports” contains two outcomes. Separate them and sequence shared-file work.

### Presenter notes

04. Choose the request route
05:00–07:00 (2 min)

Ask participants to classify three requests. The deciding factor is the accepted expectation, not whether the user used the word fix. If the expected behavior is unclear, ask only what distinguishes a defect from a requested behavior change. A direct /01-grill command and off-path mode do not bypass this classification.

Sources:
_ask/docs/developer-guide.md

## 05 — Prepare an isolated workstream

**Check access and existing edits**

Run access-check and check-clean. Resolve each existing changed file explicitly; never hide it with a silent stash or reset.

**Prepare the kit**

Install the reviewed skill versions with prepare. Generate runtime instructions with sync. Review and commit setup changes.

**Start the case**

Create work ID orders-csv. Its branch is agent/orders-csv, based on develop; templates are not approvals.

### Presenter notes

05. Prepare an isolated workstream
07:00–09:00 (2 min)

Commands are a walkthrough, not a record that they already succeeded. The product must already be a Git repository with the kit installed and an intentional develop branch. After prepare/sync, changes may need to be reviewed and committed before start-work. The optional tracker wizard is human-only. For developing Karband itself, keep the kit disabled unless a separate exact frozen copy governs dogfooding.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask access-check
./ask check-clean
./ask prepare
./ask sync
# Review and commit setup changes, then:
./ask start-work orders-csv
```

Sources:
_ask/docs/developer-guide.md

## 06 — 00 Explore: find the right destination

**A vague starting point**

“Support needs better reports” could mean a CSV export, a dashboard or scheduled email. Coding now would choose the product for the user.

**Find facts**

Read the orders page and existing filters. Ask support which decision they are trying to make with the data.

**Choose a direction**

For occasional spreadsheet analysis, a filtered CSV may be enough. Record options, the decision and the handoff.

### Presenter notes

06. 00 Explore: find the right destination
09:00–12:00 (3 min)

Explore is decision work. The agent investigates facts; the human chooses goals. Write work/orders-csv/explore-map.md with a nonempty Handoff to Intent section if Explore runs. Optional research or domain skills may help, but extra skills affecting What/Why need selection before preparation. Explain why a small export is only a candidate until the need is understood.

Sources:
_ask/docs/developer-guide.md

## 07 — Explore: test an idea or skip it

**A useful prototype**

If support is unsure about columns, show a throwaway sample CSV. Use it to discuss the decision, not to claim production completion.

**A real skip**

If the requested rows, columns and purpose are already clear, skip Explore. Record the reason in intent; do not create an empty map.

**The boundary**

A working experiment does not approve a product direction or authorize keeping its code.

### Presenter notes

07. Explore: test an idea or skip it
12:00–14:00 (2 min)

Contrast a sample file with a shipping implementation. The skip marker is exactly “Explore skipped: destination already clear.” When /00-explore is explicitly requested for feature work, Explore runs and needs its map. When the destination stays unclear, /01-grill does not magically remove the need to explore. Ask the audience which of the sample request and the fully specified export needs Explore.

Sources:
_ask/docs/developer-guide.md

## 08 — 01 Grill: settle the important choices

**Rows**

All orders matching the filter, or only the current page? Choose explicitly; both are plausible implementations.

**Empty results**

Return a file with column headers, show an empty-state message, or disable export? Explain the trade-off.

**Assumptions**

Reuse current permissions and column names. State these assumptions so support can correct them.

### Presenter notes

08. 01 Grill: settle the important choices
14:00–17:00 (3 min)

For this case, propose all filtered rows and a header-only empty file, then ask the audience to approve or change those teaching choices. Do not pretend the audience already approved. Grill asks only questions that change the outcome or block other decisions. It uses expanded choices plus optional added text. The agent should look up code facts itself. A direction such as “CSV sounds good” does not settle pagination or empty behavior.

Sources:
_ask/docs/developer-guide.md

## 09 — Approve the complete intent

**What and why**

Export all filtered orders as CSV so support can analyze them in a spreadsheet. Keep current columns and permissions.

**Not included**

Scheduled emails, extra personal data and a new report designer are outside this workstream.

**A real approval**

Read the complete intent and assumptions, then approve or request changes. The recorded approval belongs to that exact document.

### Presenter notes

09. Approve the complete intent
17:00–20:00 (3 min)

The agent commits prepared intent/scaffold before asking the approval question. A submitted choice is required; a highlighted default is not approval. Show confirm-intent only after the human choice. Changing intent makes that confirmation stale. Normal unchanged Spec/Plan preparation continues without a repeated approval at every stage. A stop-after-plan endpoint still prevents implementation.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask confirm-intent --work-id orders-csv --choice approve
```

Sources:
_ask/docs/developer-guide.md

## 10 — Define the user journey before coding

**Starting state**

A signed-in support user can view orders. The sample includes matching, nonmatching and later-page rows.

**Action and result**

Set the paid-today filter, export, then open the file. It contains only matching rows across pages, with agreed columns.

**Repeat safely**

Use isolated test data and reset it between runs. If end-to-end testing does not apply, record a specific reason.

### Presenter notes

10. Define the user journey before coding
20:00–21:00 (1 min)

An end-to-end test follows a user journey across the system, not just a helper function. Ask what environment, user role, data and reset are needed. This contract begins in Grill and is carried into Spec, Plan and Verify. Browser checks alone are not supported structured case evidence unless the accepted runner supports their declaration. Do not promise an adapter that is absent.

Sources:
_ask/docs/developer-guide.md

## 11 — 02 Spec: turn the agreement into checks

**Criterion C1: filtering**

Given paid and cancelled orders, when the user exports paid orders, the file contains every matching order and no cancelled order.

**Criterion C2: empty results**

Given no matching orders, export produces the agreed header-only CSV. No unrelated data appears.

**Stable identities**

Keep criterion IDs in the prose and JSON specification. Later tests refer to C1 and C2 rather than a vague “export works.”

### Presenter notes

11. 02 Spec: turn the agreement into checks
21:00–23:00 (2 min)

Explain a criterion as a condition the result must satisfy. Given/When/Then is simply starting state, action and expected result. The Markdown spec is readable; canonical JSON gives tooling stable IDs. The current spec preserves intent and separates requirements from implementation preferences. Empty results and permission reuse are contract choices, not choices the implementation may silently alter.

Sources:
_ask/docs/developer-guide.md

## 12 — 03 Challenge: find cases the spec misses

**Pagination**

A second matching order is on page two. A test using only one page could pass while the feature misses real orders.

**Permissions**

A user without access must not obtain data through the export endpoint. Reuse the existing access rule.

**Independent check**

A separate reviewer challenges the requirements and test obligations. Record PASS or the human decision still needed.

### Presenter notes

12. 03 Challenge: find cases the spec misses
23:00–26:00 (3 min)

Ask participants to invent one example that defeats a weak spec. The challenge is written by an independent agent, not just the author’s rereading. The stage asks for a model selection and explicit continuation if the chosen model is in the same family as the author. A larger model alone does not prove independent evidence. Escalation means a real decision remains, not that the agent may choose new semantics.

Sources:
_ask/docs/developer-guide.md

## 13 — 04 Spec Change: when the agreement changes

**The discovery**

This interrupts normal work only when the agreement must change. Support now asks for customer emails, outside the approved columns.

**The decision**

Show the reason, alternatives, access implications and revised intent together. Ask whether to approve the change or keep the current scope.

**The consequence**

If approved, update and review the affected specification, plan and tests before continuing. Do not quietly add the column.

### Presenter notes

13. 04 Spec Change: when the agreement changes
26:00–28:00 (2 min)

This stage is an interrupt, not a mandatory stop between Challenge and Plan. It is triggered by a semantic change. Preserve the previously accepted spec while proposing the change. If What/Why/assumptions change, bundle the complete revised intent and related scope change into one clear choice; do not ask twice for the same linked approval. An inconvenient failing test is not a reason to relax requirements.

Sources:
_ask/docs/developer-guide.md

## 14 — 05 Plan: divide the case into tasks

**Task T1: select and format rows**

Reuse the existing filter and CSV conventions. Prove filtering, pagination and the agreed empty-file behavior.

**Task T2: connect the export action**

Use T1 from the orders page and enforce existing permissions. T2 depends on T1.

**Task boundaries**

Each task has an ID, outcome, owned paths, dependencies and completion evidence. Shared files mean sequential work.

### Presenter notes

14. 05 Plan: divide the case into tasks
28:00–31:00 (3 min)

These are teaching task boundaries, not records of delivered code. Show plan.md and inner-loop/tasks.yaml as the human and machine views of the same breakdown. Give owned-path examples such as a module’s directory, not a fabricated real path in this repo. One task is valid when splitting would be artificial; two tasks here illustrate a real dependency. New deliverables return to reviewed planning.

Sources:
_ask/docs/developer-guide.md

## 15 — UI example: the epic and its delivery path

**Epic**

A larger goal: filtered orders CSV.

**Story and scenario**

Explain who needs it and which behavior matters.

**Task and test**

Follow the outline to the assigned work and its check.

### Presenter notes

15. UI example: the epic and its delivery path
31:00–33:00 (2 min)

Authentic UI demonstration. The UI code is from develop base eac5950928752e30f0341330bdcc6c39b601a420. Demo records and a small paid-status CSV function/test were added on isolated branch agent/demo-orders-export at 99866ad58f63414287a15a9309bd99833340ecf6. This is a smaller slice of the teaching case: it does not implement the full date, pagination or permission journey. The UI displays a proposed/planned record, not accepted or structured-verified completion. One ordinary unittest passed separately; it is not imported into the UI as authoritative execution. The top-level intent is displayed as Epic; do not describe it as a separate underlying epic node type. Select the root, then follow the Story, Scenario, Task and Test in the left outline. The demonstration story calls the user a merchandiser; that role is the orders worker in this smaller sample. The small image is an unchanged crop of the original browser screenshot; the full original is supplied alongside the deck.

Sources:
docs/askit-demo-ui/README.md

## 16 — UI: choose the workstream and source

**Workstream**

Select demo-orders-export to inspect this example.

**Source version**

The committed source identifies the exact branch and revision being displayed.

**Read-only view**

Inspect saved records here. Selecting a source does not approve or execute the work.

### Presenter notes

16. UI: choose the workstream and source
33:00–34:00 (1 min)

This is an additional detail view of an existing authentic capture, not a newly captured UI session. Source revisions and the planned evidence state remain those documented in docs/askit-demo-ui/README.md. Use the full original image if the audience wants surrounding context.

Sources:
docs/askit-demo-ui/README.md

## 17 — Connect each task to its tests

**C1 → T1 → TEST-FILTER**

Use paid and cancelled rows, plus a matching row on a later page. Assert both which rows are present and which are absent.

**C2 → T1 → TEST-EMPTY**

Use zero matching rows. Assert the exact agreed headers and no data rows.

**Permission rule → T2 → TEST-ACCESS**

Call export without the required access. Confirm that no restricted order data is returned.

### Presenter notes

17. Connect each task to its tests
34:00–37:00 (3 min)

Explain the direction aloud: requirement C1 is implemented by T1 and checked by TEST-FILTER. IDs on Persian slides are stable technical identifiers and have the same meaning as in English. The exact task graph, criterion metadata and test-plan.json mapping are independently reviewed and pinned before implementation. A test count is not a proof of coverage. A test with no meaningful assertion cannot prove a criterion.

Sources:
_ask/docs/developer-guide.md

## 18 — UI example: a task owns a named test

**One delivery task**

export-orders-csv is linked to its product story.

**One assigned check**

The assigned test is ORDERS-CSV-PAID.

**Owned files**

The function and test paths show the task’s boundary.

### Presenter notes

18. UI example: a task owns a named test
37:00–39:00 (2 min)

Authentic UI demonstration. The UI code is from develop base eac5950928752e30f0341330bdcc6c39b601a420. Demo records and a small paid-status CSV function/test were added on isolated branch agent/demo-orders-export at 99866ad58f63414287a15a9309bd99833340ecf6. This is a smaller slice of the teaching case: it does not implement the full date, pagination or permission journey. The UI displays a proposed/planned record, not accepted or structured-verified completion. One ordinary unittest passed separately; it is not imported into the UI as authoritative execution. The model Task uses a qualified execution identity (work_id plus task_id). This joins product identity to the task graph without a duplicate task row. Point to Related Stories and Related tests, then to the owned source paths. The test-plan task_scopes record assigns ORDERS-CSV-PAID to export-orders-csv. These are verified relationship records, not evidence that every completion gate passed.

Sources:
docs/askit-demo-ui/README.md

## 19 — UI: follow the task back to its story

**Related scenario**

The scenario names the behavior: export only paid orders.

**Related story**

The story explains who needs the feature and why. Use Open Story to return to that context.

**Why it matters**

A task should retain its purpose. A file list alone cannot explain whether the change meets the need.

### Presenter notes

19. UI: follow the task back to its story
39:00–40:00 (1 min)

This is an additional detail view of an existing authentic capture, not a newly captured UI session. Source revisions and the planned evidence state remain those documented in docs/askit-demo-ui/README.md. Use the full original image if the audience wants surrounding context.

Sources:
docs/askit-demo-ui/README.md

## 20 — 06 Implement: prove the missing behavior

**Write the behavior test**

TEST-FILTER includes a paid order on page two. The assertion expects that order in the exported file.

**Run it before the fix**

Commit the test and run it. A missing order should fail the assertion for the intended reason.

**Keep the failed revision**

Record the exact source revision and output. An import error or broken test setup is not proof of missing behavior.

### Presenter notes

20. 06 Implement: prove the missing behavior
40:00–43:00 (3 min)

This is Red in test-driven development: a real behavior assertion fails before the implementation. For a feature, this proves the new behavior is not present. For a reported bug, first reproduce the reporter’s fault, then write the focused regression. Use immutable committed source. A hypothetical table in a slide is a planned test, not captured Red evidence.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask traceability run orders-csv --candidate-sha <red-revision> --phase red
```

Sources:
_ask/docs/developer-guide.md

## 21 — Make the smallest correct change

**Green: satisfy the test**

Use the existing filtered query across all result pages. Export only the agreed columns. Run the relevant checks.

**Refactor: simplify safely**

If row selection is duplicated, reuse the existing helper. Keep behavior and tests unchanged; avoid an unrelated rewrite.

**One task writer**

Commit meaningful steps. Integrate the current reviewed task before another task has unintegrated work.

### Presenter notes

21. Make the smallest correct change
43:00–46:00 (3 min)

Explain Green as enough code to satisfy the agreed behavior, not enough code to pass one weak assertion. Refactor improves structure while preserving behavior. An empty cleanup pass is valid. The graph owns task dependencies and steering paths; optional task worktrees integrate fast-forward only. A new deliverable or changed test assignment requires a reviewed plan amendment.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask check-workstream orders-csv
./ask inner-loop validate orders-csv
./ask inner-loop status orders-csv
./ask inner-loop run orders-csv
```

Sources:
_ask/docs/developer-guide.md

## 22 — 07 Review: inspect the current candidate

**Requirement check**

Does page-two data appear? Are cancelled rows absent? Does the empty-file behavior match C2? Inspect the actual assertions.

**Scope check**

Did the task touch only its agreed modules? A new reporting framework is outside this export task.

**Independent decision**

A separate reviewer checks each committed task. Review and correction repeat inside its task loop. Changed candidates need fresh approval.

### Presenter notes

22. 07 Review: inspect the current candidate
46:00–49:00 (3 min)

Review is not only style inspection. The reviewer considers semantics, test strength and boundary. The reviewer commits nothing; the coordinator records its attributable decision and evidence. The stage has an explicit model choice and same-family acknowledgment rule. A worker saying “approved” cannot approve its own integration. Review in an active graph happens per task inside implementation.

Sources:
_ask/docs/developer-guide.md

## 23 — 08 Refactor: close the findings

**Local defect**

The reviewer finds that a filter is dropped on the second page. Add the focused regression, fix it and obtain fresh review.

**Broader suggestion**

“Replace the whole reporting layer” is a separate improvement. Keep an attributed later-work draft rather than expanding this task.

**Contract change**

“Export all orders regardless of filter” changes the agreement. Stop for Spec Change; do not call it cleanup.

### Presenter notes

23. 08 Refactor: close the findings
49:00–52:00 (3 min)

Within the active task loop, valid local findings must be fixed and freshly reviewed, or withdrawn by the reviewer with evidence. Exhausted retries and stale approval block integration. Broader-refactor drafts stay in candidate-bound evidence until no writer or resumable candidate remains; then the coordinator publishes later cards through normal integration. Outside the graph, dispositions also allow accept with rationale; do not apply that looser rule inside the active graph.

Sources:
_ask/docs/developer-guide.md

## 24 — 09 Verify: check the complete result

**Run the agreed checks**

The CheckPlan lists required project checks. Run final verification against committed source, including the agreed user journey.

**Keep actual evidence**

Record which cases ran, their assertions and results, the reviewed source version and criterion coverage.

**Separate task and workstream**

T1 passing is not proof that the page button and permissions in T2 work. Final checks cover the whole accepted scope.

### Presenter notes

24. 09 Verify: check the complete result
52:00–55:00 (3 min)

CheckPlan is the committed .agents/verification.yaml, not an improvised shell wrapper around verify. Put project-native static commands in it. Actual execution and semantic review must fit the claim: a type checker does not prove filtering, and a browser screenshot does not prove every test passed. Missing mandatory checks fail closed. An ordinary repository verify outside a workstream runs static checks only.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask verify
```

Sources:
_ask/docs/developer-guide.md

## 25 — Read the evidence without overstating it

**Current runner limit**

Karband’s structured per-case runner supports explicit Python unittest cases and discovery. Unsupported runners cannot claim the same completion evidence.

**Plan versus execution**

A planned test ID means “must run.” A saved case result means “this case ran on this revision.” These are different facts.

**For this case**

Do not label export complete just because TEST-FILTER is listed. Find its actual result and the independent review for the tested version.

### Presenter notes

25. Read the evidence without overstating it
55:00–57:00 (2 min)

Explain this implementation limit before a team adopts Karband for a non-Python application. Static checks can still run through CheckPlan, but they do not fill unsupported per-case evidence. Structured completion reloads contracts, coordinator authority, source bindings and logs; editing completion.json to say pass does not authorize completion. Treat old evidence migrations as explicit reviewed work, never invented historical Red.

Sources:
_ask/docs/spec-test-traceability.md

## 26 — UI example: inspect what the test proves

**Expected result**

The CSV contains paid orders O-101 and O-103 only.

**Trace to the requirement**

The selected case is linked to criterion ORDERS-001 and its scenario.

**Read the limit**

A planned test and visible source do not prove recorded execution or acceptance.

### Presenter notes

26. UI example: inspect what the test proves
57:00–59:00 (2 min)

Authentic UI demonstration. The UI code is from develop base eac5950928752e30f0341330bdcc6c39b601a420. Demo records and a small paid-status CSV function/test were added on isolated branch agent/demo-orders-export at 99866ad58f63414287a15a9309bd99833340ecf6. This is a smaller slice of the teaching case: it does not implement the full date, pagination or permission journey. The UI displays a proposed/planned record, not accepted or structured-verified completion. One ordinary unittest passed separately; it is not imported into the UI as authoritative execution. This particular screenshot was captured at d444804bda2a68e0d503c4b2c23c8aef3622e2b8. Its test plan, criterion documents, implementation, test source and Test model node are unchanged at the final demo commit; the retained provenance record verifies byte equality. Select the named test from the task, read the case identifier and ORDERS-001 assertions, and inspect the current committed source. Source visibility and planned identity are different from an executed result. In this sample task runtime remains not recorded and completion is not asserted. Ask the audience what additional Red, final execution, review and acceptance records would be needed to close this feature.

Sources:
docs/askit-demo-ui/README.md

## 27 — UI: inspect the test source

**Source path**

The test view names the committed test file.

**Concrete check**

The test creates fictional paid and pending orders.

**Keep the distinction**

Seeing test code helps review it. It is not a recorded run or a passing completion gate.

### Presenter notes

27. UI: inspect the test source
59:00–60:00 (1 min)

This is an additional detail view of an existing authentic capture, not a newly captured UI session. Source revisions and the planned evidence state remain those documented in docs/askit-demo-ui/README.md. Use the full original image if the audience wants surrounding context.

Sources:
docs/askit-demo-ui/README.md

## 28 — 10 Accept: decide whether to close the work

**The handoff**

The file follows the agreed filters, columns and empty behavior. Present the tested source revision, checks, review and known limits.

**The decision**

The human accepts the workstream or requests changes. Acceptance uses the full result, not only an agent’s success message.

**The release boundary**

Accepting the feature does not itself merge, push, tag or deploy it. Those actions need their own authority.

### Presenter notes

28. 10 Accept: decide whether to close the work
60:00–63:00 (3 min)

Show the context-audit requirement: no open checklist IDs remain; closed items are pass or a Spec Change link. Run final completion and acceptance checks before recording a pass. record-result is provenance, not the human approval itself. The default waits for a submitted Accept workstream choice; auto-accept is possible only when the delegation policy actually permits it. Release evidence and human authority remain separate.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask traceability check-completion orders-csv
./ask check-workstream orders-csv --acceptance
./ask record-result --work-id orders-csv --commit-sha <tested-revision> --result pass
```

Sources:
_ask/docs/developer-guide.md

## 29 — Case variation: repair an existing export

**The report**

“Filtered export includes cancelled orders.” The accepted requirement already says those rows must be excluded.

**Reproduce and repair**

Use the reporter’s filter and data. Capture the fault, add a focused failing regression, make the minimal fix and verify it.

**Keep the route focused**

Reuse the existing contract and a concise repair record. Do not create a new feature project or manufacture failures in passing guards.

### Presenter notes

29. Case variation: repair an existing export
63:00–66:00 (3 min)

If the report does not reproduce, record attempts and request missing context. Do not reinterpret it as feature work merely to keep coding. Bug work still keeps applicable clean-tree, branch, review, meaningful-commit and verification rules. A new request for another export format is a feature outcome and should be separated.

Sources:
_ask/docs/developer-guide.md

## 30 — Resume the right work after a break

**Name the target**

“Continue orders-csv.” Inspect its branch, intent, plan, task state and recent commits before selecting the next action.

**Respect the endpoint**

If the approved plan stopped after planning, “continue” does not authorize coding. Explicitly extend the endpoint if that is what you want.

**Keep approval current**

If only the endpoint changed, preserve approved intent bytes. If behavior or assumptions changed, use the normal change decision.

### Presenter notes

30. Resume the right work after a break
66:00–69:00 (3 min)

Named workstream beats the current checkout. Without a name, a matching checked-out agent branch is preferred; ambiguity needs clarification. status is read-only inventory; inner-loop resume is not read-only and can repair source/Git state. Preserve persistent locks and candidate evidence. Do not erase state to make a stale approval appear fresh.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask access-check
./ask status --work-id orders-csv
./ask inner-loop status orders-csv
```

Sources:
_ask/docs/developer-guide.md

## 31 — Handle unrelated work without losing it

**A dirty starting tree**

Someone has an unfinished invoice edit. Choose commit, stash, move or discard for that path before starting export work.

**An urgent interruption**

A production issue arrives. Choose the new workstream’s base explicitly and preserve the interrupted export’s state.

**Leaving the normal path**

Off-path lasts for this chat. It does not permit hidden data loss, unreported failures or changing agreed behavior without authority.

### Presenter notes

31. Handle unrelated work without losing it
69:00–71:00 (2 min)

Off-path is a workflow preference, not a persistent file flag. New chats start on-path. Mixed outcomes still need routing and a reported bug still needs reproduction. Later cards are parked proposals, not authorized active work. In an active task loop, broader-refactor drafts are published only after no writer/resumable candidate remains.

Sources:
_ask/docs/developer-guide.md

## 32 — Skills and models: two different choices

**Method**

The community grilling skill is a reusable interview method. The kit’s Grill stage adds repository-specific artifacts and approval rules.

**Generation**

Edit the canonical stage or a local overlay, then sync. Do not hand-edit the generated kit-01-grill skill.

**Model**

Choose a capable model for each job. Routine checks may use a cheaper model; independent review still needs real evidence.

### Presenter notes

32. Skills and models: two different choices
71:00–74:00 (3 min)

Community skills are pinned in _ask/skills/manifest.yaml and prepared; kit-* stage skills are generated from .agents/ask/stages plus overlays. A pin change and sync are different operations. Model defaults depend on stage/runtime and review risk. Workstream models.yaml and ASK_WORK_ID can override defaults. Regenerating files does not change an already-running agent or prove a model is available to the account.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask prepare
ASK_WORK_ID=orders-csv ./ask sync
```

Sources:
_ask/docs/developer-guide.md

## 33 — Codex: invoke a kit stage with $

**Explore an unclear request**

$kit-00-explore
Support needs better order reports. Help choose the outcome.

**Clarify a bounded feature**

$kit-01-grill
Clarify filtered CSV export; stop after complete intent approval.

**What $ selects**

It selects the kit stage skill. It does not grant approval or skip that stage’s prerequisites.

### Presenter notes

33. Codex: invoke a kit stage with $
74:00–75:00 (1 min)

These are editable usage examples, not screenshots of a Codex or Cursor client. No editor or browser surface was exposed to the UI connector during this update. Repository files verify the generated surfaces: .agents/skills/kit-01-grill/SKILL.md and .cursor/commands/01-grill.md. Explain the dollar prefix in Codex and slash prefix in Cursor; do not type either as a shell command. A live client picker screenshot requires access to that client. Both still follow repository routing, artifacts and approval rules.

Sources:
_ask/docs/codex-integration.md

## 34 — Cursor: use stage commands and local rules

**Stage command**

/01-grill
Clarify the same CSV feature in Cursor Agent chat.

**Continue at the right stage**

/05-plan
Plan from the accepted specification; preserve the authorized endpoint.

**Shared instructions**

sync generates Cursor commands and Codex skills from the same stage sources and local overlays.

### Presenter notes

34. Cursor: use stage commands and local rules
75:00–76:00 (1 min)

These are editable usage examples, not screenshots of a Codex or Cursor client. No editor or browser surface was exposed to the UI connector during this update. Repository files verify the generated surfaces: .agents/skills/kit-01-grill/SKILL.md and .cursor/commands/01-grill.md. Explain the dollar prefix in Codex and slash prefix in Cursor; do not type either as a shell command. A live client picker screenshot requires access to that client. Both still follow repository routing, artifacts and approval rules.

Sources:
_ask/docs/codex-integration.md

## 35 — Keep project settings through upgrades

**Local behavior**

Put project-specific stage additions in .agents/ask.local/. Keep product files separate from generated kit files.

**Project checks**

Keep required application checks in .agents/verification.yaml. The kit’s own test preset is not automatically your app’s test plan.

**Explicit upgrade**

Upgrade to a chosen tag or commit, review the diff and rerun checks. Consumer-owned work, specs, pins and overlays are preserved by policy.

### Presenter notes

35. Keep project settings through upgrades
76:00–77:00 (1 min)

Explain kit-owned versus consumer-owned paths. An upgrade is not a blind update from main. --skip-prepare skips dependency installation, not necessarily generated projections or migrations. Legacy consumers may need a documented target-checkout upgrade. A pinned skill version should be upgraded deliberately; never use latest for critical methods.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask upgrade --version <chosen-tag-or-commit>
```

Sources:
_ask/docs/developer-guide.md

## 36 — Optional tools: know what they prove

**Engineering Model and UI**

Browse decisions, tasks and relationships. A label such as done is declared state; it does not replace recorded test execution.

**Exact references**

A qualified reference names one owner, item and revision. It does not silently switch to the latest version.

**Experiment records**

record-run attaches a measured value to exact source and configuration. It does not run the experiment for you.

### Presenter notes

36. Optional tools: know what they prove
77:00–79:00 (2 min)

The Engineering Model is an optional organizing sidecar, not the canonical behavior or execution authority. Guarded edits use the expected snapshot digest. Invalid working state may show a last-validated, noneditable snapshot. The workbench does not automatically implement work or repair invalid definitions. Use actual screenshots only when the relationships have been checked; otherwise discuss the data model without claiming a working demo.

Example commands; replace placeholders and run only in the intended demo repository:
```bash
./ask model validate --work-id orders-csv
./ask model show --work-id orders-csv
./ask ui
```

Sources:
_ask/docs/developer-guide.md

## 37 — The same export in Superpowers

**Before coding**

Brainstorm the need, approve a short or full design, then review the plan and select the execution method.

**During work**

Choose fresh implementer/reviewer contexts per task, or implement inline and get a fresh final review. Both use tests and a progress ledger.

**At the end**

Verify the branch and choose merge, push/PR or keep it. This integration decision is different from Karband’s semantic acceptance record.

### Presenter notes

37. The same export in Superpowers
79:00–82:00 (3 min)

Comparison is pinned to the neighboring Superpowers checkout at 22f0b463e7a5e579904dd6211a520321035526f7. Do not use an old description that calls it prompt-only or claims it has no recovery state. This version has per-plan ledgers, review packages and explicit inline execution. Small entirely clear tasks can bypass a full brainstorming conversation; project-sized designs get a builder check, short designs do not.

Sources:
_ask/docs/askit-vs-superpowers.md
Superpowers exact source: https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/executing-plans/SKILL.md
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md

## 38 — Choosing a workflow for your team

**Karband**

Use it when the team needs explicit approval records, reviewed task/test mappings and completion checks tied to exact source. Budget for the records and runner support.

**Superpowers**

Use it when a design, plan and ledger with native project tools fit the team. Inline work reduces fresh contexts but removes independent per-task review.

**Combining them**

Choose one workflow owner. A borrowed skill must not bypass its scope-change rules, writer boundaries or evidence requirements.

### Presenter notes

38. Choosing a workflow for your team
82:00–84:00 (2 min)

These are judgments from the inspected designs, not benchmarks. Superpowers execution permits many recorded rulings on plan ambiguity while keeping the spec binding; Karband escalates semantic and policy changes explicitly. Neither approach authorizes silent destructive operations. There is no measured claim here that one is faster, cheaper or produces fewer defects. Ask which record the audience would need to hand this export to another team.

Sources:
_ask/docs/askit-vs-superpowers.md
Superpowers exact source: https://github.com/obra/superpowers/tree/22f0b463e7a5e579904dd6211a520321035526f7
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/executing-plans/SKILL.md
https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md

## 39 — Exercise: a late change request

**The new request**

“Also export customer email and send this report every morning.” The filtered CSV work is already approved.

**Work in pairs**

Identify the changed expectation, the required human decision, affected tasks and tests, and anything that should be a separate workstream.

**Discuss your answer**

Do not implement first and explain later. Show a bounded proposal that the support team can understand and choose.

### Presenter notes

39. Exercise: a late change request
84:00–88:00 (4 min)

Give pairs two minutes, then use two minutes to discuss. Email adds data/access implications and changes columns; scheduling adds behavior, delivery and operational questions and may warrant a separate stream. A good answer preserves the current approved export, presents the changed intent/spec together where linked, updates task/test obligations after approval, and does not falsify prior execution evidence. Accept alternatives with a clear rationale.

Sources:
_ask/docs/developer-guide.md

## 40 — A handoff another developer can use

**Find the agreement**

What was requested, why it matters, what was excluded and which changes were approved.

**Find the proof**

Which task produced the code, which tests actually ran, which revision was reviewed and what limits remain.

**Choose the next step**

Accept, request changes or start a separately authorized follow-up. Use the developer guide as your desk reference.

### Presenter notes

40. A handoff another developer can use
88:00–90:00 (2 min)

Use the last minute for one question and one bounded next action. Ask a participant to explain the case without reading chat history. Reference _ask/docs/developer-guide.md for detailed flags and troubleshooting, and _ask/docs/askit-vs-superpowers.md for the version-pinned comparison. Do not describe this workshop’s teaching export as a delivered production feature.

Sources:
_ask/docs/developer-guide.md
