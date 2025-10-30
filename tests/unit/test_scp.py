import pathlib

import pytest

import jubilant

from . import mocks


def test_minimal(run: mocks.Run):
    run.handle(['/bin/juju', 'scp', '--', 'SRC', 'DST'])
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp('SRC', 'DST')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            '/bin/juju',
            'scp',
            '--container',
            'redis',
            '--no-host-key-checks',
            '--',
            '-r',
            '-C',
            'SRC',
            'DST',
        ]
    )
    juju = jubilant.Juju(cli_binary='/bin/juju')

    juju.scp('SRC', 'DST', container='redis', host_key_checks=False, scp_options=['-r', '-C'])


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


def test_src_tempdir(
    run: mocks.Run, mock_file: mocks.NamedTemporaryFile, monkeypatch: pytest.MonkeyPatch
):
    copy_src, copy_dst = '', ''

    def mock_copy(src: str, dst: str):
        nonlocal copy_src, copy_dst
        copy_src, copy_dst = src, dst

    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore
    monkeypatch.setattr('shutil.copy', mock_copy)
    run.handle(['juju', 'scp', '--', mock_file.name, 'target:/dest'])

    juju = jubilant.Juju()
    juju.scp('/local/file', 'target:/dest')

    assert copy_src == '/local/file'
    assert copy_dst == mock_file.name


def test_dst_tempdir(
    run: mocks.Run, mock_file: mocks.NamedTemporaryFile, monkeypatch: pytest.MonkeyPatch
):
    copy_src, copy_dst = '', ''

    def mock_copy(src: str, dst: str):
        nonlocal copy_src, copy_dst
        copy_src, copy_dst = src, dst

    monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')  # type: ignore
    monkeypatch.setattr('shutil.copy', mock_copy)
    run.handle(['juju', 'scp', '--', 'target:/source', mock_file.name])

    juju = jubilant.Juju()
    juju.scp('target:/source', '/local/file')

    assert copy_src == mock_file.name
    assert copy_dst == '/local/file'
