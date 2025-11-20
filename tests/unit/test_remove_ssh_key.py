from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_single(run: mocks.Run):
    run.handle(['juju', 'remove-ssh-key', 'user@host'])
    juju = jubilant.Juju()

    juju.remove_ssh_key('user@host')


def test_multiple(run: mocks.Run):
    run.handle(
        ['juju', 'remove-ssh-key', 'user1@host', 'user2@host'],
    )
    juju = jubilant.Juju()

    juju.remove_ssh_key('user1@host', 'user2@host')
