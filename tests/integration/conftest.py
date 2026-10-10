from __future__ import annotations

import pathlib
import tarfile
import tempfile
from collections.abc import Generator
from typing import cast

import pytest

import jubilant

from . import helpers


def pytest_addoption(parser: pytest.OptionGroup):
    parser.addoption(
        '--keep-models',
        action='store_true',
        default=False,
        help='keep temporarily-created models',
    )


@pytest.fixture(scope='module')
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju]:
    """Module-scoped pytest fixture that creates a temporary model."""
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    with jubilant.temp_model(keep=keep_models) as juju:
        yield juju
        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end='')


@pytest.fixture(scope='module')
def juju_version(juju: jubilant.Juju) -> jubilant.Version:
    """Module-scoped pytest fixture that returns the Juju CLI version."""
    return juju.version()


@pytest.fixture(scope='module')
def private_key_file(juju: jubilant.Juju) -> Generator[str]:
    """Module-scoped pytest fixture that adds an SSH key to the model and returns its path."""
    private_key_pem, public_key_ssh = helpers.generate_ssh_key_pair()

    with tempfile.NamedTemporaryFile(mode='w', delete=False, dir=juju._temp_dir) as f:
        f.write(private_key_pem)
        temp_file = f.name
    pathlib.Path(temp_file).chmod(0o600)

    try:
        juju.add_ssh_key(public_key_ssh)
        yield temp_file
    finally:
        juju.remove_ssh_key(public_key_ssh)
        pathlib.Path(temp_file).unlink(missing_ok=True)


@pytest.fixture(scope='module')
def ssh_key(request: pytest.FixtureRequest, juju_version: jubilant.Version) -> str | None:
    """Module-scoped pytest fixture that returns the path to pass as ``ssh_key``, if needed.

    From Juju 4.1, ``juju ssh`` and ``juju scp`` connect through the controller's SSH server,
    which requires a key registered in the model, including for Kubernetes models.
    """
    if juju_version.tuple < (4, 1, 0):
        return None
    return request.getfixturevalue('private_key_file')


@pytest.fixture(scope='module')
def model2(request: pytest.FixtureRequest) -> Generator[jubilant.Juju]:
    """Module-scoped pytest fixture that creates a (second) temporary model."""
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    with jubilant.temp_model(keep=keep_models) as juju:
        yield juju


@pytest.fixture
def empty_tar(tmp_path: pathlib.Path) -> Generator[str]:
    """Pytest fixture that creates an empty .tar file and returns its path."""
    path = str(tmp_path / 'empty.tar')
    with tarfile.open(path, 'w'):
        pass
    yield path
