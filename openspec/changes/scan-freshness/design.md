# Design

## Context

`render(records, path)` replaces the literal `/*DATA*/[]` in
`rally-map.template.html` with the offer records, escaping `</` as `<\/`.
`--json-out` writes `{"offers": [...]}`. `summary()` prints the `REQUESTS`, `FAILED`
and `RATE_LIMITED` counters and blocks the scan above `MAX_FAILED`. The PR check
fails when `/*DATA*/[]` is left in the rendered page.

## Goals / Non-Goals

**Goals:**

- Show on the page when its data was scanned.
- Keep the metadata in the scan data file, so a re-render shows the scan time.
- Keep rendering data files written before this change.

**Non-Goals:**

- Changing the failure handling or the workflows; both already keep the last good
  map.
- A release tag or footer, or a relative age on the page.

## Decisions

- **Top-level `scan` object.** `--json-out` writes
  `{"scan": {...}, "offers": [...]}`. Keys: `finished_at`, `offers`, `requests`,
  `failed`, `rate_limited`, `start`, `end`, `from`, `to`. `offers` stays a plain list,
  so existing readers keep working. Recording the window and the origin/destination
  terms tells a reader whether a page covers everything or a filtered scan, at the
  cost of four small keys. `rate_limited` is already counted and printed, so it is
  stored too.
- **Finish time in UTC, second precision, `Z` suffix.** It is taken right after the
  last request, before the summary check, so it is the time the data was true.
- **A second placeholder.** The template gets `const SCAN = /*SCAN*/null;` next to
  `const DATA = /*DATA*/[];`, and `render(records, path, scan=None)` replaces both
  through one `embed()` helper that applies the `</` escaping. With no metadata the
  placeholder becomes `null`, which is also what the template says, so a page never
  depends on the placeholder being left in. Replacing `DATA` with one
  `{scan, offers}` object was rejected: it changes every `DATA` use in the page and
  the placeholder the PR check looks for.
- **Metadata is read, not regenerated, on `--from-json`.** The file's `scan` object is
  embedded as is. A missing `scan` key, or one that is not an object, renders the
  page with `SCAN = null` instead of failing, so `tests/fixtures/offers.json` and old
  artifacts keep working.
- **UTC on the page.** The toolbar shows `updated 2026-11-18 03:12 UTC ·` in a
  `#updated` span before `#count`. UTC matches the issue, the cron schedule and the
  JSON, and reads the same in every screenshot and for every viewer; with scans days
  apart the time-zone offset does not change how stale the data looks. The viewer's
  local time was rejected because a shared screenshot would no longer say which time
  it means. The tooltip shows the raw finish time, offers, requests and failed
  requests. The text is set with `textContent` and `title`, so the metadata is never
  parsed as HTML. The span takes over `margin-left: auto` from `#count`, so both stay
  right-aligned in the flex toolbar, and stays empty when `finished_at` is missing
  or unparsable.
- **No relative age.** "3 days ago" was rejected for now: it is computed from the
  viewer's clock, and the issue asks for the timestamp.

## Risks / Trade-offs

- A template edit that drops `/*SCAN*/null` leaves pages without a timestamp and no
  error; the unit tests check that the placeholder is replaced and decodes.
