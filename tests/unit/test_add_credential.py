import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws'])
    juju = jubilant.Juju()

    juju.add_credential('aws')


def test_with_file(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--file', '/path/to/creds.yaml'])
    juju = jubilant.Juju()

    juju.add_credential('aws', file='/path/to/creds.yaml')


def test_with_region(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--region', 'us-east-1'])
    juju = jubilant.Juju()

    juju.add_credential('aws', region='us-east-1')


def test_with_controller(run: mocks.Run):
    run.handle(['juju', 'add-credential', 'aws', '--controller', 'mycontroller'])
    juju = jubilant.Juju()

    juju.add_credential('aws', controller='mycontroller')


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
