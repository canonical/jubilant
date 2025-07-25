import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'add-model', '--no-switch', 'new'])
    juju = jubilant.Juju(model='initial')

    juju.add_model('new')

    assert juju.model == 'new'


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-model',
            '--no-switch',
            'm',
            'lc',
            '--controller',
            'c',
            '--config',
            'x=true',
            '--config',
            'y=1',
            '--config',
            'z=ss',
            '--credential',
            'cc',
        ]
    )
    juju = jubilant.Juju()

    juju.add_model(
        'm', 'lc', controller='c', config={'x': True, 'y': 1, 'z': 'ss'}, credential='cc'
    )

    assert juju.model == 'c:m'
