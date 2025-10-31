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
