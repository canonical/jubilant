from __future__ import annotations

import pathlib
import tempfile
import time
from typing import Generator

import pytest

import jubilant

from . import helpers

pytestmark = pytest.mark.machine


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju):
    juju.deploy('ubuntu')
    juju.wait(jubilant.all_active)


@pytest.fixture(scope='module')
def private_key_file(juju: jubilant.Juju) -> Generator[str]:
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


def test_exec(juju: jubilant.Juju):
    task = juju.exec('echo foo', machine=0)
    assert task.success
    assert task.return_code == 0
    assert task.stdout == 'foo\n'
    assert task.stderr == ''

    task = juju.exec('echo', 'bar', 'baz', machine=0)
    assert task.success
    assert task.stdout == 'bar baz\n'


def test_ssh(juju: jubilant.Juju, private_key_file: str):
    # The key is not available for use immediately. For now, just wait for a
    # moment. Waiting for `ssh-keys` to not be empty does not work as a solution.
    output = None
    for _ in range(60):
        try:
            output = juju.ssh('ubuntu/0', 'echo', 'UNIT', ssh_options=['-i', private_key_file])
        except jubilant.CLIError as e:  # noqa: PERF203
            if 'Permission denied (publickey).' not in e.stderr:
                raise
            time.sleep(1)
        else:
            break
    assert output == 'UNIT\n'

    output = juju.ssh(0, 'echo', 'MACHINE', ssh_options=['-i', private_key_file])
    assert output == 'MACHINE\n'


def test_add_and_remove_unit(juju: jubilant.Juju):
    juju.add_unit('ubuntu')
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps['ubuntu'].units) == 2)

    juju.remove_unit('ubuntu/1')
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps['ubuntu'].units) == 1)


def test_model_constraints(juju: jubilant.Juju):
    initial_constraints = juju.model_constraints()
    assert not initial_constraints
    juju.model_constraints(constraints={'mem': '1G', 'cores': 4})
    new_constraints = juju.model_constraints()
    assert new_constraints == {'mem': 1024, 'cores': 4}
