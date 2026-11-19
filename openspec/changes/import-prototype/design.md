# Design

## Context

The prototype has two files. `roadsurfer-rally.py` calls
`https://booking.roadsurfer.com/api/en` and, with `--map FILE`, reads the sibling
`rally-map.template.html` and replaces the literal `/*DATA*/[]` with the JSON offer
records. The API is unofficial and rate limited.

## Goals / Non-Goals

**Goals:**

- Ship the prototype unchanged so later changes have a known baseline.
- Make a clean clone runnable and lint-clean.

**Non-Goals:**

- Behaviour changes, CLI cleanup (#5), vendoring Leaflet (#6), CI.

## Decisions

- **Verbatim import, then a separate style commit.** Keeping `ruff format` output out
  of the import commit lets readers diff the import against the source byte for
  byte. The style commit changes formatting only.
- **Ruff defaults.** Use ruff without a config file: the default line length (88) and
  the default rule set (E4, E7, E9, F). The prototype passes them unchanged, so no
  rule is weakened. Wider rule sets can come later with their own fixes.
- **Template contract unchanged.** The template keeps `const DATA = /*DATA*/[];` and
  stays next to the script, because `run()` finds it through
  `Path(__file__).with_name(...)`.
- **Pristine LICENSE.** The standard Apache 2.0 text, unmodified, so GitHub detects
  `apache-2.0`.
- **Markdown lint follows the gjed pattern.** mdformat with gfm and tables, plus
  pymarkdown with MD013 and MD033 disabled, as in the existing gjed repos.

## Risks / Trade-offs

- The unofficial API may change or block clients. Mitigation: the README states
  that the API is unofficial and documents its known behaviour.
- A full scan makes about 850 sequential requests at a 0.5 s delay and takes
  minutes. This is deliberate, to avoid HTTP 429. `--from` and `--to` narrow the
  scan.
