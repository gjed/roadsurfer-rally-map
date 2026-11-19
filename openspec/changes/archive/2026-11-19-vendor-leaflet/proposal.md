# Proposal

## Why

The generated map loads Leaflet from `unpkg.com` every time someone opens it. If
unpkg is down, blocked or serves something else, the map breaks. Hosting a pinned
Leaflet release in the repo removes that runtime dependency
([#6](https://github.com/gjed/roadsurfer-rally-map/issues/6)).

## What Changes

- Add Leaflet 1.9.4, the latest stable 1.x release, under `vendor/leaflet/`:
  `leaflet.js`, `leaflet.css`, `images/` (five PNGs) and Leaflet's BSD-2-Clause
  `LICENSE`, byte-identical to the npm package. Record the version in
  `vendor/leaflet/VERSION`.
- Load `vendor/leaflet/leaflet.css` and `vendor/leaflet/leaflet.js` from
  `rally-map.template.html` by relative path instead of from unpkg.
- Exclude `vendor/` from the `end-of-file-fixer` and `trailing-whitespace` hooks, and
  mark `vendor/**` as `-text` in `.gitattributes`, so neither pre-commit nor git
  rewrites the upstream bytes.
- Document in the README the vendored version, its source, the manual update
  procedure, and that `vendor/` must sit next to the generated `index.html`.

Out of scope: map tiles (they stay on Esri World Street Map), inlining Leaflet into
the generated page, changes to `roadsurfer-rally.py`
([#5](https://github.com/gjed/roadsurfer-rally-map/issues/5)), Renovate configuration
([#11](https://github.com/gjed/roadsurfer-rally-map/issues/11)) and the Pages
workflow ([#2](https://github.com/gjed/roadsurfer-rally-map/issues/2)).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `rally-scanner`: the map loads Leaflet from the repository instead of a CDN.

## Impact

- New files under `vendor/leaflet/` (about 160 KB).
- The generated page finds Leaflet only when `vendor/` sits next to it: a local
  `--map` file must be written in the repo root, and the published page must ship
  `vendor/` alongside `index.html`.
- Viewing still needs internet access for the Esri tiles.
