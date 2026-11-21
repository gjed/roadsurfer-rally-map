# Design

## Context

`get()` in `roadsurfer-rally.py` sleeps `DELAY` seconds (0.5 by default) before each
request, retries up to five times, gives up at once on a 4xx other than 429, and
waits `5 * (attempt + 1)` seconds after a 429. A failed request returns `None` and
the scan goes on with what it has, so a blocked scan still writes a map. A full scan
sends about 850 requests.

## Goals / Non-Goals

**Goals:**

- Publish a fresh map twice a week without manual steps.
- Stay well inside the API limits from a datacenter IP.
- Never publish the result of a blocked scan.

**Non-Goals:**

- Parallel requests, a faster scan, scan metadata on the page, a release workflow.

## Decisions

- **Jitter adds up to 20% to the delay.** Each request waits
  `DELAY + uniform(0, 0.2 * DELAY)`. The minimum gap stays `DELAY`, so the existing
  pacing guarantee holds, and requests do not arrive on an exact beat. With
  `--delay 5`, 850 requests take about 70 to 90 minutes including response time.
- **429 backoff in minutes.** After a 429 the scanner waits
  `60 * (attempt + 1) + uniform(0, 30)` seconds: about 1, 2, 3 and 4 minutes, so one
  request gives up after about 10 minutes at worst. Other errors keep the 2 s retry.
  A long block can push the job past `timeout-minutes`; the job then fails and
  nothing is deployed, which is the wanted outcome.
- **Count calls, not attempts.** `REQUESTS` counts `get()` calls, `FAILED` counts
  calls that returned `None`, and `RATE_LIMITED` counts 429 responses, as #3 asks for
  the 429 count. The failed share is `FAILED / REQUESTS`.
- **Threshold as a constant.** `MAX_FAILED = 0.10` follows the issue. A
  `--max-failed` option would change the supported options for no current user.
- **Check before writing.** The summary line is printed after the scan and before
  any file is written. Above the threshold the scanner exits with status 1 and
  writes neither file. The station-list failure prints the summary too before its
  existing non-zero exit, so a fully blocked run still logs its counts.
- **Clean Pages directory.** The workflow copies `index.html` and `vendor/` into
  `_site/` and uploads only that, so the checkout's scripts and specs are not
  published. `_site/` is git-ignored.
- **Scan data as its own artifact.** `offers.json` from `--json-out` is uploaded as
  the artifact `offers`, so a later workflow can re-render the page from it.
- **No base-URL override.** A forced failure on a runner uses a throwaway branch with
  a broken `BASE`; locally, the scan runs without network (`unshare -rn`).

## Risks / Trade-offs

- The API may block runner IPs outright. The scan then fails and the published page
  stays at the last good scan.
- The 10% threshold is a guess. It is a single constant and easy to change once the
  first runner runs show the real failure rate.
