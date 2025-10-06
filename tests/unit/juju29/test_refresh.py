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
@pytest.mark.parametrize('trust', [True, False])
@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_all_args(
    juju_version: str,
    trust: bool,
    base: str,
    series: str,
    run: mocks.Run,
    monkeypatch: pytest.MonkeyPatch,
):
    written_content: list[str] = []

    class MockFile:
        name = '/path/to/mockfile'

        def write(self, data: str):
            written_content.append(data)

        def flush(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore
            pass

    monkeypatch.setattr('tempfile.TemporaryFile', lambda _: MockFile())  # type: ignore
    if juju_version[0] == '2' and trust:
        trust_cmd = ['juju', 'trust', 'app']
        run.handle(trust_cmd)
    core_cmd = [
        'juju',
        'refresh',
        'app',
        '--series' if juju_version[0] == '2' else '--base',
        series if juju_version[0] == '2' else base,
        '--channel',
        'latest/edge',
    ]
    if juju_version[0] != '2':
        core_cmd.extend(
            [
                '--config',
                'x=true',
                '--config',
                'y=1',
                '--config',
                'z=ss',
            ]
        )
    core_cmd.extend(
        [
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
        ]
    )
    if juju_version[0] == '2':
        core_cmd.extend(['--config', '/path/to/mockfile'])
    elif trust:
        core_cmd.append('--trust')
    run.handle(core_cmd)
    juju = jubilant.Juju()
    juju._is_juju_2 = juju_version[0] == '2'

    juju.refresh(
        'app',
        base=base,
        channel='latest/edge',
        config={'x': True, 'y': 1, 'z': 'ss'},
        force=True,
        path='/path/to/app.charm',
        resources={'bin': '/path'},
        revision=42,
        storage={'data': 'tmpfs,1G'},
        trust=trust,
    )
    if juju_version[0] == '2':
        assert ''.join(written_content) == 'x: true\ny: 1\nz: ss\n'
