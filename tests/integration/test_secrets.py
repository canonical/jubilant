import datetime
import json

import jubilant


def test_add_secret(juju: jubilant.Juju):
    uri = juju.add_secret(
        'sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.'
    )

    output = juju.show_secret(uri, reveal=True)
    assert output.name == 'sec1'
    assert output.description == 'A description.'
    assert output.content == {'username': 'usr', 'password': 'hunter2'}


def test_update_secret(juju: jubilant.Juju):
    uri = juju.add_secret(
        'sec2', {'username': 'usr', 'password': 'hunter2'}, info='A description.'
    )
    juju.update_secret(
        'sec2', {'username': 'usr2', 'password': 'hunter3'}, info='A new description.'
    )

    output = juju.cli('show-secret', 'sec2', '--reveal', '--format', 'json')
    result = json.loads(output)
    secret = result[uri.unique_identifier]
    assert secret['name'] == 'sec2'
    assert secret['revision'] == 2
    assert secret['description'] == 'A new description.'
    assert secret['content']['Data'] == {'username': 'usr2', 'password': 'hunter3'}


def test_get_all_secrets(juju: jubilant.Juju):
    secrets = juju.secrets()
    assert len(secrets) == 2

    assert secrets[0].revision == 1
    assert secrets[0].name == 'sec1'
    assert secrets[0].owner == '<model>'
    assert secrets[0].description == 'A description.'
    assert secrets[0].created.year == datetime.datetime.now().year

    assert secrets[1].revision == 2
    assert secrets[1].name == 'sec2'
    assert secrets[1].owner == '<model>'
    assert secrets[1].description == 'A new description.'
    assert datetime.datetime.now(datetime.timezone.utc) - secrets[1].created < datetime.timedelta(
        hours=1
    )


def test_show_secret(juju: jubilant.Juju):
    secret = juju.show_secret('sec1')
    assert secret.revision == 1
    assert secret.owner == '<model>'
    assert secret.name == 'sec1'
    assert secret.description == 'A description.'
    assert datetime.datetime.now(datetime.timezone.utc) - secret.created < datetime.timedelta(
        hours=1
    )
    assert secret.created == secret.updated
    assert not hasattr(secret, 'content')

    secret = juju.show_secret('sec1', reveal=True)
    assert secret.content == {'username': 'usr', 'password': 'hunter2'}

    secret = juju.show_secret('sec2', reveal=True, revision=1)
    assert secret.content == {'username': 'usr', 'password': 'hunter2'}
    secret = juju.show_secret('sec2', reveal=True, revision=2)
    assert secret.content == {'username': 'usr2', 'password': 'hunter3'}

    secret = juju.show_secret('sec2', revisions=True)
    assert not hasattr(secret, 'content')
    assert secret.revisions
    assert len(secret.revisions) == 2
    assert secret.revisions[0].revision == 1
    assert secret.revisions[1].revision == 2

    secret_with_uri = juju.show_secret(secret.uri)
    assert secret.name == secret_with_uri.name
