# Cross-machine evidence handoff

The missing-evidence failure reproduces in a normal clone of this branch:
`load_accepted` reports `migration_required: missing coordinator accepted-tests ref`.
The old checkpoint exporter omitted accepted-test authority even when the source
machine had it. Copying the branch or `work/` did not restore private progress refs.

The corrected exporter includes the checkpoint, accepted-test authority and its
history, and the workflow catalog when present. Import publishes checkpoint and
authority refs atomically and preserves conflicting local authority. The regression
`RecoveryTests.test_bundle_transfers_accepted_authority_and_private_progress`
checks a real fresh clone, accepted-contract loading, private progress restoration,
repeat import, conflict rejection, and mode 0600 under umask 000.

## Retained evidence identities

- Source under aggregate verification: `ae0d443d75cfc2145e28ae75a71d8cf01d432ff5`.
- Checkpoint: `1f1ec069eb47dbc63a2b2526f46d2ef2b8aed6bd`.
- Retained state revision: 119.
- Accepted-test authority: `768d42f27894017c109213285aede23e89105e7c`.
- Accepted-test obligations: 40.
- Private bundle basename: `1f1ec069eb47dbc63a2b2526f46d2ef2b8aed6bd.bundle`.
- Bundle SHA-256: `53aa9b83b10fdc8f5eb54f5cb88f9bdd88d88cdb8467109ca597b7c052b0a7f4`.
- Bundle size: 7,903,776 bytes; permissions: 0600.
- Source-machine custody directory:
  `/home/mohamad/.local/state/askit/transfers/client-security-hardening/` (0700).

The bundle contains `refs/ask/inner-loop/client-security-hardening`,
`refs/ask/accepted-tests/client-security-hardening`, and all five existing
`refs/ask/accepted-tests-history/client-security-hardening/*` refs. These are
transfer identities, not a new acceptance or a verification pass. New aggregate
output after checkpoint revision 119 remains separate from this retained snapshot.

## Receiving machine

Transfer the private bundle as well as the source branch containing the corrected
importer. Check its SHA-256 against this handoff, then run:

```sh
./ask inner-loop checkpoint-import client-security-hardening /private/path/1f1ec069eb47dbc63a2b2526f46d2ef2b8aed6bd.bundle
./ask inner-loop status client-security-hardening
ASK_WORK_ID=client-security-hardening ./ask verify
```

Full transfer instructions: [`_ask/docs/inner-loop-evidence.md`](../../_ask/docs/inner-loop-evidence.md#moving-work-to-another-machine).
Raw logs remain in the private bundle. This committed handoff supplies their
transfer identity without publishing their contents or recreating approvals.
