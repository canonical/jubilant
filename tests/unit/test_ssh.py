import pytest

import jubilant

from . import mocks


def test_machine(run: mocks.Run):
    run.handle(['juju', 'ssh', '1', 'echo bar'], stdout='bar\n')
    juju = jubilant.Juju()

    output = juju.ssh('echo bar', machine=1)
    assert output == 'bar\n'


def test_unit(run: mocks.Run):
    run.handle(['juju', 'ssh', 'ubuntu/0', 'echo', 'foo'], stdout='foo\n')
    juju = jubilant.Juju()

    output = juju.ssh('echo', 'foo', unit='ubuntu/0')
    assert output == 'foo\n'


def test_container(run: mocks.Run):
    run.handle(
        ['juju', 'ssh', '--container', 'snappass', 'snappass-test/0', 'echo', 'foo'],
        stdout='foo\n',
    )
    juju = jubilant.Juju()

    output = juju.ssh('echo', 'foo', unit='snappass-test/0', container='snappass')
    assert output == 'foo\n'


def test_user(run: mocks.Run):
    run.handle(['juju', 'ssh', 'usr@ubuntu/0', 'echo', 'foo'], stdout='foo\n')
    juju = jubilant.Juju()

    output = juju.ssh('echo', 'foo', unit='ubuntu/0', user='usr')
    assert output == 'foo\n'


def test_ssh_options(run: mocks.Run):
    run.handle(
        [
            'juju',
            'ssh',
            '--no-host-key-checks',
            'ubuntu/0',
            '-i',
            '/path/to/private.key',
            'echo',
            'foo',
        ],
        stdout='foo\n',
    )
    juju = jubilant.Juju()

    output = juju.ssh(
        'echo',
        'foo',
        unit='ubuntu/0',
        host_key_checks=False,
        ssh_options=['-i', '/path/to/private.key'],
    )
    assert output == 'foo\n'


def test_type_errors():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.ssh('cmd')
    with pytest.raises(TypeError):
        juju.ssh('cmd', unit='ubuntu/0', machine=0)
    with pytest.raises(TypeError):
        juju.ssh(unit='ubuntu/0')
