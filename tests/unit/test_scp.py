import pathlib

import pytest

import jubilant

from . import mocks


def test_minimal(run: mocks.Run):
    run.handle(['juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju()

    juju.scp('SRC', 'DST')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'scp',
            '--container',
            'redis',
            '--no-host-key-checks',
            '--',
            '-r',
            '-C',
            'SRC',
            'DST',
        ]
    )
    juju = jubilant.Juju()

    juju.scp('SRC', 'DST', container='redis', host_key_checks=False, scp_options=['-r', '-C'])


def test_path_source(run: mocks.Run):
    run.handle(['juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju()

    juju.scp(pathlib.Path('SRC'), 'DST')


def test_path_destination(run: mocks.Run):
    run.handle(['juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju()

    juju.scp('SRC', pathlib.Path('DST'))


# The 'run' fixture mocks out the version call.
def test_type_error(run: mocks.Run):
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.scp('src', 'dst', scp_options='invalid')
