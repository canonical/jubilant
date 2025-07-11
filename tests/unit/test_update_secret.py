import jubilant
from tests.unit import mocks


def test_basic(run: mocks.Run, file: mocks.File):
    run.handle(['juju', 'update-secret', 'my-secret', '--file', file.name])
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'})

    assert len(file.write_log) == 1
    assert file.write_log[0] == 'username: admin\n'


def test_new_name(run: mocks.Run, file: mocks.File):
    run.handle(
        ['juju', 'update-secret', 'my-secret', '--name', 'credentials', '--file', file.name]
    )
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, name='credentials')


def test_new_info(run: mocks.Run, file: mocks.File):
    run.handle(
        [
            'juju',
            'update-secret',
            'my-secret',
            '--info',
            'a new description',
            '--file',
            file.name,
        ]
    )
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, info='a new description')


def test_auto_prune(run: mocks.Run, file: mocks.File):
    run.handle(['juju', 'update-secret', 'my-secret', '--auto-prune', '--file', file.name])
    juju = jubilant.Juju()

    juju.update_secret('my-secret', {'username': 'admin'}, auto_prune=True)


def test_all_options(run: mocks.Run, file: mocks.File):
    run.handle(
        [
            'juju',
            'update-secret',
            'my-secret',
            '--name',
            'credentials',
            '--info',
            'a new description',
            '--auto-prune',
            '--file',
            file.name,
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
