from __future__ import annotations

import jubilant

from . import helpers


def test_offer_and_consume(juju: jubilant.Juju, model2: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.offer(f'{juju.model}.testdb', endpoint='db', name='testdbx')

    out = juju.cli('offers')
    print('OFFERS1\n' + out)

    model2.deploy(helpers.find_charm('testapp'))
    model2.consume(f'{juju.model}.testdbx', 'dbalias')

    out = model2.cli('offers')
    print('OFFERS2\n' + out)

    model2.integrate('dbalias', 'testapp')

    out = juju.cli('offers')
    print('OFFERS1b\n' + out)

    status = juju.wait(jubilant.all_active)
    #    assert status.apps['testdb'].relations['db'][0].related_app == 'testapp'
    assert status.apps['testdb'].app_status.message == 'relation created'

    status2 = model2.wait(jubilant.all_active)
    #    assert status2.apps['testapp'].relations['db'][0].related_app == 'testdb'
    assert status2.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    out = juju.cli('offers')
    print('OFFERS1c\n' + out)
