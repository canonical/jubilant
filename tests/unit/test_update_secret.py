import jubilant
from tests.unit import mocks


def test_basic(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'update-secret', 'my-secret', '--file', mock_file.name])
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'})

    assert len(mock_file.writes) == 1
    assert mock_file.writes[0] == 'username: admin\n'


def test_new_name(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        ['juju', 'update-secret', 'my-secret', '--name', 'credentials', '--file', mock_file.name]
    )
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, name='credentials')


def test_new_info(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        [
            'juju',
            'update-secret',
            'my-secret',
            '--info',
            'a new description',
            '--file',
            mock_file.name,
        ]
    )
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, info='a new description')


def test_auto_prune(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'update-secret', 'my-secret', '--auto-prune', '--file', mock_file.name])
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, auto_prune=True)


def test_all_options(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        [
            'juju',
            'update-secret',
            'my-secret',
            '--info',
            'a new description',
            '--name',
            'credentials',
            '--auto-prune',
            '--file',
            mock_file.name,
        ]
    )
    juju = jubilant.Juju()

    juju.update_secret(
        'my-secret',
        {'username': 'admin'},
        name='credentials',
        info='a new description',
        auto_prune=True,
    )
