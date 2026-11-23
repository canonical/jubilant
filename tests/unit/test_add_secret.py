from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_normal(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        ['juju', 'add-secret', 'my-secret', '--file', mock_file.name],
        stdout='secret:0123456789abcdefghji\n',
    )
    juju = jubilant.Juju()

    secret_uri = juju.add_secret('my-secret', {'username': 'admin'})

    assert secret_uri.startswith('secret:')
    assert mock_file.content == 'username: admin\n'
    assert mock_file.flushed == mock_file.content


def test_with_info(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        ['juju', 'add-secret', 'my-secret', '--info', 'A description.', '--file', mock_file.name],
        stdout='secret:0123456789abcdefghji\n',
    )
    juju = jubilant.Juju()

    juju.add_secret('my-secret', {'username': 'admin'}, info='A description.')

    assert mock_file.content == 'username: admin\n'
    assert mock_file.flushed == mock_file.content
