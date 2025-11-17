from __future__ import annotations

import pytest

import jubilant
from tests.unit import mocks


def test_add_ssh_key_single(run: mocks.Run):
    run.handle(
        ['juju', 'add-ssh-key', 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user@host'],
        stdout='',
    )
    juju = jubilant.Juju()

    juju.add_ssh_key('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user@host')


def test_add_ssh_key_multiple(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-ssh-key',
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user1@host',
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAC user2@host',
        ],
        stdout='',
    )
    juju = jubilant.Juju()

    juju.add_ssh_key(
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user1@host',
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAC user2@host',
    )


def test_add_ssh_key_no_keys():
    juju = jubilant.Juju()

    with pytest.raises(TypeError, match='at least one SSH key must be specified'):
        juju.add_ssh_key()
