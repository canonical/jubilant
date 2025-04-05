import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'trust', 'app'])
    juju = jubilant.Juju()

    juju.trust('app')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'trust', '--model', 'mdl', 'app'])
    juju = jubilant.Juju(model='mdl')

    juju.trust('app')


def test_remove(run: mocks.Run):
    run.handle(['juju', 'trust', 'rmv', '--remove'])
    juju = jubilant.Juju()

    juju.trust('rmv', remove=True)


def test_scope(run: mocks.Run):
    run.handle(['juju', 'trust', 'app', '--scope', 'cluster'])
    juju = jubilant.Juju()

    juju.trust('app', scope='cluster')


def test_scope_and_remove(run: mocks.Run):
    run.handle(['juju', 'trust', 'rmv', '--remove', '--scope', 'cluster'])
    juju = jubilant.Juju()

    juju.trust('rmv', remove=True, scope='cluster')
