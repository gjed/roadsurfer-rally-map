# Tasks

## 1. Vendor

- [ ] 1.1 Copy `leaflet.js`, `leaflet.css`, `images/` and `LICENSE` from the leaflet 1.9.4 npm package to `vendor/leaflet/` and add `VERSION`
- [ ] 1.2 Exclude `vendor/` from `end-of-file-fixer` and `trailing-whitespace`, and add `vendor/** -text` to `.gitattributes`

## 2. Template

- [ ] 2.1 Load `vendor/leaflet/leaflet.css` and `vendor/leaflet/leaflet.js` by relative path

## 3. Documentation

- [ ] 3.1 Document the vendored version, source, update procedure and where `vendor/` must sit

## 4. Validation

- [ ] 4.1 sha256 of each vendored file matches the npm tarball and the GitHub release zip
- [ ] 4.2 `grep -c unpkg rally-map.template.html` prints 0
- [ ] 4.3 With unpkg.com blocked, the served map shows tiles, route lines and the default marker icon, and makes no request to unpkg.com
- [ ] 4.4 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [ ] 4.5 `openspec validate --strict --all` passes
