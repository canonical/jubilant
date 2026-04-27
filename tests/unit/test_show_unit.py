import json

import jubilant
from tests.unit.fake_unitinfo import FULL_UNITINFO, MINIMAL_UNITINFO

from . import mocks


def test_full(run: mocks.Run):
    run.handle(
        ['juju', 'show-unit', 'mysql/0', '--format', 'json'],
        stdout=json.dumps(FULL_UNITINFO),
    )
    juju = jubilant.Juju()
    info = juju.show_unit('mysql/0')

    assert info == jubilant.UnitInfo(
        workload_version='8.0.41',
        machine='0',
        relation_info=[
            jubilant.unittypes.UnitRelationInfo(
                endpoint='database',
                relation_id=5,
                related_endpoint='database',
                cross_model=False,
                application_data={'foo': 'bar'},
                local_unit=jubilant.unittypes.UnitRelationData(
                    in_scope=True,
                    data={'ingress-address': '10.0.0.1'},
                ),
                related_units={
                    'wordpress/0': jubilant.unittypes.UnitRelationData(
                        in_scope=True,
                        data={'egress-subnets': '10.1.1.1/32'},
                    )
                },
            )
        ],
        opened_ports=['3306/tcp'],
        public_address='10.0.0.1',
        charm='mysql',
        leader=True,
        life='alive',
        provider_id='mysql-0',
        address='10.0.0.1',
    )


def test_minimal(run: mocks.Run):
    run.handle(
        ['juju', 'show-unit', 'mysql/0', '--format', 'json'],
        stdout=json.dumps(MINIMAL_UNITINFO),
    )
    juju = jubilant.Juju()
    info = juju.show_unit('mysql/0')

    assert info == jubilant.UnitInfo(
        charm='mysql',
    )


def test_model_attribute(run: mocks.Run):
    run.handle(
        ['juju', 'show-unit', '--model', 'ctrl:mdl', 'mysql/0', '--format', 'json'],
        stdout=json.dumps(MINIMAL_UNITINFO),
    )
    juju = jubilant.Juju(model='ctrl:mdl')

    juju.show_unit('mysql/0')
