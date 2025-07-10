from __future__ import annotations

import jubilant

from . import helpers


def test_offer_and_consume(juju: jubilant.Juju, model2: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.offer(f'{juju.model}.testdb', endpoint='db', name='testdbx')

    model2.deploy(helpers.find_charm('testapp'))
    model2.consume(f'{juju.model}.testdbx', 'dbalias')
    model2.integrate('dbalias', 'testapp')

    status = juju.wait(jubilant.all_active)
    assert status.apps['testdb'].app_status.message == 'relation created'

    status2 = model2.wait(jubilant.all_active)
    assert status2.apps['testapp'].relations['db'][0].related_app == 'dbalias'
    assert status2.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'
    assert status2.app_endpoints['dbalias'].relations['db'][0] == 'testapp'
