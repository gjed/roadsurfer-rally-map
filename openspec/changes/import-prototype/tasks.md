# Tasks

## 1. Import

- [ ] 1.1 Copy `roadsurfer-rally.py` and `rally-map.template.html` verbatim from the prototype
- [ ] 1.2 Add `.gitignore` for `index.html`, `.roadsurfer-rally-seen.json`, `__pycache__/`

## 2. Linting

- [ ] 2.1 Add `.pre-commit-config.yaml` and `.pymarkdown.json`
- [ ] 2.2 Apply `ruff format` to the scanner in a separate style commit

## 3. Documentation and license

- [ ] 3.1 Add `README.md` with usage, API notes, known behaviour, disclaimer and license line
- [ ] 3.2 Add the standard Apache License 2.0 text as `LICENSE`

## 4. Validation

- [ ] 4.1 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [ ] 4.2 `python3 roadsurfer-rally.py --map index.html` writes `index.html`, which git ignores
- [ ] 4.3 `openspec validate --strict` passes
