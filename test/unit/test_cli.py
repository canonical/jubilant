import subprocess

import pytest

import jubilant

from . import mocks


def test_success(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'microk8s'], stdout='bootstrapped\n')
    juju = jubilant.Juju()

    stdout = juju.cli('bootstrap', 'microk8s')

    assert stdout == 'bootstrapped\n'


def test_error(run: mocks.Run):
    run.handle(['juju', 'error'], returncode=3, stdout='OUT', stderr='ERR')
    juju = jubilant.Juju()

    with pytest.raises(jubilant.CLIError) as excinfo:
        juju.cli('error')

    exc = excinfo.value
    assert isinstance(exc, subprocess.CalledProcessError)
    assert exc.returncode == 3
    assert exc.cmd == ['juju', 'error']
    assert exc.stdout == 'OUT'
    assert exc.stderr == 'ERR'
    assert str(exc).endswith('Stdout:\nOUT\nStderr:\nERR')


def test_include_model_no_model(run: mocks.Run):
    run.handle(['juju', 'test'], stdout='OUT')
    juju = jubilant.Juju()

    stdout = juju.cli('test')

    assert stdout == 'OUT'


def test_include_model_with_model(run: mocks.Run):
    run.handle(['juju', 'test', '--model', 'mdl'], stdout='OUT')
    juju = jubilant.Juju(model='mdl')

    stdout = juju.cli('test')

    assert stdout == 'OUT'


def test_exclude_model_no_model(run: mocks.Run):
    run.handle(['juju', 'test'], stdout='OUT')
    juju = jubilant.Juju()

    stdout = juju.cli('test', include_model=False)

    assert stdout == 'OUT'


def test_exclude_model_with_model(run: mocks.Run):
    run.handle(['juju', 'test'], stdout='OUT')
    juju = jubilant.Juju(model='mdl')

    stdout = juju.cli('test', include_model=False)

    assert stdout == 'OUT'
