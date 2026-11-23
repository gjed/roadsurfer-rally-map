# AGENTS.md

Instructions for AI coding agents working in this repo.

## What this repo is

A scanner and a map for [roadsurfer Rally](https://booking.roadsurfer.com/en/rally)
one-way campervan relocation offers. `roadsurfer-rally.py` (Python 3.8+, standard
library only) asks the roadsurfer booking API for every Rally route and its
timeframes. It prints the offers and can save them as JSON and render
`rally-map.template.html` into a self-contained Leaflet page. The workflow
`scan.yml` publishes that page to <https://gjed.github.io/roadsurfer-rally-map/>.

The API is unofficial and undocumented. The project is not affiliated with
roadsurfer.

## Layout

```text
roadsurfer-rally.py         scanner, JSON writer and map renderer
rally-map.template.html     map page template; render() fills /*DATA*/[], /*SCAN*/null
                            and /*RELEASE*/null
tests/                      offline unittest suite and fixtures/offers.json
vendor/leaflet/             unmodified upstream Leaflet
openspec/                   specs and changes (OpenSpec)
.github/workflows/          scan.yml (scheduled scan + Pages), release.yml
                            (semantic-release + Pages), pr-check.yml
.releaserc.json             semantic-release config
Makefile                    local entry points
```

## API notes

The base URL is `https://booking.roadsurfer.com/api/en`. Every request needs an
`X-Requested-Alias` header that matches the route, or the API answers with a 404
HTML page. The README section "API notes" has the table of paths and aliases and the
observed behaviour (7-day rallies, flat price, ranges longer than 7 days unavailable).
Keep that section current when the API changes.

## Rate limits

The API answers bursts with HTTP 429. Do not weaken these rules:

- Requests go out one at a time. Never parallelise them.
- Each request waits for `--delay` seconds plus up to 20% jitter. The default is
  0.5 s for local runs; `scan.yml` uses `--delay 5`.
- A scan with more than 10% failed requests (`MAX_FAILED`) exits with status 1 and
  writes no `--json-out` or `--map` file, so a blocked scan never replaces good data.
- Road distances come from OSRM, not roadsurfer: sequential `/table` requests at most
  one per second, with a User-Agent naming the project, and only for station pairs
  missing from the cache (`--road-cache`, default `road-distances.json`, git-ignored;
  `scan.yml` keeps it in an S3 bucket, with the Actions cache as the fallback; see the
  next section). A routing failure never counts toward
  `MAX_FAILED`: the pair falls back to the estimate and is not cached. `--from-json`
  never routes.
- A full scan is about 850 requests. Do not run one to test a change: use
  `--from-json` with the fixture, or a narrow `--from`/`--to`/`--start`/`--end`
  window.

## Road distance cache in S3

`scan.yml`'s build job restores `road-distances.json` from the Actions cache, then
downloads the S3 object `road-distances.json` over it, so the S3 copy wins when it
exists. After a scan that exited 0 it uploads the file and saves the Actions cache.
Authentication is GitHub OIDC (`aws-actions/configure-aws-credentials`, pinned to a
SHA) with the role in the Actions variable `ROAD_DISTANCE_CACHE_ROLE_ARN`; the bucket
is `ROAD_DISTANCE_CACHE_BUCKET`. The role trusts only `ref:refs/heads/main`, so
the workflow cannot reach AWS from a branch or a PR, and the bucket and role live in
`gjed/homelab-aws`. Keep these rules:

- The AWS steps stay in the build job. `id-token: write` is granted there only; the
  deploy job uses the `github-pages` environment, which changes the OIDC `sub` claim.
- An AWS failure only warns; it never fails or blocks the scan. Unset variables skip
  the AWS steps.
- The build job keeps its own concurrency group (`road-distance-scan`, not `pages`),
  so two scans never overwrite each other's upload.
- A blocked or crashed scan uploads nothing.
- `release.yml` never reads the bucket.

## Scan and render

Scanning needs the network; rendering does not.

- `--json-out FILE.json` saves the scanned offers.
- `--from-json FILE.json --map index.html` renders the page from that file without
  any request.

The JSON file is an object whose `offers` key holds the list of offer records, the
same records the page embeds. Each record has the timeframe, the booking link and
the pick-up and return stations with their coordinates; see
`tests/fixtures/offers.json` for a real example. A scan adds `km` (road distance) and
`km_estimated` (`true` for the straight-line × 1.3 fallback) to every record; records
without them, like the fixture's, render with the fallback labelled as an estimate.
Other top-level keys may be added
(for example scan metadata), so code that reads the file must look up `offers` and
ignore keys it does not know.

## Build, lint and test

```sh
make test     # python3 -m unittest discover -s tests -v, offline
make map      # render index.html from offers.json, or from the fixture
make serve    # preview at http://127.0.0.1:8000/
make lint     # pre-commit run --all-files
make scan     # full scan into offers.json; slow, hits the live API
```

The page loads Leaflet from `vendor/leaflet/` by relative path, so write and serve
`index.html` from the repo root. `offers.json`, `index.html` and `road-distances.json` are git-ignored.
The PR check (`pr-check.yml`) runs the same lint and tests, renders the fixture and
checks the generated page; run `make lint test map` before pushing.

Python 3.8 is the minimum, for the scanner and the tests. `ruff.toml` targets it and
the PR check's `python38` job runs the scanner and the tests on it
(`uv run --python 3.8 python -m unittest discover -s tests -v` locally). To change
the minimum, update README.md, CONTRIBUTING.md, AGENTS.md, `ruff.toml`, that job and
the Python 3.8 requirements in `openspec/specs/` together, through an OpenSpec change.

## OpenSpec workflow

Behaviour changes go through [OpenSpec](https://github.com/Fission-AI/OpenSpec):

1. Write the change under `openspec/changes/<name>/`: `proposal.md`, `tasks.md`,
   `design.md` when there are decisions to record, and spec deltas under `specs/`.
   Pure documentation needs no spec delta.
1. `openspec validate <name> --strict`, then implement and tick the tasks.
1. Archive in the same PR, before the final commit: `openspec archive <name> -y`,
   then `openspec validate --strict --all`.

## Commit conventions

- Conventional Commits: `<type>(<scope>): <subject>`, for example
  `fix(scanner): retry on HTTP 503` or `docs(readme): link the live map`.
- Every commit is signed off: `git commit -s`.
- Atomic commits: one logical change each. Stage files by explicit path, never
  `git add -A` or `git add .`.
- The project is experimental: never mark a commit as breaking (no `!`, no
  `BREAKING CHANGE` footer).

## Releases

`release.yml` runs semantic-release (`.releaserc.json`) on every push to `main`, so
the commit types decide the version:

- `feat` cuts a minor release, `fix` and `perf` a patch release.
- `docs`, `chore`, `ci`, `build`, `style`, `refactor` and `test` cut no release.
- The first release from the current history is `v1.0.0`: semantic-release starts at
  1.0.0 and no commit is marked breaking.

A release creates the tag `vX.Y.Z` and a GitHub release; it commits nothing to
`main`. Then the workflow renders the page with `--from-json` from the `offers`
artifact of the newest `scan.yml` run on `main` that uploaded one, and `--release vX.Y.Z`,
and deploys it. It never scans and never contacts roadsurfer: keep it that way. With
no such artifact the release job fails and nothing is deployed. `scan.yml` renders
with the latest release tag too, so the version stays on the page between releases.
Only the two deploy jobs share the concurrency group `pages`.

## vendor/

`vendor/` must stay byte-identical to the upstream release. Never edit or reformat
it. The pre-commit config excludes it from the whitespace and end-of-file hooks, and
`.gitattributes` marks it `-text` so git never converts line endings.
The update procedure is in the README section "Vendored Leaflet".

## Pull requests

- Assign the PR to `gjed`.
- Put `Closes #N` in the body for the issue it resolves.
- Keep a PR to one issue; for a behaviour change, include the OpenSpec change and its
  archive.
- The PR check must pass.
