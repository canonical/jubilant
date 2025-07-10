import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'consume', 'othermodel.mysql'])
    juju = jubilant.Juju()

    juju.consume('othermodel.mysql')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'consume', '--model', 'mdl', 'othermodel.mysql'])
    juju = jubilant.Juju(model='mdl')

    juju.consume('othermodel.mysql')


def test_owner(run: mocks.Run):
    run.handle(['juju', 'consume', 'owner/othermodel.mysql'])
    juju = jubilant.Juju()

    juju.consume('othermodel.mysql', owner='owner')


def test_all_args(run: mocks.Run):
    run.handle(['juju', 'consume', 'anothercontroller:admin/othermodel.mysql', 'sql'])
    juju = jubilant.Juju()

    juju.consume('othermodel.mysql', 'sql', controller='anothercontroller', owner='admin')
