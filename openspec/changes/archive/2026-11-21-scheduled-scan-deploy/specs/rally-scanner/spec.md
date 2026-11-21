# Spec Delta

## MODIFIED Requirements

### Requirement: Polite API access

The scanner SHALL send every request to `https://booking.roadsurfer.com/api/en` with
an `X-Requested-Alias` header that matches the route. It SHALL send requests one at a
time, each after a configurable delay (0.5 s by default) plus a random jitter of up to
20% of it. After HTTP 429 it SHALL retry after a jittered wait of at least one minute
that grows with each attempt.

#### Scenario: Default scan pacing

- **WHEN** the scanner runs without `--delay`
- **THEN** requests are sent sequentially, at least 0.5 s apart

#### Scenario: Rate limited

- **WHEN** a request fails with HTTP 429
- **THEN** the scanner waits at least one minute, longer before each later retry,
  and gives up after five attempts

#### Scenario: Wrong route alias

- **WHEN** a request fails with HTTP 404
- **THEN** the scanner gives up on that request without retrying

## ADDED Requirements

### Requirement: Blocked scan detection

After a scan, the scanner SHALL print the number of requests, failed requests and
HTTP 429 responses, and the scan duration. A request counts as failed when the
scanner gives up on it. When more than 10% of the requests failed, the scanner SHALL
exit with a non-zero status and SHALL NOT write the `--json-out` or `--map` file.

#### Scenario: Healthy scan

- **WHEN** a scan with `--json-out offers.json --map index.html` finishes with at most
  10% failed requests
- **THEN** the scanner prints the request count, the failed count and the duration,
  writes both files and exits with status 0

#### Scenario: Blocked scan

- **WHEN** more than 10% of the requests of a scan fail
- **THEN** the scanner prints the request count, the failed count and the duration,
  exits with a non-zero status and writes neither the `--json-out` nor the `--map`
  file
