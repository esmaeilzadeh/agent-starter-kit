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
Export and import also reject missing authority before publishing an incomplete
transfer. The existing GC/transfer regression still proves checkpoint object
retention after deleting refs and pruning; it restores the retained authority ref
before exporting the complete handoff.

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

## Fresh-clone verification

The real bundle was imported into a disposable `git clone --no-local` of source
`ae0d443d75cfc2145e28ae75a71d8cf01d432ff5` using the corrected importer.
`load_accepted(clone, work_id, source_sha, source_sha)` loaded all 40 obligations;
`restore_cache(clone, work_id)` restored revision 119 with CSH-01 through CSH-10
all `integrated`. The clone had neither private ref before import. This check
restored the original recorded evidence; it did not run the behavior tests or
change the historical task outcomes.

Recovery verification: `python3 -m unittest _ask.tests.inner_loop_recovery`
passed all 48 tests in 534.764 seconds against the transfer implementation.
After adding the missing-authority guards, the two focused transfer tests passed
in 13.287 seconds. The original source's aggregate separately passed its 47
recovery tests in 493.181 seconds. These results do not claim an aggregate pass.

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
