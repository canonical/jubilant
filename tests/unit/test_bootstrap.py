import jubilant

from . import mocks


def test_defaults_with_cloud(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd', 'my-controller', '--no-switch'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd','my-controller')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'bootstrap',
            'lxd',
            'my-lxd-controller',
            '--no-switch',
            '--bootstrap-base',
            'ubuntu@22.04',
            '--bootstrap-constraints',
            'mem=8G',
            '--config',
            'foo=bar',
            '--constraints',
            'mem=8G',
            '--credential',
            'my-credential',
            '--force',
            '--model-default',
            'foo=bar',
            '--storage-pool',
            'name=my-pool',
            '--storage-pool',
            'type=lxd',
            '--to',
            'lxd:1',
        ]
    )
    juju = jubilant.Juju()

    juju.bootstrap(
        'lxd',
        'my-lxd-controller',
        bootstrap_base='ubuntu@22.04',
        bootstrap_constraints={'mem': '8G'},
        config={'foo': 'bar'},
        constraints={'mem': '8G'},
        credential='my-credential',
        force=True,
        model_default={'foo': 'bar'},
        storage_pool={'name': 'my-pool', 'type': 'lxd'},
        to='lxd:1',
    )
