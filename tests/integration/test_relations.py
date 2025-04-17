from __future__ import annotations

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
