import subprocess

import mocks
import pytest

import jubilant


def test_cli_success(run: mocks.Run):
    run.handle(['juju', 'bootstrap', 'microk8s'], stdout='bootstrapped\n')
    juju = jubilant.Juju()

    stdout = juju.cli('bootstrap', 'microk8s')

    assert stdout == 'bootstrapped\n'


def test_cli_error(run: mocks.Run):
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
