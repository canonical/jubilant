import logging
import subprocess
from typing import Any

import pytest

import jubilant

from . import mocks


def mock_token_hex(n: int):
    assert n == 4
    return 'abcd1234'


def test_defaults(run: mocks.Run, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('secrets.token_hex', mock_token_hex)
    run.handle(['juju', 'add-model', '--no-switch', 'jubilant-abcd1234'])
    run.handle(['juju', 'deploy', '--model', 'jubilant-abcd1234', 'app1'])
    run.handle(
        [
            'juju',
            'destroy-model',
            'jubilant-abcd1234',
            '--no-prompt',
            '--destroy-storage',
            '--force',
        ]
    )

    with jubilant.temp_model() as juju:
        assert juju.model == 'jubilant-abcd1234'
        assert len(run.calls) == 1
        assert run.calls[0].args[1] == 'add-model'

        juju.deploy('app1')

        assert len(run.calls) == 2
        assert run.calls[1].args[1] == 'deploy'

    assert juju.model is None
    assert len(run.calls) == 3
    assert run.calls[2].args[1] == 'destroy-model'


def test_other_args(run: mocks.Run, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('secrets.token_hex', mock_token_hex)
    run.handle(
        [
            'juju',
            'add-model',
            '--no-switch',
            'jubilant-abcd1234',
            'localhost',
            '--controller',
            'ctl',
            '--config',
            'x=true',
            '--config',
            'y=1',
            '--config',
            'z=ss',
            '--credential',
            'cc',
        ]
    )
    run.handle(['juju', 'deploy', '--model', 'ctl:jubilant-abcd1234', 'app1'])
    run.handle(
        [
            'juju',
            'destroy-model',
            'ctl:jubilant-abcd1234',
            '--no-prompt',
            '--destroy-storage',
            '--force',
        ]
    )

    with jubilant.temp_model(
        controller='ctl',
        config={'x': True, 'y': 1, 'z': 'ss'},
        credential='cc',
        cloud='localhost',
    ) as juju:
        assert juju.model == 'ctl:jubilant-abcd1234'
        assert len(run.calls) == 1
        assert run.calls[0].args[1] == 'add-model'

        juju.deploy('app1')

        assert len(run.calls) == 2
        assert run.calls[1].args[1] == 'deploy'

    assert juju.model is None
    assert len(run.calls) == 3
    assert run.calls[2].args[1] == 'destroy-model'
    assert run.calls[2].args[2] == 'ctl:jubilant-abcd1234'


def test_other_args_keep(run: mocks.Run, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr('secrets.token_hex', mock_token_hex)
    run.handle(
        [
            'juju',
            'add-model',
            '--no-switch',
            'jubilant-abcd1234',
            'localhost',
            '--controller',
            'ctl',
            '--config',
            'x=true',
            '--config',
            'y=1',
            '--config',
            'z=ss',
            '--credential',
            'cc',
        ]
    )
    run.handle(['juju', 'deploy', '--model', 'ctl:jubilant-abcd1234', 'app1'])

    with jubilant.temp_model(
        keep=True,
        controller='ctl',
        config={'x': True, 'y': 1, 'z': 'ss'},
        credential='cc',
        cloud='localhost',
    ) as juju:
        assert juju.model == 'ctl:jubilant-abcd1234'
        assert len(run.calls) == 1
        assert run.calls[0].args[1] == 'add-model'

        juju.deploy('app1')

        assert len(run.calls) == 2
        assert run.calls[1].args[1] == 'deploy'

    assert juju.model == 'ctl:jubilant-abcd1234'
    assert len(run.calls) == 2


def test_destroy_timeout(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture):
    def mock_run(args: 'list[str]', **kwargs: 'dict[str, Any]'):
        if args[1] == 'add-model':
            return subprocess.CompletedProcess(args, 0, '', '')
        assert args == [
            'juju',
            'destroy-model',
            'jubilant-abcd1234',
            '--no-prompt',
            '--destroy-storage',
            '--force',
        ]
        assert kwargs['timeout'] == 10 * 60
        raise subprocess.TimeoutExpired(args, 10 * 60, 'STDOUT', 'STDERR')

    monkeypatch.setattr('subprocess.run', mock_run)
    monkeypatch.setattr('secrets.token_hex', mock_token_hex)
    caplog.set_level(logging.ERROR, logger='jubilant')

    with jubilant.temp_model():
        pass

    assert 'timeout destroying model' in caplog.records[0].getMessage()
