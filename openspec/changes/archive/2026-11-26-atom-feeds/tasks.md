# Tasks

## 1. Scanner

- [x] 1.1 `--feeds DIR`: `all.xml` and `from-<slug>.xml`, `xml.etree.ElementTree`, Python 3.8
- [x] 1.2 Station slug rule; entry id, title, link and summary; `<updated>` from the scan
- [x] 1.3 `--from-json` accepts `--feeds` (with or without `--map`); a scan routes for it and a blocked scan writes none
- [x] 1.4 `scan.stations` lists the pick-up stations asked about; every station gets a feed, with no entries when it has no offers
- [x] 1.5 Unit tests: parse, counts, unique and stable ids, links, slugs, escaping, blocked scan

## 2. Publishing

- [x] 2.1 `scan.yml` and `release.yml` pass `--feeds feeds` and copy `feeds/` into `_site`
- [x] 2.2 `pr-check.yml` renders the fixture feeds and checks that they parse
- [x] 2.3 `<link rel="alternate" type="application/atom+xml">` in the template `<head>`, and `.gitignore`

## 3. Docs

- [x] 3.1 README "Feeds" section and usage text; AGENTS.md layout and publishing paths
