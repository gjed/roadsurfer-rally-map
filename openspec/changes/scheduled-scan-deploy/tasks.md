# Tasks

## 1. Scanner

- [ ] 1.1 Add jitter to the per-request delay and minute-scale backoff after HTTP 429
- [ ] 1.2 Count requests, failed requests and 429 responses, and print a summary line with the duration
- [ ] 1.3 Exit non-zero without writing `--json-out` or `--map` when more than 10% of the requests fail

## 2. Workflow

- [ ] 2.1 Add `.github/workflows/scan.yml` with the scheduled scan, the Pages artifact, the `offers` artifact and the deploy job
- [ ] 2.2 Ignore `_site/`

## 3. Documentation

- [ ] 3.1 Document the delay, jitter, backoff, threshold, runtime and the published map in the README

## 4. Validation

- [ ] 4.1 With `urlopen` and `time.sleep` stubbed: 429 backs off for minutes with jitter, retries succeed, non-429 4xx fails fast, failures are counted, and a blocked scan writes no file
- [ ] 4.2 A real `--from 1 --delay 5` scan prints the summary line
- [ ] 4.3 The same scan without network exits non-zero and writes neither file
- [ ] 4.4 `actionlint` passes on `scan.yml`
- [ ] 4.5 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [ ] 4.6 `openspec validate --strict --all` passes
