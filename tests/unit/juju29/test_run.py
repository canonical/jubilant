from __future__ import annotations

import pytest

import jubilant_backports as jubilant

from .. import mocks


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
    run.handle(
        [
            'juju',
            'run',
            '--format',
            'json',
            'mysql/0',
            'get-password',
        ],
        stdout=out_json,
    )
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


def test_completed29(run: mocks.Run):
    out_json = """
{
  "unit-mysql-0": {
    "UnitId": "mysql/0",
    "id": "36",
    "log": [
      "2025-03-01 16:23:26 +1300 NZDT Log message",
      "2025-03-01 16:23:26 +1300 NZDT Another message"
    ],
    "results": {
      "password": "pass",
      "username": "user",
      "Stdout": "OUT"
    },
    "status": "completed",
    "timing": {
      "completed": "2025-07-15 13:01:55 +0000 UTC",
      "enqueued": "2025-07-15 13:01:54 +0000 UTC",
      "started": "2025-07-15 13:01:54 +0000 UTC"
    }
  }
}
"""
    run.handle(
        [
            'juju',
            'run-action',
            '--format',
            'json',
            'mysql/0',
            'get-password',
            '--wait',
        ],
        stdout=out_json,
    )
    juju = jubilant.Juju()
    juju._is_juju_2 = True

    task = juju.run('mysql/0', 'get-password')

    assert task == jubilant.Task(
        id='36',
        status='completed',
        results={'username': 'user', 'password': 'pass'},
        return_code=0,
        stdout='OUT',
        stderr='',
        log=[
            '2025-03-01 16:23:26 +1300 NZDT Log message',
            '2025-03-01 16:23:26 +1300 NZDT Another message',
        ],
    )
    assert task.success


def test_failed29(run: mocks.Run):
    out_json = """
{
  "unit-mysql-0": {
    "UnitId": "mysql/0",
    "id": "34",
    "message": "MSG",
    "results": {
      "ReturnCode": 1,
      "Stderr": "ERR"
    },
    "status": "failed",
    "timing": {
      "completed": "2025-07-15 13:00:56 +0000 UTC",
      "enqueued": "2025-07-15 13:00:54 +0000 UTC",
      "started": "2025-07-15 13:00:55 +0000 UTC"
    }
  }
}
"""
    run.handle(
        [
            'juju',
            'run-action',
            '--format',
            'json',
            'mysql/0',
            'get-password',
            '--wait',
        ],
        stdout=out_json,
    )
    juju = jubilant.Juju()
    juju._is_juju_2 = True

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.run('mysql/0', 'get-password')

    assert excinfo.value.task == jubilant.Task(
        id='34',
        status='failed',
        message='MSG',
        results={},
        return_code=1,
        stdout='',
        stderr='ERR',
        log=[],
    )
