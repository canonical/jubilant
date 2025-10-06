from __future__ import annotations

import pytest
import yaml

import jubilant

from . import mocks


def test_completed(run: mocks.Run):
    out_json = """
{
  "mysql/0": {
    "id": "42",
    "log": [
      "2025-03-01 16:23:26 +1300 NZDT Log message",
      "2025-03-01 16:23:26 +1300 NZDT Another message"
    ],
    "results": {
      "password": "pass",
      "return-code": 0,
      "username": "user",
      "stdout": "OUT",
      "stderr": "ERR"
    },
    "status": "completed"
  }
}
"""
    run.handle(['juju', 'run', '--format', 'json', 'mysql/0', 'get-password'], stdout=out_json)
    juju = jubilant.Juju()

    task = juju.run('mysql/0', 'get-password')

    assert task == jubilant.Task(
        id='42',
        status='completed',
        results={'username': 'user', 'password': 'pass'},
        return_code=0,
        stdout='OUT',
        stderr='ERR',
        log=[
            '2025-03-01 16:23:26 +1300 NZDT Log message',
            '2025-03-01 16:23:26 +1300 NZDT Another message',
        ],
    )
    assert task.success


def test_not_found(run: mocks.Run):
    run.handle(['juju', 'run', '--format', 'json', 'mysql/0', 'get-password'])
    juju = jubilant.Juju()

    with pytest.raises(ValueError):
        juju.run('mysql/0', 'get-password')


def test_failure(run: mocks.Run):
    out_json = """
{
  "mysql/0": {
    "id": "42",
    "message": "Failure message",
    "results": {
      "foo": "bar",
      "return-code": 0
    },
    "status": "failed"
  }
}
"""
    run.handle(['juju', 'run', '--format', 'json', 'mysql/0', 'faily'], stdout=out_json)
    juju = jubilant.Juju()

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.run('mysql/0', 'faily')

    assert excinfo.value.task == jubilant.Task(
        id='42',
        status='failed',  # This is what causes the failure (even when return_code is 0)
        results={'foo': 'bar'},
        return_code=0,
        message='Failure message',
    )
    assert not excinfo.value.task.success


def test_exception_task_failed(run: mocks.Run):
    out_json = """
{
  "mysql/0": {
    "id": "42",
    "results": {
      "foo": "bar",
      "return-code": 1,
      "stderr": "Uncaught Exception in charm code: thing happened..."
    },
    "status": "failed"
  }
}
"""
    run.handle(
        ['juju', 'run', '--format', 'json', 'mysql/0', 'exceptiony'],
        returncode=1,
        stdout=out_json,
        stderr='... task failed ...',
    )
    juju = jubilant.Juju()

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.run('mysql/0', 'exceptiony')

    assert excinfo.value.task == jubilant.Task(
        id='42',
        status='failed',
        results={'foo': 'bar'},
        return_code=1,
        stderr='Uncaught Exception in charm code: thing happened...',
    )
    assert not excinfo.value.task.success


def test_exception_other(run: mocks.Run):
    run.handle(
        ['juju', 'run', '--format', 'json', 'mysql/0', 'exceptiony'],
        returncode=2,
        stdout='OUT',
        stderr='ERR',  # Must not contain "task failed"
    )
    juju = jubilant.Juju()

    with pytest.raises(jubilant.CLIError) as excinfo:
        juju.run('mysql/0', 'exceptiony')

    assert excinfo.value.returncode == 2
    assert excinfo.value.stdout == 'OUT'
    assert excinfo.value.stderr == 'ERR'


def test_wait_timeout(run: mocks.Run):
    run.handle(
        ['juju', 'run', '--format', 'json', 'mysql/0', 'do-thing', '--wait', '0.001s'],
        returncode=1,
        stdout='OUT',
        stderr='... timed out ...',
    )
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError):
        juju.run('mysql/0', 'do-thing', wait=0.001)


def test_params(run: mocks.Run, mock_file: mocks.NamedTemporaryFile):
    stdout = """
{
  "mysql/0": {
    "id": "42",
    "results": {
      "password": "pass",
      "return-code": 0,
      "username": "user"
    },
    "status": "completed"
  }
}"""
    run.handle(
        ['juju', 'run', '--format', 'json', 'mysql/0', 'get-password', '--params', mock_file.name],
        stdout=stdout,
    )
    juju = jubilant.Juju()

    task = juju.run('mysql/0', 'get-password', {'foo': 1, 'bar': ['ab', 'cd']})

    assert task == jubilant.Task(
        id='42',
        status='completed',
        results={'username': 'user', 'password': 'pass'},
    )
    assert task.success
    assert yaml.safe_load('\n'.join(mock_file.writes)) == {'foo': 1, 'bar': ['ab', 'cd']}
    assert mock_file.num_flushes == 1
