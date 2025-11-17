import json

import jubilant
from tests.unit.fake_modelinfo import (
    FULL_MODELINFO,
    MINIMAL_MODELINFO,
)

from . import mocks


def test_full(run: mocks.Run):
    run.handle(
        ['juju', 'show-model', '--format', 'json'],
        stdout=json.dumps(FULL_MODELINFO),
    )
    juju = jubilant.Juju()
    info = juju.show_model()

    assert info == jubilant.ModelInfo(
        name='admin/t',
        short_name='t',
        model_uuid='910dff48-2bc2-4007-858b-e382d2fcdc0f',
        model_type='iaas',
        controller_uuid='82fa1bd2-e1a6-4aeb-87c3-5aaed212d4ff',
        controller_name='localhost-localhost',
        is_controller=False,
        cloud='localhost',
        life='alive',
        region='localhost',
        type='lxd',
        status=jubilant.modeltypes.ModelStatusInfo(
            current='available',
            since='18 hours ago',
        ),
        users={
            'admin': jubilant.modeltypes.ModelUserInfo(
                access='admin', last_connection='58 minutes ago', display_name='admin'
            )
        },
        agent_version='3.6.10',
        credential=jubilant.modeltypes.ModelCredential(
            name='localhost', owner='admin', cloud='localhost', validity_check='valid'
        ),
        supported_features=[
            jubilant.modeltypes.SupportedFeature(
                name='juju', description='the version of Juju used by the model', version='3.6.10'
            )
        ],
    )


def test_minimal(run: mocks.Run):
    run.handle(
        ['juju', 'show-model', '--format', 'json'],
        stdout=json.dumps(MINIMAL_MODELINFO),
    )
    juju = jubilant.Juju()
    info = juju.show_model()

    assert info == jubilant.ModelInfo(
        name='admin/min',
        short_name='min',
        model_uuid='910dff48-2bc2-4007-858b-e382d2fcdc0e',
        model_type='caas',
        controller_uuid='82fa1bd2-e1a6-4aeb-87c3-5aaed212d4fe',
        controller_name='ctrl',
        is_controller=True,
        cloud='aws',
        life='dying',
    )


def test_model_attribute(run: mocks.Run):
    run.handle(
        ['juju', 'show-model', '--format', 'json', 'ctrl:mdl'],
        stdout=json.dumps(MINIMAL_MODELINFO),
    )
    juju = jubilant.Juju(model='ctrl:mdl')
    info = juju.show_model()

    assert info.model_uuid == '910dff48-2bc2-4007-858b-e382d2fcdc0e'


def test_model_arg(run: mocks.Run):
    run.handle(
        ['juju', 'show-model', '--format', 'json', 'mdlarg'],
        stdout=json.dumps(MINIMAL_MODELINFO),
    )

    juju = jubilant.Juju()
    info = juju.show_model('mdlarg')
    assert info.model_uuid == '910dff48-2bc2-4007-858b-e382d2fcdc0e'

    juju = jubilant.Juju(model='ctrl:mdl')
    info = juju.show_model('mdlarg')
    assert info.model_uuid == '910dff48-2bc2-4007-858b-e382d2fcdc0e'
