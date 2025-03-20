import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'debug-log', '--limit', '0'], stdout='line 1\nline 2\n')

    juju = jubilant.Juju()
    logs = juju.debug_log()
    assert logs == 'line 1\nline 2\n'


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'debug-log', '--model', 'mdl', '--limit', '0'], stdout='out')

    juju = jubilant.Juju(model='mdl')
    logs = juju.debug_log()
    assert logs == 'out'


def test_limit(run: mocks.Run):
    run.handle(['juju', 'debug-log', '--limit', '10'], stdout='out')

    juju = jubilant.Juju()
    logs = juju.debug_log(limit=10)
    assert logs == 'out'
