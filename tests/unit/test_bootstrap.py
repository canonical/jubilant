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
            '--bootstrap-constraints',
            'is_test=true',
            '--config',
            'foo=bar',
            '--config',
            'baz=qux',
            '--constraints',
            'mem=8G',
            '--constraints',
            'arch=amd64',
            '--constraints',
            'another_bool=false',
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
            '--metadata-source',
            '/path/to/metadata',
        ]
    )
    juju = jubilant.Juju()

    juju.bootstrap(
        'lxd',
        'my-lxd-controller',
        bootstrap_base='ubuntu@22.04',
        bootstrap_constraints={'mem': '8G', 'tags': 'juju', 'is_test': True},
        config={'foo': 'bar', 'baz': 'qux'},
        constraints={'mem': '8G', 'arch': 'amd64', 'another_bool': False},
        credential='my-credential',
        force=True,
        model_defaults={'foo': 'bar'},
        storage_pool={'name': 'my-pool', 'type': 'lxd'},
        metadata_source='/path/to/metadata',
        to='lxd:1',
    )


def test_list_args(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd', 'myctrl', '--no-switch', '--to', 'to1,to2'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd', 'myctrl', to=['to1', 'to2'])
