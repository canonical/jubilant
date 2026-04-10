from __future__ import annotations

import pathlib

import pytest

import jubilant

from . import mocks


def test_with_path_str(run: mocks.Run):
    run.handle(['juju', 'update-cloud', 'mycloud', '--client', '-f', '/path/to/cloud.yaml'])
    juju = jubilant.Juju()

    juju.update_cloud('mycloud', '/path/to/cloud.yaml', client=True)


def test_with_controller_default_client(run: mocks.Run):
    run.handle(
        [
            'juju',
            'update-cloud',
            'mycloud',
            '--controller',
            'mycontroller',
            '-f',
            '/path/to/cloud.yaml',
        ]
    )
    juju = jubilant.Juju()

    juju.update_cloud('mycloud', '/path/to/cloud.yaml', controller='mycontroller')


def test_with_path_pathlib(run: mocks.Run):
    run.handle(['juju', 'update-cloud', 'mycloud', '--client', '-f', '/path/to/cloud.yaml'])
    juju = jubilant.Juju()

    juju.update_cloud('mycloud', pathlib.Path('/path/to/cloud.yaml'), client=True)


def test_with_yaml_dict(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(['juju', 'update-cloud', 'mycloud', '--client', '-f', mock_file.name])
    juju = jubilant.Juju()

    definition = {'clouds': {'mycloud': {'type': 'lxd', 'endpoint': '1.2.3.4'}}}
    juju.update_cloud('mycloud', definition, client=True)

    assert len(mock_file.writes) == 1
    assert 'type: lxd' in mock_file.writes[0]


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'update-cloud',
            'mycloud',
            '--client',
            '--controller',
            'mycontroller',
            '-f',
            '/path/to/cloud.yaml',
        ]
    )
    juju = jubilant.Juju()

    juju.update_cloud(
        'mycloud',
        '/path/to/cloud.yaml',
        client=True,
        controller='mycontroller',
    )


def test_requires_client_or_controller():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.update_cloud('mycloud', '/path/to/cloud.yaml')  # type: ignore
