# Tasks

## 1. Tooling

- [ ] 1.1 Add the `Makefile` with `help`, `scan`, `map` (fixture fallback), `serve`, `lint` and `test`
- [ ] 1.2 Git-ignore `/offers.json`

## 2. Documentation

- [ ] 2.1 Add `AGENTS.md`
- [ ] 2.2 Add `CONTRIBUTING.md`
- [ ] 2.3 Add the bug report and feature request issue forms and `config.yml`
- [ ] 2.4 Update the README: live map, workflows, `make` targets

## 3. Validation

- [ ] 3.1 From a clean copy: `make test`, offline `make map`, `make lint`, `make help` and `make -n scan serve`
- [ ] 3.2 `pre-commit run --all-files` with the repository and the global markdown config
- [ ] 3.3 `openspec validate --strict --all` passes after archiving
