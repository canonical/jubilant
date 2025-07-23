import json

import jubilant
from tests.unit.fake_secrets import MULTIPLE_SECRETS

from . import mocks


def test_get_secrets(run: mocks.Run):
    run.handle(['juju', 'secrets', '--format', 'json'], stdout=json.dumps(MULTIPLE_SECRETS))
    juju = jubilant.Juju()

    response = juju.secrets()
    assert len(response) == 2
    assert response[0].revision == 2
    assert response[0].owner == '<model>'
    assert response[0].name == 'admin-account'
    assert response[0].created.day == response[0].updated.day


def test_get_empty_secrets(run: mocks.Run):
    run.handle(['juju', 'secrets', '--format', 'json'], stdout=json.dumps({}))
    juju = jubilant.Juju()

    response = juju.secrets()
    assert response == []


def test_get_secrets_with_owner(run: mocks.Run):
    run.handle(['juju', 'secrets', '--owner', 'user', '--format', 'json'], stdout=json.dumps({}))
    juju = jubilant.Juju()

    response = juju.secrets(owner='user')
    assert response == []
