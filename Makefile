PYTHON  ?= python3
SCANNER := $(PYTHON) roadsurfer-rally.py
OFFERS  := offers.json
FIXTURE := tests/fixtures/offers.json

.DEFAULT_GOAL := help
.PHONY: help scan map serve lint test

help: ## List the targets
	@awk -F ':.*## ' '/^[a-z]+:.*## / { printf "  %-6s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

scan: ## Full scan of the roadsurfer API into offers.json (several minutes)
	$(SCANNER) --json-out $(OFFERS)

map: ## Render index.html from offers.json, or from the test fixture, offline
	@if [ -f $(OFFERS) ]; then src=$(OFFERS); else \
		src=$(FIXTURE); \
		echo "note: no $(OFFERS), rendering the test fixture $(FIXTURE); run 'make scan' for real data"; \
	fi; \
	echo "$(SCANNER) --from-json $$src --map index.html"; \
	$(SCANNER) --from-json $$src --map index.html

serve: ## Serve the repo root at http://127.0.0.1:8000/
	$(PYTHON) -m http.server --bind 127.0.0.1

lint: ## Run the pre-commit hooks on all files
	pre-commit run --all-files

test: ## Run the unit tests, as the PR check does
	$(PYTHON) -m unittest discover -s tests -v
