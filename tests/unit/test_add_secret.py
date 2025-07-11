from __future__ import annotations

import jubilant
from tests.unit import mocks


def test_normal(run: mocks.Run, file: mocks.File):
    run.handle(
        ['juju', 'add-secret', 'my-secret', '--file', file.name],
        stdout='secret:0123456789abcdefghji\n',
    )
    juju = jubilant.Juju()

    juju.add_secret('my-secret', {'username': 'admin'})

    assert len(file.write_log) == 1
    assert file.write_log[0] == 'username: admin\n'


def test_with_info(run: mocks.Run, file: mocks.File):
    run.handle(
        ['juju', 'add-secret', 'my-secret', '--info', 'A description.', '--file', file.name],
        stdout='secret:0123456789abcdefghji\n',
    )
    juju = jubilant.Juju()

    juju.add_secret('my-secret', {'username': 'admin'}, info='A description.')

    assert len(file.write_log) == 1
    assert file.write_log[0] == 'username: admin\n'
