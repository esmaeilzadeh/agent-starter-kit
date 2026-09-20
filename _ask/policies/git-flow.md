# Git-flow

`develop` is the integration branch. `agent/<work-id>` starts from `develop`.
Protected `main` is releasable. Agents prepare PRs, `release/<version>`
artifacts, and `work/<work-id>/release-evidence.md`. Humans authorize merge,
tag, and push to `main`.

| Branch | Role | Who advances |
| --- | --- | --- |
| `develop` | Integration and durable later-work | Agents prepare; human or agreed merge |
| `agent/<work-id>` | Workstream writer | `./ask start-work` from `develop` |
| `agent/<work-id>/task/<id>` | Optional isolated writer | Runner; fast-forward only onto coordinator |
| `release/<version>` | Release prep | Agent prepares; human authorizes |
| `main` | Releasable | Human merge, tag, push |
| `hotfix/*` | Production fix | From `main`; after human release, back-merge to `main` and `develop` |

`./ask start-work` fails closed when `develop` is missing.

Version tags: `vMAJOR.MINOR.PATCH` on `main`. Changelog path: `CHANGELOG.md`
(or the product’s existing changelog).

Later cards: commit `.later/<slug>.md` on `develop` and link a tracker issue.
Feature branches do not treat later cards as live workstreams.
