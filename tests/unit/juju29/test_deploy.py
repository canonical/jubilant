import pathlib

import pytest

import jubilant

from .. import mocks


@pytest.mark.parametrize(
    'base,series',
    [
        ('ubuntu@14.04', 'trusty'),
        ('ubuntu@16.04', 'xenial'),
        ('ubuntu@18.04', 'bionic'),
        ('ubuntu@20.04', 'focal'),
        ('ubuntu@22.04', 'jammy'),
        ('ubuntu@24.04', 'noble'),
        ('ubuntu@24.10', 'oracular'),
        ('ubuntu@25.04', 'plucky'),
        ('ubuntu@25.10', 'questing'),
    ],
)
@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_all_args(juju_version: str, base: str, series: str, run: mocks.Run):
    run.handle(
        [
            'juju',
            'deploy',
            'charm',
            'app',
            '--attach-storage',
            'stg',
            '--series' if juju_version[0] == '2' else '--base',
            series if juju_version[0] == '2' else base,
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
    juju._is_juju_2 = juju_version[0] == '2'

    juju.deploy(
        'charm',
        'app',
        attach_storage='stg',
        base=base,
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
