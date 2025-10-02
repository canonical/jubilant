import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'remove-relation', 'app1', 'app2'])
    juju = jubilant.Juju(cli_version='3.6.9')

    juju.remove_relation('app1', 'app2')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'remove-relation', '--model', 'mdl', 'app1', 'app2'])
    juju = jubilant.Juju(model='mdl', cli_version='3.6.9')

    juju.remove_relation('app1', 'app2')


def test_with_endpoints(run: mocks.Run):
    run.handle(['juju', 'remove-relation', 'app1:db', 'app2:db'])
    juju = jubilant.Juju(cli_version='3.6.9')

    juju.remove_relation('app1:db', 'app2:db')


def test_force(run: mocks.Run):
    run.handle(['juju', 'remove-relation', 'app1', 'app2', '--force'])
    juju = jubilant.Juju(cli_version='3.6.9')

    juju.remove_relation('app1', 'app2', force=True)
