from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_remove_ssh_key_by_fingerprint(run: mocks.Run):
    run.handle(
        ['juju', 'remove-ssh-key', '45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4'],
        stdout='',
    )
    juju = jubilant.Juju()

    juju.remove_ssh_key('45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4')


def test_remove_ssh_key_by_comment(run: mocks.Run):
    run.handle(
        ['juju', 'remove-ssh-key', 'user@host'],
        stdout='',
    )
    juju = jubilant.Juju()

    juju.remove_ssh_key('user@host')


def test_remove_ssh_key_multiple(run: mocks.Run):
    run.handle(
        ['juju', 'remove-ssh-key', 'user1@host', 'user2@host'],
        stdout='',
    )
    juju = jubilant.Juju()

    juju.remove_ssh_key('user1@host', 'user2@host')
