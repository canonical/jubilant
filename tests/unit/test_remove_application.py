import jubilant

from . import mocks


def test_single(run: mocks.Run):
    run.handle(['juju', 'remove-application', '--no-prompt', 'app1'])
    juju = jubilant.Juju()

    juju.remove_application('app1')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'remove-application', '--model', 'mdl', '--no-prompt', 'app1'])
    juju = jubilant.Juju(model='mdl')

    juju.remove_application('app1')


def test_force_and_destroy(run: mocks.Run):
    run.handle(
        ['juju', 'remove-application', '--no-prompt', 'app1', '--destroy-storage', '--force']
    )
    juju = jubilant.Juju()

    juju.remove_application('app1', destroy_storage=True, force=True)


def test_multiple(run: mocks.Run):
    run.handle(['juju', 'remove-application', '--no-prompt', 'app1', 'app2', 'app3'])
    juju = jubilant.Juju()

    juju.remove_application('app1', 'app2', 'app3')
