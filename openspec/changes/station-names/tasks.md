# Tasks

- [ ] Language-aware `get()` and one `/rally/stations` request per page language after the English list
- [ ] `names` on each record's `from` and `to`, only where a language differs; per-language fallback to English
- [ ] A failed language request counts toward `MAX_FAILED` and falls back to English
- [ ] `sname()` label helper in the page; `place()` shows it, `placeKey()` keeps the English key
- [ ] Use the label at every display site and keep `.name` at every key site
- [ ] Station selects: English values, localised labels, sorted on the label
- [ ] Tests: records with and without `names`, keys unchanged, fallback, failed language request
- [ ] README: API notes and the interface languages
- [ ] Live check on a narrow window: `names` present, six more requests; page and feeds checked
