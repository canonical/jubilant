import pytest

import jubilant

from . import mocks


def test_with_file(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--file', '/path/to/creds.yaml'])
    juju = jubilant.Juju()

    juju.add_credential('aws', file='/path/to/creds.yaml')


def test_with_yaml_str(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'add-credential', 'aws', '--file', mock_file.name])
    juju = jubilant.Juju()

    yaml_str = 'credentials:\n  aws:\n    mycred:\n      auth-type: access-key\n'
    juju.add_credential('aws', yaml=yaml_str)

    assert mock_file.writes == [yaml_str]


def test_with_yaml_dict(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'add-credential', 'aws', '--file', mock_file.name])
    juju = jubilant.Juju()

    yaml_dict = {'credentials': {'aws': {'mycred': {'auth-type': 'access-key'}}}}
    juju.add_credential('aws', yaml=yaml_dict)

    assert len(mock_file.writes) == 1
    assert 'auth-type: access-key' in mock_file.writes[0]


def test_with_region(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--file', '/path/to/creds.yaml', '--region', 'us-east-1'])
    juju = jubilant.Juju()

    juju.add_credential('aws', file='/path/to/creds.yaml', region='us-east-1')


def test_with_controller(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--file', '/path/to/creds.yaml', '--controller', 'mycontroller'])
    juju = jubilant.Juju()

    juju.add_credential('aws', file='/path/to/creds.yaml', controller='mycontroller')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-credential',
            'aws',
            '--file',
            '/path/to/creds.yaml',
            '--region',
            'us-east-1',
            '--controller',
            'mycontroller',
        ]
    )
    juju = jubilant.Juju()

    juju.add_credential(
        'aws',
        file='/path/to/creds.yaml',
        region='us-east-1',
        controller='mycontroller',
    )


def test_neither_file_nor_yaml():
    juju = jubilant.Juju()

    with pytest.raises(ValueError, match='exactly one of file or yaml must be specified'):
        juju.add_credential('aws')  # type: ignore[call-overload]


def test_both_file_and_yaml():
    juju = jubilant.Juju()

    with pytest.raises(ValueError, match='exactly one of file or yaml must be specified'):
        juju.add_credential('aws', file='/path/to/creds.yaml', yaml='test')  # type: ignore[call-overload]
