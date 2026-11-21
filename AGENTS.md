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
rally-map.template.html     map page template; render() fills /*DATA*/[]
tests/                      offline unittest suite and fixtures/offers.json
vendor/leaflet/             unmodified upstream Leaflet
openspec/                   specs and changes (OpenSpec)
.github/workflows/          scan.yml (scheduled scan + Pages), pr-check.yml
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
- A full scan is about 850 requests. Do not run one to test a change: use
  `--from-json` with the fixture, or a narrow `--from`/`--to`/`--start`/`--end`
  window.

## Scan and render

Scanning needs the network; rendering does not.

- `--json-out FILE.json` saves the scanned offers.
- `--from-json FILE.json --map index.html` renders the page from that file without
  any request.

The JSON file is an object whose `offers` key holds the list of offer records, the
same records the page embeds. Each record has the timeframe, the booking link and
the pick-up and return stations with their coordinates; see
`tests/fixtures/offers.json` for a real example. Other top-level keys may be added
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
`index.html` from the repo root. `offers.json` and `index.html` are git-ignored.
The PR check (`pr-check.yml`) runs the same lint and tests, renders the fixture and
checks the generated page; run `make lint test map` before pushing.

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
