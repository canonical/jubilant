from __future__ import annotations

from typing import cast

import jubilant
from jubilant import statustypes

from . import helpers


def test_integrate_and_remove_relation(juju: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'), base='ubuntu@22.04')
    juju.deploy(helpers.find_charm('testapp'), base='ubuntu@22.04')

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    if juju.cli_major_version == 2:
        assert status.apps['testdb'].relations['db'][0] == 'testapp'
        assert status.apps['testapp'].relations['db'][0] == 'testdb'
    else:
        assert isinstance(status, jubilant.Status)
        db_relation = cast(
            'list[statustypes.AppStatusRelation]', status.apps['testdb'].relations['db']
        )
        app_relation = cast(
            'list[statustypes.AppStatusRelation]', status.apps['testapp'].relations['db']
        )
        assert db_relation[0].related_app == 'testapp'
        assert app_relation[0].related_app == 'testdb'
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    juju.remove_relation('testdb', 'testapp')
    juju.wait(
        lambda status: (
            not status.apps['testdb'].relations and not status.apps['testapp'].relations
        )
    )
