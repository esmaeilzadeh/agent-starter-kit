# Explore Map: disconnected red diagnostic

## Destination

Replace the empty completion error for an unreachable red-source commit with a useful diagnostic.

## Notes

The card includes a concrete reproduction, root cause, and explicit instruction to preserve the existing evidence. The evidence-policy alternatives are outside this bounded fix.

## Decisions so far

Keep the current ancestor requirement. Treat exit status 1 from `git merge-base --is-ancestor` as the non-ancestor condition and name both relevant commit IDs.

## Not yet specified

The broader policy for rejecting or retaining disconnected attempts and whether identical trees can establish lineage remains unresolved.

## Out of scope

That broader evidence contract and any report deletion or rewriting.

## Handoff to Intent

Implement only the diagnostic. Keep the card parked for its unresolved evidence-contract investigation.
