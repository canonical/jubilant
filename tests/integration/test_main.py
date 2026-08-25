"""End-to-end tests for the jubilant CLI (jubilant/_main.py)."""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import uuid

import pytest

import jubilant

# The entry point script installed by setuptools always lives in the same bin/
# directory as the Python executable.  Using this path means we do not rely on
# the venv being activated, PATH, or ``python -m jubilant`` (which requires a
# __main__.py that this package intentionally does not have).
_JUBILANT_BIN = str(pathlib.Path(sys.executable).parent / 'jubilant')


def run_cli(*args: str, model: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run the jubilant CLI entry-point script as a subprocess.

    Resolves the script via the same interpreter directory as pytest, so the
    correct venv is always used without requiring it to be activated.
    """
    cmd = [_JUBILANT_BIN, *args]
    if model is not None:
        cmd += ['--model', model]
    return subprocess.run(cmd, capture_output=True, text=True)


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju) -> None:
    """Deploy a charm so there is real, active status to evaluate expressions against."""
    juju.deploy('snappass-test')
    juju.wait(jubilant.all_active)


def test_wait_already_active(juju: jubilant.Juju) -> None:
    """Happy path: ready condition is already true, exit code should be 0."""
    result = run_cli('wait', 'jubilant.all_active(status)', model=juju.model)
    assert result.returncode == 0


def test_wait_successes(juju: jubilant.Juju) -> None:
    """--successes 1 exits as soon as a single success is recorded."""
    result = run_cli('wait', 'jubilant.all_active(status)', '--successes', '1', model=juju.model)
    assert result.returncode == 0


def test_wait_error_condition(juju: jubilant.Juju) -> None:
    """--error True fires immediately, exit code should be 1."""
    result = run_cli('wait', 'False', '--error', 'True', '--timeout', '10', model=juju.model)
    assert result.returncode == 1


def test_wait_timeout(juju: jubilant.Juju) -> None:
    """Ready expression never becomes true; timeout fires, exit code should be 124."""
    result = run_cli('wait', 'False', '--timeout', '3', '--delay', '1', model=juju.model)
    assert result.returncode == 124


def test_wait_unknown_model() -> None:
    """A model name that does not exist produces a non-zero exit code."""
    unknown = f'no-such-model-{uuid.uuid4().hex[:8]}'
    result = run_cli('wait', 'True', model=unknown)
    assert result.returncode != 0


def test_version() -> None:
    """version sub-command prints a semver string and exits 0."""
    result = run_cli('version')
    assert result.returncode == 0
    assert re.match(r'^\d+\.\d+\.\d+$', result.stdout.strip())


def test_invalid_argument(juju: jubilant.Juju) -> None:
    """An unrecognised flag produces a non-zero exit code."""
    result = run_cli('wait', '--unknown-flag', model=juju.model)
    assert result.returncode != 0


def test_wait_app_scoped_condition(juju: jubilant.Juju) -> None:
    """App-scoped condition: jubilant.all_agents_idle(status, 'snappass-test')."""
    result = run_cli('wait', "jubilant.all_agents_idle(status, 'snappass-test')", model=juju.model)
    assert result.returncode == 0


def test_wait_exception_in_expression(juju: jubilant.Juju) -> None:
    """An expression that raises an exception exits non-zero and logs the exception."""
    result = run_cli('wait', '0/0', model=juju.model)
    assert result.returncode != 0
    assert 'ZeroDivisionError' in result.stderr


def test_wait_undefined_name_in_expression(juju: jubilant.Juju) -> None:
    """An expression referencing an out-of-scope name exits non-zero and logs a NameError."""
    result = run_cli('wait', 'os.name', model=juju.model)
    assert result.returncode != 0
    assert 'NameError' in result.stderr


def test_quiet_still_prints_errors(juju: jubilant.Juju) -> None:
    """--quiet suppresses INFO output but still prints ERROR-level messages (e.g. timeout)."""
    result = run_cli(
        'wait', 'False', '--timeout', '3', '--delay', '1', '--quiet', model=juju.model
    )
    assert result.returncode == 124
    assert 'timed out' in result.stderr


def test_verbose_emits_debug_output(juju: jubilant.Juju) -> None:
    """--verbose produces DEBUG-level log lines on stderr.

    The DEBUG formatter is ``%(asctime)s %(levelname)s %(name)s %(message)s``,
    which includes the word ``DEBUG`` in every line.  The INFO formatter omits
    the level, so checking for ``DEBUG`` distinguishes the two paths.
    """
    result = run_cli('wait', 'jubilant.all_active(status)', '--verbose', model=juju.model)
    assert result.returncode == 0
    assert 'DEBUG' in result.stderr


def test_default_emits_info_output(juju: jubilant.Juju) -> None:
    """Default verbosity emits the 'Ready condition succeeded' INFO message on stderr."""
    result = run_cli('wait', 'jubilant.all_active(status)', model=juju.model)
    assert result.returncode == 0
    assert 'Ready condition succeeded' in result.stderr


def test_quiet_suppresses_info_output(juju: jubilant.Juju) -> None:
    """--quiet suppresses the INFO 'Ready condition succeeded' message."""
    result = run_cli('wait', 'jubilant.all_active(status)', '--quiet', model=juju.model)
    assert result.returncode == 0
    assert 'Ready condition succeeded' not in result.stderr
