
.PHONY: help
help:
	@echo "Usage: make [target]\n\nTargets:"
	@awk -F: '/^[a-z]+:/ { print "   ", $$1 }' Makefile

# Run all quick, local commands
.PHONY: all
all: format lint static unit

# Build documentation
.PHONY: docs
docs:
	uv export --group docs >docs/requirements.txt
	uv run --group docs sphinx-build docs/ docs/_build/html

# Fix linting issues
.PHONY: fix
fix:
	uv run ruff check --fix

# Format the Python code
.PHONY: format
format:
	uv run ruff format

# Run integration tests (slow, require real Juju)
.PHONY: integration
integration:
	uv run pytest test/integration

# Perform linting
.PHONY: lint
lint:
	uv run ruff check
	uv run ruff format --diff

# Check static types
.PHONY: static
static:
	uv run pyright

# Run quick unit tests
.PHONY: unit
unit:
	uv run pytest test/unit --cov=jubilant
