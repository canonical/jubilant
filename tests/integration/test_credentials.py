import json

import jubilant


def test_add_credential(juju: jubilant.Juju):
    credential = {
        'credentials': {
            'aws': {
                'cred1': {
                    'auth-type': 'access-key',
                    'access-key': 'fake-access-key',
                    'secret-key': 'fake-secret-key',
                }
            }
        }
    }
    juju.add_credential('aws', credential, client=True)

    stdout = juju.cli('credentials', '--format', 'json', include_model=False)
    result = json.loads(stdout)
    creds = result['client-credentials']['aws']['cloud-credentials']['cred1']
    assert creds['details']['access-key'] == 'fake-access-key'
