from __future__ import annotations

import pathlib
import subprocess
from typing import Any
from unittest import mock

import pytest

import jubilant

from . import mocks


def test_minimal(run: mocks.Run):
    run.handle(['/bin/juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp('SRC', 'DST')


def test_all_args(run: mocks.Run):
    run.handle([
        '/bin/juju',
        'scp',
        '--container',
        'redis',
        '--no-host-key-checks',
        '--ssh-key',
        '/path/to/private.key',
        '--',
        '-r',
        '-C',
        'SRC',
        'DST',
    ])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp(
        'SRC',
        'DST',
        container='redis',
        host_key_checks=False,
        ssh_key=pathlib.Path('/path/to/private.key'),
        scp_options=['-r', '-C'],
    )


def test_ssh_key(run: mocks.Run):
    run.handle(['/bin/juju', 'scp', '--ssh-key', '/path/to/private.key', '--', 'SRC', 'DST'])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp('SRC', 'DST', ssh_key=pathlib.Path('/path/to/private.key'))


def test_path_source(run: mocks.Run):
    run.handle(['/bin/juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp(pathlib.Path('SRC'), 'DST')


def test_path_destination(run: mocks.Run):
    run.handle(['/bin/juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp('SRC', pathlib.Path('DST'))


def test_type_error():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.scp('src', 'dst', scp_options='invalid')


def test_src_file_tempdir(run: mocks.Run, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    snap_dir = tmp_path / 'snap'
    snap_dir.mkdir()
    monkeypatch.setattr('tempfile.TemporaryDirectory', mocks.TemporaryDirectory(str(snap_dir)))

    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    (src_dir / 'myfile.txt').write_text('DATA')

    run.handle(['juju', 'scp', '--', f'{snap_dir}/myfile.txt', 'target:/dest'])

    juju = jubilant.Juju()
    juju.scp(str(src_dir / 'myfile.txt'), 'target:/dest')

    assert (snap_dir / 'myfile.txt').read_text() == 'DATA'


def test_src_dir_tempdir(run: mocks.Run, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    snap_dir = tmp_path / 'snap'
    snap_dir.mkdir()
    monkeypatch.setattr('tempfile.TemporaryDirectory', mocks.TemporaryDirectory(str(snap_dir)))

    src_dir = tmp_path / 'mydir'
    src_dir.mkdir()
    (src_dir / 'a.txt').write_text('A')
    (src_dir / 'b.txt').write_text('B')

    run.handle(['juju', 'scp', '--', '-r', f'{snap_dir}/mydir', 'target:/dest'])

    juju = jubilant.Juju()
    juju.scp(str(src_dir), 'target:/dest', scp_options=['-r'])

    assert (snap_dir / 'mydir').is_dir()
    assert (snap_dir / 'mydir' / 'a.txt').read_text() == 'A'
    assert (snap_dir / 'mydir' / 'b.txt').read_text() == 'B'


def test_dst_file_tempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    num_calls = 0

    def mock_run(args: list[str], **_: Any):
        nonlocal num_calls
        num_calls += 1
        assert args == ['juju', 'scp', '--', 'target:/source', mock.ANY]
        # Simulate juju writing a file to the temp path.
        pathlib.Path(args[4]).write_text('REMOTE')
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    dest = tmp_path / 'local_copy'

    juju = jubilant.Juju()
    juju.scp('target:/source', str(dest))

    assert dest.read_text() == 'REMOTE'

    assert num_calls == 1


def test_dst_dir_tempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    num_calls = 0

    def mock_run(args: list[str], **_: Any):
        nonlocal num_calls
        num_calls += 1
        assert args == ['juju', 'scp', '--', '-r', 'target:/source', mock.ANY]
        # Simulate juju writing a directory to the temp path.
        temp_path = pathlib.Path(args[5])
        temp_path.mkdir()
        (temp_path / 'c.txt').write_text('C')
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    dest = tmp_path / 'local_dir'

    juju = jubilant.Juju()
    juju.scp('target:/source', str(dest), scp_options=['-r'])

    assert dest.is_dir()
    assert (dest / 'c.txt').read_text() == 'C'

    assert num_calls == 1


def test_dst_existing_dir_file_tempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    def mock_run(args: list[str], **_: Any):
        assert args == ['juju', 'scp', '--', 'target:/var/log/source.log', mock.ANY]
        # Simulate scp copying the file into the temporary directory.
        (pathlib.Path(args[4]) / 'source.log').write_text('REMOTE')
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    juju = jubilant.Juju()
    juju.scp('target:/var/log/source.log', str(tmp_path))

    assert [p.name for p in tmp_path.iterdir()] == ['source.log']
    assert (tmp_path / 'source.log').read_text() == 'REMOTE'


def test_dst_existing_dir_glob_tempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    def mock_run(args: list[str], **_: Any):
        assert args == ['juju', 'scp', '--', 'target:/tmp/x*.log', mock.ANY]
        # Simulate scp expanding the glob on the remote side.
        (pathlib.Path(args[4]) / 'x1.log').write_text('1')
        (pathlib.Path(args[4]) / 'x2.log').write_text('2')
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    juju = jubilant.Juju()
    juju.scp('target:/tmp/x*.log', str(tmp_path))

    assert sorted(p.name for p in tmp_path.iterdir()) == ['x1.log', 'x2.log']
    assert (tmp_path / 'x1.log').read_text() == '1'
    assert (tmp_path / 'x2.log').read_text() == '2'


def test_dst_existing_dir_dir_tempdir(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    def mock_run(args: list[str], **_: Any):
        assert args == ['juju', 'scp', '--', '-r', 'ubuntu@target:/source/', mock.ANY]
        # Simulate scp copying the directory into the temporary directory.
        source_dir = pathlib.Path(args[5]) / 'source'
        source_dir.mkdir()
        (source_dir / 'c.txt').write_text('C')
        return subprocess.CompletedProcess(args, 0, '', '')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore

    juju = jubilant.Juju()
    juju.scp('ubuntu@target:/source/', str(tmp_path), scp_options=['-r'])
    # Copying again over the first copy works, as it does with scp.
    juju.scp('ubuntu@target:/source/', str(tmp_path), scp_options=['-r'])

    assert [p.name for p in tmp_path.iterdir()] == ['source']
    assert (tmp_path / 'source' / 'c.txt').read_text() == 'C'
