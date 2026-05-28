from __future__ import annotations

import jubilant

from . import helpers


def test_integrate_and_remove_relation(juju: jubilant.Juju, empty_tar: str):
    juju.deploy(helpers.find_charm('testdb'))
    juju.deploy(helpers.find_charm('testapp'), resources={'test-file': empty_tar})

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    assert status.apps['testdb'].relations['db'][0].related_app == 'testapp'
    assert status.apps['testapp'].relations['db'][0].related_app == 'testdb'
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    juju.remove_relation('testdb', 'testapp')
    juju.wait(
        lambda status: not status.apps['testdb'].relations and not status.apps['testapp'].relations
    )


def test_show_unit(juju: jubilant.Juju, juju_version: jubilant.Version):
    juju.wait(jubilant.all_active)

    info = juju.show_unit('testapp/0')

    assert isinstance(info, jubilant.UnitInfo)
    assert info.charm == 'local:testapp-0'
    assert isinstance(info.leader, bool)
    assert info.machine or info.provider_id
    assert info.life == 'alive'

    if juju_version.major < 4:
        assert any(
            relation.endpoint == 'db'
            and relation.related_endpoint == 'db'
            and any(unit.startswith('testdb/') for unit in relation.related_units)
            for relation in info.relation_info
        )
    else:
        assert any(
            relation.endpoint == 'db'
            and relation.related_endpoint == 'db'
            and relation.local_unit is not None
            and relation.local_unit.in_scope
            for relation in info.relation_info
        )
