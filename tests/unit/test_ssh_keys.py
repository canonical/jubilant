from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_ssh_keys_empty(run: mocks.Run):
    run.handle(
        ['juju', 'ssh-keys', '--format', 'json'],
        stdout='[]',
    )
    juju = jubilant.Juju()

    keys = juju.ssh_keys()
    assert keys == []


def test_ssh_keys_normal(run: mocks.Run):
    run.handle(
        ['juju', 'ssh-keys', '--format', 'json'],
        stdout="""[
  {
    "fingerprint": "45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4",
    "comment": "user@host"
  },
  {
    "fingerprint": "c2:3d:92:da:59:14:e8:de:5f:e2:54:14:a7:17:e1:fa",
    "comment": "alice@workstation"
  }
]""",
    )
    juju = jubilant.Juju()

    keys = juju.ssh_keys()

    assert len(keys) == 2
    assert keys[0].fingerprint == '45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4'
    assert keys[0].comment == 'user@host'
    assert keys[0].key is None
    assert keys[1].fingerprint == 'c2:3d:92:da:59:14:e8:de:5f:e2:54:14:a7:17:e1:fa'
    assert keys[1].comment == 'alice@workstation'
    assert keys[1].key is None


def test_ssh_keys_full(run: mocks.Run):
    run.handle(
        ['juju', 'ssh-keys', '--format', 'json', '--full'],
        stdout="""[
  {
    "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB",
    "fingerprint": "45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4",
    "comment": "user@host"
  }
]""",
    )
    juju = jubilant.Juju()

    keys = juju.ssh_keys(full=True)

    assert len(keys) == 1
    assert keys[0].fingerprint == '45:7f:33:2c:10:4e:6c:14:e3:a1:a4:c8:b2:e1:34:b4'
    assert keys[0].comment == 'user@host'
    assert keys[0].key == 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAB'
