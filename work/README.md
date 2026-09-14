# work/

Per-workstream artifacts live under `work/<work-id>/` (explore-map, intent, plan, review, verification, acceptance, results).

Create a workstream with `./ask start-work <work-id>`.

These files are **branch-local**. List live plans with `./ask status` (workstreams from `agent/*` refs and archived `work/*` on the default branch; later cards from `.later/` on this checkout). Do not treat a single checkout as the workstream inventory.

A job found **during** another workstream is not live: write `.later/<slug>.md` and start it later with `./ask start-work`. See `.later/README.md`.
