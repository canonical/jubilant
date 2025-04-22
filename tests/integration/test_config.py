from __future__ import annotations

import contextlib

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


@contextlib.contextmanager
def fast_forward(juju: jubilant.Juju):
    """Context manager that temporarily speeds up update-status hooks."""
    old = juju.model_config()['update-status-hook-interval']
    juju.model_config({'update-status-hook-interval': '10s'})
    try:
        yield
    finally:
        juju.model_config({'update-status-hook-interval': old})


def test_model_config(juju: jubilant.Juju):
    assert juju.model_config()['update-status-hook-interval'] == '5m'
    with fast_forward(juju):
        assert juju.model_config()['update-status-hook-interval'] == '10s'
    assert juju.model_config()['update-status-hook-interval'] == '5m'


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
