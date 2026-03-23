from __future__ import annotations

import pytest

import jubilant

from . import helpers


def test_integrate_and_remove_relation(juju: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.deploy(helpers.find_charm('testapp'))

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    assert status.apps['testdb'].relations['db'][0].related_app == 'testapp'
    assert status.apps['testapp'].relations['db'][0].related_app == 'testdb'
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    juju.remove_relation('testdb', 'testapp')
    juju.wait(
        lambda status: (
            not status.apps['testdb'].relations and not status.apps['testapp'].relations
        )
    )


def test_status_with_selectors(juju: jubilant.Juju):
    juju.wait(jubilant.all_active)

    try:
        status_testdb = juju.status('testdb')
    except jubilant.CLIError as exc:
        if 'patterns are not implemented' in str(exc).lower():
            pytest.skip('status selectors are not supported by this Juju client/server pair')
        raise

    assert 'testdb' in status_testdb.apps
    assert 'testapp' not in status_testdb.apps

    status_testapp = juju.status('testapp')
    assert 'testapp' in status_testapp.apps
    assert 'testdb' not in status_testapp.apps

    status_unit = juju.status('testdb/0')
    assert 'testdb' in status_unit.apps
    assert 'testdb/0' in status_unit.apps['testdb'].units
    assert 'testapp' not in status_unit.apps

    status_active = juju.status('active')
    assert status_active.apps

    status_error = juju.status('error')
    assert not status_error.apps
