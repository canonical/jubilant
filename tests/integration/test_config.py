from __future__ import annotations

import json

import pytest

import jubilant

from . import helpers


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.wait(
        lambda status: status.apps['testdb'].units['testdb/0'].workload_status.current == 'unknown'
    )


def test_config(juju: jubilant.Juju):
    config = juju.config('testdb')
    assert config['testoption'] == ''

    juju.config('testdb', {'testoption': 'foobar'})
    config = juju.config('testdb')
    assert config['testoption'] == 'foobar'


def test_trust(juju: jubilant.Juju):
    app_config = juju.config('testdb', app_config=True)
    assert app_config['trust'] is False

    # Test that the "trust" app_config value updates.
    juju.trust('testdb', scope='cluster')
    app_config = juju.config('testdb', app_config=True)
    assert app_config['trust'] is True

    juju.trust('testdb', remove=True, scope='cluster')
    app_config = juju.config('testdb', app_config=True)
    assert app_config['trust'] is False


def test_add_secret(juju: jubilant.Juju):
    uri = juju.add_secret(
        'sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.'
    )
    assert uri.startswith('secret:')

    output = juju.cli('show-secret', 'sec1', '--reveal', '--format', 'json')
    result = json.loads(output)
    secret = result[uri[len('secret:') :]]
    assert secret['name'] == 'sec1'
    assert secret['description'] == 'A description.'
    assert secret['content']['Data'] == {'username': 'usr', 'password': 'hunter2'}
