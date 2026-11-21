# Projection redesign authorization — 2026-11-03

The user resumed this stopped workstream with “continue based on decision,”
referring to the decision to investigate selective item projections. This
supersedes the saved stop boundary for this scoped work.

## Scope

Diagnose and address the failed savings result by making the frozen journeys
read only the exact items needed to answer their unchanged questions. Preserve
all source, approval, execution, and log evidence; verify its exact provenance
before projecting it. Re-run the same tokenizer and strict aggregate token and
metadata-byte thresholds. Keep the AskIt kit workflow disabled while changing
AskIt itself.

The benchmark report remains a failure until a new equivalent-evidence replay
passes both thresholds. This authorization does not accept the workstream or
change its approved intent, frozen questions, corpus, accounting, or thresholds.

## Reproduction and diagnosis

The retained run `work/shorter-hashes/benchmark/results/fab05ca/report.json`
reproduces the acceptance miss: 16,598 → 29,023 agent-input tokens and
195,626 → 235,031 metadata bytes. Its review journey grew from 10,128 to 22,042
tokens. The replay script registers each whole source file as a
`prose-item/1` snapshot and calls `refs show` on that snapshot, so it measures
whole-file responses rather than selected item projections. The generated
responses include the complete 54,671-byte test-plan response and
27,260-byte plan response. The saved catalogs contain only whole-file
snapshots for these inputs.
