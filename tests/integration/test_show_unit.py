from __future__ import annotations

import jubilant

from . import helpers


def test_show_unit(juju: jubilant.Juju, juju_version: jubilant.Version, empty_tar: str):
    juju.deploy(helpers.find_charm('testdb'))
    juju.deploy(helpers.find_charm('testapp'), resources={'test-file': empty_tar})

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)

    unit_name = next(iter(status.apps['testapp'].units))
    info = juju.show_unit(unit_name)

    assert isinstance(info, jubilant.UnitInfo)
    assert 'testapp' in info.charm
    assert info.leader in (True, False)
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
            and relation.local_unit.in_scope
            for relation in info.relation_info
        )
