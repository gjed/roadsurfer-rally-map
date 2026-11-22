# Tasks

## 1. Configuration

- [x] 1.1 Add a packageRule disabling major updates of the `executablebooks/mdformat` pre-commit hook, with the reason and the condition to re-enable it

## 2. Validation

- [x] 2.1 `renovate-config-validator --strict` passes
- [x] 2.2 A local `--platform=local` dry run no longer plans the mdformat 1.0.0 branch
- [x] 2.3 `pre-commit run --all-files` and `openspec validate --strict --all` pass
