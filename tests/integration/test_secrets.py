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
