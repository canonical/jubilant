from __future__ import annotations

import uuid

import jubilant


def test_show_model(juju: jubilant.Juju):
    assert juju.model is not None
    info = juju.show_model()
    assert info.name.endswith('/' + juju.model)
    assert info.short_name == juju.model
    assert not info.is_controller
    assert info.status.current == 'available'
    uuid.UUID(info.model_uuid)  # will raise ValueError if invalid
    uuid.UUID(info.controller_uuid)

    info_model = juju.show_model(juju.model)
    assert info_model.model_uuid == info.model_uuid


def test_user_qualified_model_name_is_transparent(juju: jubilant.Juju):
    """Jubilant forwards ``[<controller>:][<user>/]<model>`` to the Juju CLI verbatim."""
    assert juju.model is not None
    info = juju.show_model()
    user, _, _ = info.name.rpartition('/')
    assert user, f'expected qualified model name, got {info.name!r}'
    controller = info.controller_name

    info_user = juju.show_model(f'{user}/{juju.model}')
    assert info_user.model_uuid == info.model_uuid
    info_full = juju.show_model(f'{controller}:{user}/{juju.model}')
    assert info_full.model_uuid == info.model_uuid

    juju_qual = jubilant.Juju(model=f'{user}/{juju.model}')
    assert juju_qual.show_model().model_uuid == info.model_uuid
    juju_full = jubilant.Juju(model=f'{controller}:{user}/{juju.model}')
    assert juju_full.show_model().model_uuid == info.model_uuid
