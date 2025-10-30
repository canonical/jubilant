from __future__ import annotations

import pathlib
import subprocess
import tempfile
from typing import Any
from unittest import mock

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
            '/bin/juju',
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
    juju = jubilant.Juju(cli_binary='/bin/juju')

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


def test_tempdir(monkeypatch: pytest.MonkeyPatch):
    num_calls = 0

    def mock_run(args: list[str], **_: Any):
        nonlocal num_calls
        num_calls += 1
        assert args == [
            'juju',
            'refresh',
            'myapp',
            '--path',
            mock.ANY,
            '--resource',
            mock.ANY,
            '--resource',
            'r2=R2',
        ]
        temp_dir = pathlib.Path(args[4]).parent
        assert '/snap/juju/common' in str(temp_dir)
        assert args[4] == f'{temp_dir}/_temp.charm'
        assert args[6] == f'r1={temp_dir}/r1'
        assert pathlib.Path(args[4]).read_text() == 'CH'
        assert pathlib.Path(args[6][3:]).read_text() == 'R1'
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    with tempfile.TemporaryDirectory() as temp:
        (pathlib.Path(temp) / 'my.charm').write_text('CH')
        (pathlib.Path(temp) / 'r1').write_text('R1')

        juju = jubilant.Juju()
        juju.refresh(
            'myapp',
            path=pathlib.Path(temp) / 'my.charm',
            resources={
                'r1': str(pathlib.Path(temp) / 'r1'),
                'r2': 'R2',
            },
        )

    assert num_calls == 1
