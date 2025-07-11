import jubilant

from . import mocks


def test_remove_secret(run: mocks.Run):
    run.handle(['juju', 'remove-secret', 'my-secret'])
    juju = jubilant.Juju()

    juju.remove_secret('my-secret')


def test_remove_secret_revision(run: mocks.Run):
    run.handle(['juju', 'remove-secret', 'my-secret', '--revision', '2'])
    juju = jubilant.Juju()

    juju.remove_secret('my-secret', revision=2)
