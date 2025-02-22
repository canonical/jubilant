import mocks

import jubilant


def test_basic(run: mocks.Run):
    run.handle(['juju', 'switch', 'new'])
    juju = jubilant.Juju(model='initial')

    juju.switch('new')

    assert juju.model == 'new'
