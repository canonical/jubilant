# AGENTS.md

This file provides guidance to AI agents when working with code in this repository.

## Project Overview

Jubilant is a Python library that wraps the Juju CLI for use in charm integration tests. Methods map 1:1 to Juju CLI commands with a synchronous, type-annotated, Pythonic interface.

## Common Commands

```bash
make all                    # Format, lint, and unit test (run before committing)
make unit                   # Unit tests with coverage
make unit ARGS='tests/unit/test_deploy.py'           # Single test file
make unit ARGS='-k test_defaults'                    # Test by name pattern
make help                   # Run to see all available commands
```

## Code Style

- **Line length**: 99 characters
- **Quotes**: Single quotes
- **Docstrings**: Google style
- **Type hints**: Strict pyright mode; `from __future__ import annotations` in every file
- **Imports**: Import modules, not other objects, unless they are only used for type annotations
- **Target Python**: 3.8+
- **Comments**: Explain *why*, not *what*; if necessary for 'what', consider rewriting so that they are not

Ensure that `pre-commit` is installed (with the user's permission) so that style is enforced with every commit. If the user does not permit using `pre-commit`, *always* ensure that `make all` shows no issues before committing.

Read [the Charm Tech style guide](https://github.com/canonical/operator/blob/main/STYLE.md) if more clarification is required.

## Architecture

### Core Module: `jubilant/_juju.py`

The `Juju` class is the main entry point. Every public method except `wait` corresponds to a Juju CLI command. All commands are executed via `subprocess.run()` through the private `_cli()` method. Errors raise `CLIError` (subclass of `CalledProcessError`).

### Type System: `jubilant/statustypes.py`, `modeltypes.py`, `secrettypes.py`

Frozen dataclasses representing structured Juju output. Each has a `_from_dict()` class method for parsing JSON. These are all generated automatically from the Juju Go code, and should *never* be modified by AI.

### Wait Pattern: `jubilant/_all_any.py`

`Juju.wait(condition)` polls status until a callable condition returns True. Built-in helpers: `all_active()`, `any_blocked()`, `all_agents_idle()`, etc. Supports custom lambdas.

### Public API

Everything public is exported from `jubilant/__init__.py`. Internal modules use leading underscores. Do not add public symbols without updating `__init__.py`.

**Always** ensure backwards compatibility of the public API.

## Testing

### Unit Tests (`tests/unit/`)

- Mock `subprocess.run` using the custom `mocks.Run` helper in `tests/unit/mocks.py`
- Test command construction and output parsing, not real CLI execution
- No external dependencies needed

### Integration Tests (`tests/integration/`)

- Require a running Juju controller
- Machine-specific tests use `@pytest.mark.machine` marker
- Each test module gets a temporary Juju model via fixture:
  ```python
  @pytest.fixture(scope='module')
  def juju():
      with jubilant.temp_model() as juju:
          yield juju
  ```
- Test charms live in `tests/integration/charms/` and must be packed with `make pack`
