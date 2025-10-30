import pathlib

import pytest

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


def test_path(run: mocks.Run):
    run.handle(['juju', 'refresh', 'xyz', '--path', 'foo'])
    juju = jubilant.Juju()

    juju.refresh('xyz', path=pathlib.Path('foo'))


def test_tempdir(
    run: mocks.Run, mock_file: mocks.NamedTemporaryFile, monkeypatch: pytest.MonkeyPatch
):
    copy_src, copy_dst = '', ''

    def mock_copy(src: str, dst: str):
        nonlocal copy_src, copy_dst
        copy_src, copy_dst = src, dst

    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore
    monkeypatch.setattr('shutil.copy', mock_copy)
    run.handle(['juju', 'refresh', 'app', '--path', mock_file.name])

    juju = jubilant.Juju()
    juju.refresh('app', path='/path/to/my.charm')

    assert copy_src == '/path/to/my.charm'
    assert copy_dst == mock_file.name
