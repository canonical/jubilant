import jubilant

from . import mocks
from .fake_statuses import MINIMAL_JSON, MINIMAL_STATUS, SNAPPASS_JSON


def test_minimal_no_model(run: mocks.Run):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.status()

    assert status == MINIMAL_STATUS


def test_minimal_with_model(run: mocks.Run):
    run.handle(['juju', 'status', '--model', 'mdl', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju(model='mdl')

    status = juju.status()

    assert status == MINIMAL_STATUS


def test_real_status(run: mocks.Run):
    run.handle(['juju', 'status', '--format', 'json'], stdout=SNAPPASS_JSON)
    juju = jubilant.Juju()

    status = juju.status()

    assert status.model.type == 'caas'
    assert status.apps['snappass-test'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].leader
