# Contributing

How to set up the repo, run the checks and open a pull request. The conventions
(rate limits, OpenSpec, commits, `vendor/`) are in [AGENTS.md](AGENTS.md); they apply
to people and agents alike.

## Setup

You need Python 3.8 or newer, `make` and [pre-commit](https://pre-commit.com/). The
scanner uses only the standard library, so there is nothing else to install.

```sh
git clone https://github.com/gjed/roadsurfer-rally-map.git
cd roadsurfer-rally-map
pip install pre-commit
pre-commit install
```

`pre-commit install` runs the hooks (ruff, ruff-format, mdformat, pymarkdown and the
generic file checks) on every commit.

## Run the checks

```sh
make test     # unit tests, offline
make lint     # all pre-commit hooks on all files
make map      # render index.html offline
make serve    # open http://127.0.0.1:8000/ to look at it
```

Without an `offers.json`, `make map` renders the test fixture
`tests/fixtures/offers.json` and says so. `make scan` fetches real data: it makes
about 850 sequential requests to the live API and takes several minutes, so run it
only when you need fresh offers. Run `make` alone to list the targets.

## Pull requests

1. Open or pick an issue. For a behaviour change, write an OpenSpec change under
   `openspec/changes/` (see [AGENTS.md](AGENTS.md#openspec-workflow)).
1. Branch from `main` and make atomic, signed, signed-off Conventional Commits
   (`git commit -S -s`).
1. Run `make lint test map` and fix what they report.
1. Open the PR against `main`, assign it to `gjed` and write `Closes #N` in the body.
1. Wait for the PR check (lint, tests, fixture render and page checks) to pass.

## Reporting problems

Use the [issue forms](https://github.com/gjed/roadsurfer-rally-map/issues/new/choose)
for bugs and feature requests.
