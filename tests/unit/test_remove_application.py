import jubilant

from . import mocks


def test_single(run: mocks.Run):
    run.handle(['juju', 'remove-application', '--no-prompt', 'app1'])
    juju = jubilant.Juju()

    juju.remove_application('app1')
