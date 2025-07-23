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


def test_empty_string_controller_owner(run: mocks.Run):
    # Using empty strings doesn't really make sense, but test the current behaviour.
    # Juju itself would return an error.
    run.handle(['juju', 'consume', ':/othermodel.mysql'])
    juju = jubilant.Juju()

    juju.consume('othermodel.mysql', controller='', owner='')


def test_controller_owner_in_first_arg(run: mocks.Run):
    # You probably wouldn't write it this way, but it works, so test current behaviour.
    run.handle(['juju', 'consume', 'anothercontroller:admin/othermodel.mysql'])
    juju = jubilant.Juju()

    juju.consume('anothercontroller:admin/othermodel.mysql')
