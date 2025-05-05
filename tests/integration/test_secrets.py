import datetime
import json

import jubilant


def test_add_secret(juju: jubilant.Juju):
    uri = juju.add_secret(
        'sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.'
    )

    output = juju.cli('show-secret', 'sec1', '--reveal', '--format', 'json')
    result = json.loads(output)
    secret = result[uri.unique_identifier]
    assert secret['name'] == 'sec1'
    assert secret['description'] == 'A description.'
    assert secret['content']['Data'] == {'username': 'usr', 'password': 'hunter2'}


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
    expected_values = [
        {
            'name': 'sec1',
            'username': 'usr',
            'password': 'hunter2',
            'info': 'A description.',
            'revision': 1,
        },
        {
            'name': 'sec2',
            'username': 'usr2',
            'password': 'hunter3',
            'info': 'A new description.',
            'revision': 2,
        },
    ]
    secrets = juju.secrets()

    assert isinstance(secrets, list)
    assert len(secrets) > 0
    for i, secret in enumerate(secrets):
        assert secret.revision == expected_values[i]['revision']
        assert secret.name == expected_values[i]['name']
        assert secret.owner == '<model>'
        assert secret.description == expected_values[i]['info']
        assert secret.created.year == datetime.datetime.now().year


def test_show_secret(juju: jubilant.Juju):
    secret = juju.show_secret(name_or_uri='sec1')

    assert secret.revision == 1
    assert secret.owner == '<model>'
    assert secret.name == 'sec1'
    assert secret.description == 'A description.'
    assert secret.created.year == datetime.datetime.now().year
    assert secret.created == secret.updated
    assert secret.content == {'username': 'usr', 'password': 'hunter2'}

    secret_again = juju.show_secret(name_or_uri=secret.uri)
    assert secret == secret_again
