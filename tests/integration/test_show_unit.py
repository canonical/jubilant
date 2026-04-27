from __future__ import annotations

import jubilant

from . import helpers


def test_show_unit(juju: jubilant.Juju, empty_tar: str):
    juju.deploy(helpers.find_charm('testdb'))
    juju.deploy(helpers.find_charm('testapp'), resources={'test-file': empty_tar})

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)

    unit_name = next(iter(status.apps['testapp'].units))
    info = juju.show_unit(unit_name)

    assert isinstance(info, jubilant.UnitInfo)
    assert info.charm == 'testapp'
    assert info.leader in (True, False)
    assert info.machine
    assert info.life == 'alive'
    assert any(
        relation.endpoint == 'db'
        and relation.related_endpoint == 'db'
        and any(unit.startswith('testdb/') for unit in relation.related_units)
        for relation in info.relation_info
    )
