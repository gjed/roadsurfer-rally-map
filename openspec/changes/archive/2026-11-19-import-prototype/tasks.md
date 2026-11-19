# Tasks

## 1. Import

- [x] 1.1 Copy `roadsurfer-rally.py` and `rally-map.template.html` verbatim from the prototype
- [x] 1.2 Add `.gitignore` for `index.html`, `.roadsurfer-rally-seen.json`, `__pycache__/`

## 2. Linting

- [x] 2.1 Add `.pre-commit-config.yaml` and `.pymarkdown.json`
- [x] 2.2 Apply `ruff format` to the scanner in a separate style commit

## 3. Documentation and license

- [x] 3.1 Add `README.md` with usage, API notes, known behaviour, disclaimer and license line
- [x] 3.2 Add the standard Apache License 2.0 text as `LICENSE`

## 4. Validation

- [x] 4.1 `pre-commit run --all-files` passes with the repo config and the global markdown config
- [x] 4.2 `python3 roadsurfer-rally.py --map index.html` writes `index.html`, which git ignores
- [x] 4.3 `openspec validate --strict` passes
