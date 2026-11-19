import json

import jubilant
from tests.unit.fake_secrets import (
    SINGLE_SECRET,
    SINGLE_SECRET_REVEALED,
    SINGLE_SECRET_REVEALED_JUJU35,
    SINGLE_SECRET_REVISIONS,
    SINGLE_SECRET_WITH_ACCESS,
)

from . import mocks


def test_get_secret(run: mocks.Run):
    run.handle(
        ['juju', 'show-secret', 'example-charm-secret', '--format', 'json'],
        stdout=json.dumps(SINGLE_SECRET),
    )
    juju = jubilant.Juju()
    response = juju.show_secret('example-charm-secret')

    uri, secret = next(iter(SINGLE_SECRET_REVEALED.items()))
    assert secret

    assert response.uri == f'secret:{uri}'
    assert response.name == secret.get('name')
    assert response.label == secret.get('label')
    assert response.owner == secret.get('owner')
    assert response.rotates
    assert response.rotation == secret.get('rotation')
    assert response.revision == secret.get('revision')
    assert response.description == secret.get('description')
    assert response.created.year == response.updated.year
    assert response.expires == secret.get('expires')
    assert response.access is None
    assert response.revisions is None


def test_get_secret_with_reveal(run: mocks.Run):
    run.handle(
        ['juju', 'show-secret', 'example-charm-secret', '--format', 'json', '--reveal'],
        stdout=json.dumps(SINGLE_SECRET_REVEALED),
    )
    juju = jubilant.Juju()
    response = juju.show_secret('example-charm-secret', reveal=True)

    _, secret = next(iter(SINGLE_SECRET_REVEALED.items()))
    assert secret

    assert hasattr(response, 'content')
    assert response.content == {'password': 'secret', 'username': 'admin'}
    assert response.checksum == secret.get('checksum')


def test_get_secret_with_reveal_juju35(run: mocks.Run):
    run.handle(
        ['juju', 'show-secret', 'example-charm-secret', '--format', 'json', '--reveal'],
        stdout=json.dumps(SINGLE_SECRET_REVEALED_JUJU35),
    )
    juju = jubilant.Juju()
    response = juju.show_secret('example-charm-secret', reveal=True)

    _, secret = next(iter(SINGLE_SECRET_REVEALED.items()))
    assert secret

    assert hasattr(response, 'content')
    assert response.content == {'password': 'secret', 'username': 'admin'}
    assert response.checksum == ''


def test_get_secret_with_revisions(run: mocks.Run):
    run.handle(
        ['juju', 'show-secret', 'example-charm-secret', '--format', 'json', '--revisions'],
        stdout=json.dumps(SINGLE_SECRET_REVISIONS),
    )
    juju = jubilant.Juju()

    response = juju.show_secret('example-charm-secret', revisions=True)
    assert response.revisions
    assert response.revisions[0].revision == 1
    assert response.revisions[1].revision == 2
    assert response.revisions[0].backend == response.revisions[1].backend
    assert response.revisions[0].created.year == response.revisions[1].created.year
    assert response.revisions[0].updated.year == response.revisions[1].updated.year


def test_get_secret_with_revision(run: mocks.Run):
    run.handle(
        [
            'juju',
            'show-secret',
            'example-charm-secret',
            '--format',
            'json',
            '--revision',
            '2',
        ],
        stdout=json.dumps(SINGLE_SECRET_REVEALED),
    )
    juju = jubilant.Juju()

    juju.show_secret('example-charm-secret', revision=2)


def test_get_secret_with_access(run: mocks.Run):
    run.handle(
        ['juju', 'show-secret', 'example-charm-secret', '--format', 'json'],
        stdout=json.dumps(SINGLE_SECRET_WITH_ACCESS),
    )
    juju = jubilant.Juju()

    response = juju.show_secret('example-charm-secret')
    assert response.access
    assert len(response.access) == 1
    assert response.access[0].role
    assert response.access[0].scope
    assert response.access[0].target
