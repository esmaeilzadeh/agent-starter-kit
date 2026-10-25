# Scoped testing direction: continuation recovery only

Human direction on 2026-10-25:

> ignore all true red demand for each test. only try to write them and pass them (if they aleady passed fine)

Scope clarification:

> it is only for this work (Because it was a bug fix that was mistaken with a feature)

This direction applies only to the continuation-recovery bug fix. Write or retain meaningful tests and require passing results; tests that already pass are sufficient. Historical behavior Red evidence is not a requirement to create or reconstruct for each test. Preserve the existing historical records without inventing or relabeling outcomes. The direction supersedes conflicting per-test Red-first demands for this work only.

Continue the authorized CR-3 task using current passing evidence and required integration checks. This note changes the testing method; it does not add product scope or authorize CR-4 admission. Route: continuation of an existing bug fix, whose original reproduction is recorded in work/continuation-recovery/reproduction.md.
