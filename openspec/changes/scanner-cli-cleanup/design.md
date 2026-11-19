# Design

## Context

`run()` fetches the offers, prints them, updates the seen-state file, optionally
calls `notify-send` and, with `--map`, substitutes the offer records into
`rally-map.template.html`. `main()` loops forever with `--watch`. Rendering therefore
always needs a full scan and network access.

## Goals / Non-Goals

**Goals:**

- Keep only the options listed in #5, each with unchanged semantics.
- Render the map from a file without network access.
- Keep the pure helpers importable without side effects so #9 can test them.

**Non-Goals:**

- Scan metadata such as `scanned_at` (#4), vendoring Leaflet (#6), tests and CI.

## Decisions

- **Remove `--watch`.** It is in neither list of #5 and only serves a local polling
  setup. Scheduled scans belong to CI (#2). Without it the `--start` default no longer
  goes stale during a long run, and `--notify` has no loop to serve.
- **Data file shape.** `--json-out` writes `{"offers": [...]}`, where `offers` holds
  exactly the records the map embeds. A top-level object leaves room for metadata
  (#4) without breaking readers. No metadata keys are added now.
- **Code shape.** `run()` prints the listing and returns the records. A new
  `render(records, path)` holds the template substitution and the `</` escaping.
  `main()` either loads `--from-json` and renders, returning before the station list
  is fetched, or scans, then writes `--json-out` and renders `--map` as requested.
  Nothing runs at import time.
- **Argument checks.** `--from-json` requires `--map`, and rejects `--list`,
  `--json-out`, `--from`, `--to` and `--prices`, because it only renders. `--start`
  and `--end` have defaults and are ignored when rendering.
- **UTF-8 file I/O.** The template, the map and the data file are read and written
  with `encoding="utf-8"`, since the records use `ensure_ascii=False` and station
  names are not ASCII-only.
- **`resolve()` unchanged.** It still exits on an unknown station; the split does not
  need it to raise.

## Risks / Trade-offs

- Users of the removed options get an argparse error. → The project is new and the
  options were local-only; the README documents the remaining CLI.
