import jubilant

from . import mocks


def test_defaults_interactive(run: mocks.Run):
    run.handle(['juju', 'bootstrap'])
    juju = jubilant.Juju()

    juju.bootstrap()


def test_clouds(run: mocks.Run):
    run.handle(['juju', 'bootstrap', '--clouds'])
    juju = jubilant.Juju()

    juju.bootstrap(clouds=True)


def test_regions(run: mocks.Run):
    run.handle(['juju', 'bootstrap', '--regions', 'aws'])
    juju = jubilant.Juju()

    juju.bootstrap(regions='aws')


def test_defaults_with_cloud(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd')


def test_defaults_with_add_model(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'lxd', '--add-model', 'test-model'])
    juju = jubilant.Juju()

    juju.bootstrap('lxd', add_model='test-model')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'bootstrap',
            'lxd',
            'my-lxd-controller',
            '--add-model',
            'test-model',
            '--agent-version',
            '1.2.3',
            '--auto-upgrade',
            '--bootstrap-base',
            'ubuntu@22.04',
            '--bootstrap-constraints',
            'mem=8G',
            '--bootstrap-image',
            'ubuntu@22.04',
            '--bootstrap-series',
            'jammy',
            '--build-agent',
            '--config',
            'foo=bar',
            '--constraints',
            'mem=8G',
            '--controller-charm-channel',
            '3.6/stable',
            '--controller-charm-path',
            'path/to/controller.charm',
            '--credential',
            'my-credential',
            '--db-snap',
            'path/to/db.snap',
            '--db-snap-asserts',
            'path/to/db.assert',
            '--force',
            '--keep-broken',
            '--metadata-source',
            'path/to/metadata/source',
            '--model-default',
            'foo=bar',
            '--no-switch',
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
        add_model='test-model',
        agent_version='1.2.3',
        auto_upgrade=True,
        bootstrap_base='ubuntu@22.04',
        bootstrap_constraints={'mem': '8G'},
        bootstrap_image='ubuntu@22.04',
        bootstrap_series='jammy',
        build_agent=True,
        config={'foo': 'bar'},
        constraints={'mem': '8G'},
        controller_charm_channel='3.6/stable',
        controller_charm_path='path/to/controller.charm',
        credential='my-credential',
        db_snap='path/to/db.snap',
        db_snap_asserts='path/to/db.assert',
        force=True,
        keep_broken=True,
        metadata_source='path/to/metadata/source',
        model_default={'foo': 'bar'},
        no_switch=True,
        storage_pool={'name': 'my-pool', 'type': 'lxd'},
        to='lxd:1',
    )
