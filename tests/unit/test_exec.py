import pytest

import jubilant

from . import mocks


def test_unit(run: mocks.Run):
    out_json = r"""
{
  "ubuntu/0": {
    "id": "28",
    "results": {
      "return-code": 0,
      "stdout": "foo\n"
    },
    "status": "completed",
    "unit": "ubuntu/0"
  }
}
"""
    run.handle(
        ['juju', 'exec', '--format', 'json', '--unit', 'ubuntu/0', '--', 'echo', 'foo'],
        stdout=out_json,
    )
    juju = jubilant.Juju()

    task = juju.exec('echo', 'foo', unit='ubuntu/0')

    assert task == jubilant.Task(
        id='28',
        status='completed',
        return_code=0,
        stdout='foo\n',
    )
    assert task.success


def test_machine(run: mocks.Run):
    out_json = r"""
{
  "3": {
    "id": "28",
    "results": {
      "return-code": 0,
      "stdout": "bar\n"
    },
    "status": "completed",
    "unit": "ubuntu/0"
  }
}
"""
    run.handle(
        ['juju', 'exec', '--format', 'json', '--machine', '3', '--', 'echo', 'bar'],
        stdout=out_json,
    )
    juju = jubilant.Juju()

    task = juju.exec('echo', 'bar', machine=3)

    assert task == jubilant.Task(
        id='28',
        status='completed',
        return_code=0,
        stdout='bar\n',
    )
    assert task.success


def test_failure(run: mocks.Run):
    out_json = r"""
{
  "ubuntu/0": {
    "id": "28",
    "results": {
      "return-code": 1,
      "stderr": "sleep: invalid time interval\n"
    },
    "status": "completed",
    "unit": "ubuntu/0"
  }
}
"""
    run.handle(
        ['juju', 'exec', '--format', 'json', '--unit', 'ubuntu/0', '--', 'sleep x'],
        stdout=out_json,
    )
    juju = jubilant.Juju()

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.exec('sleep x', unit='ubuntu/0')

    task = excinfo.value.task
    assert task == jubilant.Task(
        id='28',
        status='completed',
        return_code=1,
        stderr='sleep: invalid time interval\n',
    )
    assert not task.success


def test_machine_not_found(run: mocks.Run):
    run.handle(['juju', 'exec', '--format', 'json', '--machine', '0', '--', 'echo'])
    juju = jubilant.Juju()

    with pytest.raises(ValueError):
        juju.exec('echo', machine=0)


def test_unit_not_found(run: mocks.Run):
    run.handle(['juju', 'exec', '--format', 'json', '--unit', 'u/0', '--', 'echo'])
    juju = jubilant.Juju()

    with pytest.raises(ValueError):
        juju.exec('echo', unit='u/0')


def test_no_target_arg():
    juju = jubilant.Juju()
    with pytest.raises(TypeError):
        juju.exec('echo')  # type: ignore
