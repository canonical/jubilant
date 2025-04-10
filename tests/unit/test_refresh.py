import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'refresh', 'xyz'])
    juju = jubilant.Juju()

    juju.refresh('xyz')


def test_defaults_with_model(run: mocks.Run):
    run.handle(['juju', 'refresh', '--model', 'mdl', 'xyz'])
    juju = jubilant.Juju(model='mdl')

    juju.refresh('xyz')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'refresh',
            'app',
            '--base',
            'ubuntu@22.04',
            '--channel',
            'latest/edge',
            '--config',
            'x=true',
            '--config',
            'y=1',
            '--config',
            'z=ss',
            '--force',
            '--force-base',
            '--force-units',
            '--path',
            '/path/to/app.charm',
            '--resource',
            'bin=/path',
            '--revision',
            '42',
            '--storage',
            'data=tmpfs,1G',
            '--trust',
        ]
    )
    juju = jubilant.Juju()

    juju.refresh(
        'app',
        base='ubuntu@22.04',
        channel='latest/edge',
        config={'x': True, 'y': 1, 'z': 'ss'},
        force=True,
        path='/path/to/app.charm',
        resources={'bin': '/path'},
        revision=42,
        storage={'data': 'tmpfs,1G'},
        trust=True,
    )
