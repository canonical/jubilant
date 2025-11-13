import pytest

import jubilant

from . import mocks


def test_with_file(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--client', '--file', '/path/to/creds.yaml'])
    juju = jubilant.Juju()

    juju.add_credential('aws', file='/path/to/creds.yaml', client=True)


def test_with_yaml_str(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'add-credential', 'aws', '--client', '--file', mock_file.name])
    juju = jubilant.Juju()

    yaml_str = 'credentials:\n  aws:\n    mycred:\n      auth-type: access-key\n'
    juju.add_credential('aws', yaml=yaml_str, client=True)

    assert mock_file.writes == [yaml_str]


def test_with_yaml_dict(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'add-credential', 'aws', '--client', '--file', mock_file.name])
    juju = jubilant.Juju()

    yaml_dict = {'credentials': {'aws': {'mycred': {'auth-type': 'access-key'}}}}
    juju.add_credential('aws', yaml=yaml_dict, client=True)

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
        client=True,
        controller='mycontroller',
        file='/path/to/creds.yaml',
        region='us-east-1',
    )


def test_neither_file_nor_yaml():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.add_credential('aws', client=True)  # type: ignore


def test_both_file_and_yaml():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.add_credential('aws', file='/path/to/creds.yaml', yaml='test')  # type: ignore


def test_neither_client_nor_controller():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.add_credential('aws', file='/f')  # type: ignore
