# Design

## Context

`rally-map.template.html` loads `leaflet.css` and `leaflet.js` 1.9.4 from unpkg. The
scanner writes the filled template wherever `--map` points. Leaflet's default marker
icons are resolved relative to the `leaflet.css` link.

## Goals / Non-Goals

**Goals:**

- The map renders with `unpkg.com` unreachable.
- The vendored release is pinned, unmodified and easy to update.

**Non-Goals:**

- A single-file page, offline tiles, automated updates.

## Decisions

- **Vendor files instead of inlining.** Inlining Leaflet into the generated page
  would make `index.html` a single file, but the scanner would have to read and embed
  `vendor/` and rewrite the CSS image URLs as data URIs. That means changing
  `roadsurfer-rally.py`, which [#5](https://github.com/gjed/roadsurfer-rally-map/issues/5)
  is rewriting. Relative paths need no scanner change. Inlining can come later as its
  own change.
- **Leaflet 1.9.4.** Every newer npm release is a 2.0 alpha or beta. 1.9.4 is the
  latest stable 1.x and is what the template already uses.
- **Source: the npm tarball.** `https://registry.npmjs.org/leaflet/-/leaflet-1.9.4.tgz`
  carries a registry integrity hash, and its `leaflet.js` is the file unpkg served.
  The files are cross-checked against the `leaflet.zip` asset of the GitHub release
  `v1.9.4`: all match except `leaflet.js`, whose banner comment in the zip names the
  build (`1.9.4+v1.d15112c`). The release zip has no `LICENSE`.
- **Version in one file.** `vendor/leaflet/VERSION` holds the version. The template
  paths carry no version, so an update touches the files and `VERSION` only, and a
  future Renovate regex manager ([#11](https://github.com/gjed/roadsurfer-rally-map/issues/11))
  can track one line.
- **Byte-identical upstream files.** `leaflet.css` and `LICENSE` use CRLF line
  endings, and `leaflet.js` has no final newline. `end-of-file-fixer` would rewrite
  `leaflet.js`, so `vendor/` is excluded from that hook and from
  `trailing-whitespace`. `.gitattributes` marks `vendor/**` as `-text` so git never
  converts line endings on checkout.
- **No sourcemap.** `leaflet.js` ends with a `sourceMappingURL` comment. Browsers
  fetch the map only when developer tools are open, so a 404 there costs nothing and
  `leaflet.js` stays unmodified.
- **No `L.Icon.Default.imagePath`.** Leaflet derives the image path from the
  `leaflet.css` link, which now points at `vendor/leaflet/`. The browser check
  confirms the default icon loads from there.

## Risks / Trade-offs

- A page copied away from the repo root loses Leaflet. Mitigation: the README states
  where `vendor/` must be.
- Security fixes in Leaflet need a manual update. Mitigation: the README documents
  the procedure, and #11 can automate it.
