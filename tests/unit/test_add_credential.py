import pathlib

import pytest

import jubilant

from . import mocks


def test_with_path_str(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--client', '--file', '/path/to/creds.yaml'])
    juju = jubilant.Juju()

    juju.add_credential('aws', '/path/to/creds.yaml', client=True)


def test_with_path_pathlib(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--client', '--file', '/path/to/creds.yaml'])
    juju = jubilant.Juju()

    juju.add_credential('aws', pathlib.Path('/path/to/creds.yaml'), client=True)


def test_with_yaml_dict(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'add-credential', 'aws', '--controller', 'cc', '--file', mock_file.name])
    juju = jubilant.Juju()

    credential = {'credentials': {'aws': {'mycred': {'auth-type': 'access-key'}}}}
    juju.add_credential('aws', credential, controller='cc')

    assert len(mock_file.writes) == 1
    assert 'auth-type: access-key' in mock_file.writes[0]


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-credential',
            'aws',
            '--client',
            '--controller',
            'mycontroller',
            '--region',
            'us-east-1',
            '--file',
            '/path/to/creds.yaml',
        ]
    )
    juju = jubilant.Juju()

    juju.add_credential(
        'aws',
        credential='/path/to/creds.yaml',
        client=True,
        controller='mycontroller',
        region='us-east-1',
    )


def test_neither_client_nor_controller():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.add_credential('aws', '/path/to/creds.yaml')  # type: ignore
