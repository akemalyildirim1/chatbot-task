SHELL=/bin/bash
.DEFAULT_GOAL := default

.PHONY: install
install:
	@echo "Installing Production Dependencies."
	pip install poetry
	poetry install --without dev

.PHONY: install-dev
install-dev:
	@echo "Installing Development Dependencies."
	pip install poetry
	poetry install

.PHONY: lint
lint:
	SKIP=no-commit-to-branch pre-commit run --all-files

.PHONY: coverage
coverage:
	@echo "Test coverage."
	bash scripts/test.sh

.PHONY: run
run:
	@echo "Running the application."
	poetry run uvicorn src.main:app --reload
