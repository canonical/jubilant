import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'integrate', 'app1', 'app2'])
    juju = jubilant.Juju()

    juju.integrate('app1', 'app2')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'integrate', '--model', 'mdl', 'app1', 'app2'])
    juju = jubilant.Juju(model='mdl')

    juju.integrate('app1', 'app2')


def test_with_endpoints(run: mocks.Run):
    run.handle(['juju', 'integrate', 'app1:db', 'app2:db'])
    juju = jubilant.Juju()

    juju.integrate('app1:db', 'app2:db')


def test_via(run: mocks.Run):
    run.handle(['juju', 'integrate', 'app1', 'mdl.app2', '--via', '192.168.0.0/16'])
    juju = jubilant.Juju()

    juju.integrate('app1', 'mdl.app2', via='192.168.0.0/16')


def test_via_list(run: mocks.Run):
    run.handle(['juju', 'integrate', 'app1', 'mdl.app2', '--via', '192.168.0.0/16,16,10.0.0.0/8'])
    juju = jubilant.Juju()

    juju.integrate('app1', 'mdl.app2', via=['192.168.0.0/16', '16,10.0.0.0/8'])
