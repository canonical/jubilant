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
    assert mock_file.writes == ['username: admin\n']


def test_with_info(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    run.handle(
        ['juju', 'add-secret', 'my-secret', '--info', 'A description.', '--file', mock_file.name],
        stdout='secret:0123456789abcdefghji\n',
    )
    juju = jubilant.Juju()

    juju.add_secret('my-secret', {'username': 'admin'}, info='A description.')

    assert len(mock_file.writes) == 1
    assert mock_file.writes[0] == 'username: admin\n'
