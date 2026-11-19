# Tasks

## 1. Remove local-only features

- [ ] 1.1 Remove the seen-state file, the `NEW` flag, `--notify` and `--watch`, and drop `.roadsurfer-rally-seen.json` from `.gitignore`
- [ ] 1.2 Remove `--via`, `--detour`, `detour()`, its route filter and the `+Nkm` column
- [ ] 1.3 Remove the now unused `km()` helper and `import math`

## 2. Split scanning from rendering

- [ ] 2.1 Move the template substitution into `render(records, path)` and have `run()` return the records
- [ ] 2.2 Add `--json-out FILE` writing `{"offers": [...]}`
- [ ] 2.3 Add `--from-json FILE`, rendering with `--map` and no network access

## 3. Documentation

- [ ] 3.1 README: drop the seen-file paragraph, show `--help` verbatim, document the scan/render split

## 4. Validation

- [ ] 4.1 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [ ] 4.2 A `--from 1` scan gives the same offer count through `--map` on `origin/main` and through `--json-out` plus an offline `--from-json` render
- [ ] 4.3 `openspec validate --strict --all` passes
