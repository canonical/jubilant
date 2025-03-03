import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'switch', 'new'])
    juju = jubilant.Juju()

    juju.switch('new')

    assert juju.model == 'new'


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'switch', 'new'])
    juju = jubilant.Juju(model='initial')

    juju.switch('new')

    assert juju.model == 'new'
