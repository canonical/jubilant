import pytest

import jubilant


def test_task_success():
    task = jubilant.Task(id='42', status='completed', return_code=0)
    assert task.success

    task = jubilant.Task(id='42', status='completed', return_code=1)
    assert not task.success

    task = jubilant.Task(id='42', status='failed', return_code=0)
    assert not task.success

    task = jubilant.Task(id='42', status='failed', return_code=1)
    assert not task.success


def test_task_raise_on_failure():
    task = jubilant.Task(id='42', status='completed', return_code=0)
    task.raise_on_failure()

    task = jubilant.Task(id='42', status='completed', return_code=1)
    with pytest.raises(jubilant.TaskError):
        task.raise_on_failure()


def test_task_str_minimal():
    task = jubilant.Task(id='42', status='completed')
    assert str(task) == "Task 42: status 'completed', return code 0"


def test_task_str_full():
    task = jubilant.Task(
        id='1',
        status='failed',
        results={'foo': 'bar'},
        return_code=3,
        stdout='STDOUT',
        stderr='STDERR',
        message='Some kind of failure',
        log=['LOG 1', 'LOG 2'],
    )
    assert (
        str(task)
        == """\
Task 1: status 'failed', return code 3, details:
Results: {'foo': 'bar'}
Stdout:
STDOUT
Stderr:
STDERR
Message: Some kind of failure
Log:
LOG 1
LOG 2"""
    )


def test_task_repr():
    task = jubilant.Task(id='42', status='completed')
    assert eval(repr(task), {'Task': jubilant.Task}) == task


def test_task_error_str():
    task = jubilant.Task(id='42', status='completed')
    exc = jubilant.TaskError(task)
    assert str(exc) == 'task error: ' + str(task)
