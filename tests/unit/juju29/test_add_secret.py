from __future__ import annotations

import pytest

import jubilant


def test_29():
    juju = jubilant.Juju(cli_version='2.9.52')

    with pytest.raises(NotImplementedError):
        juju.add_secret('sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.')
