from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_single(run: mocks.Run):
    run.handle(
        ['juju', 'add-ssh-key', 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user@host'],
    )
    juju = jubilant.Juju()

    juju.add_ssh_key('ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user@host')


def test_multiple(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-ssh-key',
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user1@host',
            'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAC user2@host',
        ],
    )
    juju = jubilant.Juju()

    juju.add_ssh_key(
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB user1@host',
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAC user2@host',
    )
