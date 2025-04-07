import logging
import subprocess

import pytest

import jubilant

from . import mocks


def test_success(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'microk8s'], stdout='bootstrapped\n')
    juju = jubilant.Juju()

    stdout = juju.cli('bootstrap', 'microk8s')

    assert stdout == 'bootstrapped\n'


def test_logging_normal(run: mocks.Run, caplog: pytest.LogCaptureFixture):
    run.handle(['juju', 'deploy', '--model', 'mdl', 'app1'])
    juju = jubilant.Juju(model='mdl')
    caplog.set_level(logging.INFO, logger='jubilant')

    juju.cli('deploy', 'app1')

    logs = [r for r in caplog.records if r.msg.startswith('cli:')]
    assert len(logs) == 1
    assert logs[0].getMessage() == 'cli: juju deploy --model mdl app1'


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


def test_stdin(run: mocks.Run):
    run.handle(['juju', 'ssh', 'mysql/0', 'pg_restore ...'], stdout='restored\n')
    juju = jubilant.Juju()

    stdout = juju.cli('ssh', 'mysql/0', 'pg_restore ...', stdin='PASSWORD')

    assert stdout == 'restored\n'
    assert run.calls[0].stdin == 'PASSWORD'
