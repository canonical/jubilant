
# We're using Make as a command runner, so always make (avoids need for .PHONY)
MAKEFLAGS += --always-make

help:  # Display help
	@echo "Usage: make [target] [ARGS='additional args']\n\nTargets:"
	@awk -F'#' '/^[a-z-]+:/ { sub(":.*", "", $$1); print " ", $$1, "#", $$2 }' Makefile | column -t -s '#'

all: format lint unit  # Run all quick, local commands

# Please keep the list below in alphabetical order.

coverage-html:  # Write and open HTML coverage report from last unit test run
	uv run coverage html
	open htmlcov/index.html 2>/dev/null

docs:  # Build documentation
	MAKEFLAGS='' $(MAKE) -C docs run

fix:  # Fix linting issues
	uv run ruff check --fix

format:  # Format the Python code
	uv run ruff format

install-dev:  # Install development tooling
	uv tool install codespell
	uv tool install ruff
	uv tool install zizmor

integration-k8s:  # Run K8s integration tests on Juju, eg: make integration ARGS='-k test_deploy'
	uv run pytest tests/integration -vv --log-level=INFO --log-format="%(asctime)s %(levelname)s %(message)s" -m 'not machine' $(ARGS)

integration-machine:  # Run machine integration tests on Juju, eg: make integration-machine ARGS='-k test_ssh'
	uv run pytest tests/integration -vv --log-level=INFO --log-format="%(asctime)s %(levelname)s %(message)s" -m machine $(ARGS)

lint:  # Perform linting and static type checks
	uv run ruff check
	uv run ruff format --diff
	uv run pyright

pack:  # Pack charms used by integration tests (requires charmcraft)
	cd tests/integration/charms/testdb && charmcraft pack
	cd tests/integration/charms/testapp && charmcraft pack

publish-test:  # Publish to TestPyPI
	rm -rf dist
	uv build
	uv publish --publish-url=https://test.pypi.org/legacy/ --token=$(UV_PUBLISH_TOKEN_TEST)

unit:  # Run unit tests, eg: make unit ARGS='tests/unit/test_deploy.py'
	uv run pytest tests/unit -vv --cov=jubilant $(ARGS)
