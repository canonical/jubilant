import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd', 'my-controller', '--no-switch'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd', 'my-controller')
    assert juju.model is None  # ensure self.model hasn't changed


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
            '--bootstrap-constraints',
            'tags=juju',
            '--config',
            'foo=bar',
            '--config',
            'baz=qux',
            '--constraints',
            'mem=8G',
            '--constraints',
            'arch=amd64',
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
        bootstrap_constraints={'mem': '8G', 'tags': 'juju'},
        config={'foo': 'bar', 'baz': 'qux'},
        constraints={'mem': '8G', 'arch': 'amd64'},
        credential='my-credential',
        force=True,
        model_defaults={'foo': 'bar'},
        storage_pool={'name': 'my-pool', 'type': 'lxd'},
        to='lxd:1',
    )


def test_list_args(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd', 'myctrl', '--no-switch', '--to', 'to1,to2'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd', 'myctrl', to=['to1', 'to2'])
