from __future__ import annotations

import jubilant_backports as jubilant
from jubilant_backports import statustypes

from . import helpers


def test_integrate_and_remove_relation(juju: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.deploy(helpers.find_charm('testapp'))

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    db_relations = status.apps['testdb'].relations['db']
    app_relations = status.apps['testapp'].relations['db']
    assert isinstance(db_relations[0], statustypes.AppStatusRelation)
    assert isinstance(app_relations[0], statustypes.AppStatusRelation)
    if not juju._is_juju_2:
        # In Juju 2.9, none of the `AppStatusRelation` fields are provided.
        assert db_relations[0].related_app == 'testapp'
        assert app_relations[0].related_app == 'testdb'
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    juju.remove_relation('testdb', 'testapp')
    juju.wait(
        lambda status: (
            not status.apps['testdb'].relations and not status.apps['testapp'].relations
        )
    )
