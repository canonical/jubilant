import os.path
import subprocess
from typing import Any

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

    result = juju.run('mysql/0', 'get-password')

    assert result == jubilant.ActionResult(
        success=True,
        status='completed',
        task_id='42',
        results={'username': 'user', 'password': 'pass'},
        return_code=0,
        stdout='OUT',
        stderr='ERR',
        log=[
            '2025-03-01 16:23:26 +1300 NZDT Log message',
            '2025-03-01 16:23:26 +1300 NZDT Another message',
        ],
    )


def test_not_found(run: mocks.Run):
    run.handle(['juju', 'run', '--format', 'json', 'mysql/0', 'get-password'])
    juju = jubilant.Juju()

    with pytest.raises(ValueError):
        juju.run('mysql/0', 'get-password')


def test_failed(run: mocks.Run):
    out_json = """
{
  "mysql/0": {
    "id": "42",
    "message": "Failure message",
    "results": {
      "foo": "bar",
      "return-code": 1,
      "stderr": "Uncaught Exception in charm code: thing happened..."
    },
    "status": "failed"
  }
}
"""
    run.handle(['juju', 'run', '--format', 'json', 'mysql/0', 'faily'], stdout=out_json)
    juju = jubilant.Juju()

    with pytest.raises(jubilant.ActionError) as excinfo:
        juju.run('mysql/0', 'faily')

    assert excinfo.value.result == jubilant.ActionResult(
        success=False,
        status='failed',
        task_id='42',
        results={'foo': 'bar'},
        return_code=1,
        stderr='Uncaught Exception in charm code: thing happened...',
        message='Failure message',
    )


def test_params(monkeypatch: pytest.MonkeyPatch):
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
    params_path = ''

    def mock_run(args: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        nonlocal params_path
        assert args[:-1] == [
            'juju',
            'run',
            '--format',
            'json',
            'mysql/0',
            'get-password',
            '--params',
        ]
        (params_path,) = args[-1:]  # Ensure there's no extra args
        with open(params_path) as f:
            params = yaml.safe_load(f)
        assert params == {'foo': 1, 'bar': ['ab', 'cd']}
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout)

    monkeypatch.setattr('subprocess.run', mock_run)
    juju = jubilant.Juju()

    result = juju.run('mysql/0', 'get-password', {'foo': 1, 'bar': ['ab', 'cd']})

    assert result == jubilant.ActionResult(
        success=True,
        status='completed',
        task_id='42',
        results={'username': 'user', 'password': 'pass'},
    )
    assert params_path
    assert not os.path.exists(params_path)
