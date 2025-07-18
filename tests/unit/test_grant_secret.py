import jubilant

from . import mocks


def test_single_app(run: mocks.Run):
    run.handle(['juju', 'grant-secret', 'my-secret', 'my-charm'])
    juju = jubilant.Juju()

    juju.grant_secret('my-secret', 'my-charm')


def test_multiple_apps_as_list(run: mocks.Run):
    run.handle(['juju', 'grant-secret', 'my-secret', 'my-charm,my-other-charm'])
    juju = jubilant.Juju()

    juju.grant_secret('my-secret', ['my-charm', 'my-other-charm'])


def test_multiple_apps_as_string(run: mocks.Run):
    run.handle(['juju', 'grant-secret', 'my-secret', 'my-charm,my-other-charm'])
    juju = jubilant.Juju()

    juju.grant_secret('my-secret', 'my-charm,my-other-charm')
