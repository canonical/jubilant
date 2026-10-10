import pathlib

import pytest

import jubilant

from . import mocks


def test_machine(run: mocks.Run):
    run.handle(['juju', 'ssh', '1', 'echo bar'], stdout='bar\n')
    juju = jubilant.Juju()

    output = juju.ssh(1, 'echo bar')
    assert output == 'bar\n'


def test_unit(run: mocks.Run):
    run.handle(['juju', 'ssh', 'ubuntu/0', 'echo', 'foo'], stdout='foo\n')
    juju = jubilant.Juju()

    output = juju.ssh('ubuntu/0', 'echo', 'foo')
    assert output == 'foo\n'


def test_container(run: mocks.Run):
    run.handle(
        ['juju', 'ssh', '--container', 'snappass', 'snappass-test/0', 'echo', 'foo'],
        stdout='foo\n',
    )
    juju = jubilant.Juju()

    output = juju.ssh('snappass-test/0', 'echo', 'foo', container='snappass')
    assert output == 'foo\n'


def test_user(run: mocks.Run):
    run.handle(['juju', 'ssh', 'usr@ubuntu/0', 'echo', 'foo'], stdout='foo\n')
    juju = jubilant.Juju()

    output = juju.ssh('ubuntu/0', 'echo', 'foo', user='usr')
    assert output == 'foo\n'


def test_ssh_options(run: mocks.Run):
    run.handle(
        [
            'juju',
            'ssh',
            '--no-host-key-checks',
            '--ssh-key',
            '/path/to/juju.key',
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
        'ubuntu/0',
        'echo',
        'foo',
        host_key_checks=False,
        ssh_key=pathlib.Path('/path/to/juju.key'),
        ssh_options=['-i', '/path/to/private.key'],
    )
    assert output == 'foo\n'


def test_ssh_key(run: mocks.Run):
    run.handle(
        ['juju', 'ssh', '--ssh-key', '/path/to/private.key', 'ubuntu/0', 'echo', 'foo'],
        stdout='foo\n',
    )
    juju = jubilant.Juju()

    output = juju.ssh('ubuntu/0', 'echo', 'foo', ssh_key=pathlib.Path('/path/to/private.key'))
    assert output == 'foo\n'


def test_type_error():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.ssh('ubuntu/0', 'ls', ssh_options='invalid')
