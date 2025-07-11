import pathlib

import pytest

import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'deploy', 'xyz'])
    juju = jubilant.Juju()

    juju.deploy('xyz')


def test_defaults_with_model(run: mocks.Run):
    run.handle(['juju', 'deploy', '--model', 'mdl', 'xyz'])
    juju = jubilant.Juju(model='mdl')

    juju.deploy('xyz')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'deploy',
            'charm',
            'app',
            '--attach-storage',
            'stg',
            '--base',
            'ubuntu@22.04',
            '--bind',
            'end1=space1 end2=space2',
            '--channel',
            'latest/edge',
            '--config',
            'x=true',
            '--config',
            'y=1',
            '--config',
            'z=ss',
            '--constraints',
            'mem=8G',
            '--force',
            '--num-units',
            '3',
            '--overlay',
            'one.yaml',
            '--overlay',
            'dir/two.yaml',
            '--resource',
            'bin=/path',
            '--revision',
            '42',
            '--storage',
            'data=tmpfs,1G',
            '--to',
            'lxd:25',
            '--trust',
        ]
    )
    juju = jubilant.Juju()

    juju.deploy(
        'charm',
        'app',
        attach_storage='stg',
        base='ubuntu@22.04',
        bind={'end1': 'space1', 'end2': 'space2'},
        channel='latest/edge',
        config={'x': True, 'y': 1, 'z': 'ss'},
        constraints={'mem': '8G'},
        force=True,
        num_units=3,
        overlays=['one.yaml', pathlib.Path('dir', 'two.yaml')],
        resources={'bin': '/path'},
        revision=42,
        storage={'data': 'tmpfs,1G'},
        to='lxd:25',
        trust=True,
    )


def test_bind_str(run: mocks.Run):
    run.handle(['juju', 'deploy', 'charm', '--bind', 'binding'])
    juju = jubilant.Juju()

    juju.deploy('charm', bind='binding')


def test_list_args(run: mocks.Run):
    run.handle(['juju', 'deploy', 'charm', '--attach-storage', 'stg1,stg2', '--to', 'to1,to2'])
    juju = jubilant.Juju()

    juju.deploy('charm', attach_storage=['stg1', 'stg2'], to=['to1', 'to2'])


def test_overlays_str():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.deploy('charm', overlays='bad')


def test_path(run: mocks.Run):
    run.handle(['juju', 'deploy', 'xyz'])
    juju = jubilant.Juju()

    juju.deploy(pathlib.Path('xyz'))
