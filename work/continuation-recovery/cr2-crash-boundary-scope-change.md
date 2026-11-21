# CR-2 crash-boundary scope amendment

The user explicitly approved “Amend CR-T38 for checkpoint replay”. CR-T38
moves from CR-1 to CR-2 and changes from `regression` to `changed`, because the
assertion is being updated to require CR-2's checkpoint replay behavior after
interruption between checkpoint-ref publication and runtime-cache replacement.
It remains bound to CR-03 and CR-07. The owning test path
`_ask/tests/inner_loop_reliability.py` moves from CR-1 to CR-2 for this task.

The test is green on the current working branch because checkpoint behavior is
already implemented there. That does not establish behavior Red. CR-2 Red must
run from the immutable pre-implementation base with the amended assertion and
fail on the behavior assertion; an inherited green run is not relabeled Red.
No other task scope, criterion, or product intent changes.
