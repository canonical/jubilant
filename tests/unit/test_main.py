"""Tests for Jubilant CLI."""

from __future__ import annotations

import json
import re
from typing import Any
from unittest.mock import MagicMock

import pytest

import jubilant
from jubilant import Status
from jubilant._main import main

from .fake_statuses import MINIMAL_JSON, SNAPPASS_JSON


@pytest.mark.parametrize(
    'argv_str',
    [
        'wait status.model.name=="mdl"',
        'wait status.model.name=="mdl" --error status.apps["snappass-test"].app_status.current=="error"',
        'wait --model mycontroller:alice/my-model --juju-cli-bin foo True --error False --timeout 10.0 --successes 3 --delay 2.0',
        'wait status.model.name=="mdl" --verbose',
        'wait status.model.name=="mdl" --quiet',
        'wait --verbose status.model.name=="mdl"',
        'wait --quiet status.model.name=="mdl"',
    ],
)
def test_parse_wait_okay(argv_str: str, mock_wait: MagicMock) -> None:
    """Test parsing the wait arguments."""

    exit_code = main(argv_str.split())

    assert exit_code == 0
    assert mock_wait.call_count == 1


def test_parse_version(capsys: pytest.CaptureFixture[str], mock_wait: MagicMock) -> None:
    """Test parsing the version command."""

    exit_code = main(['version'])

    assert exit_code == 0
    assert mock_wait.call_count == 0  # Print version and exit.
    captured = capsys.readouterr()

    # Assert only the version string exists in stdout.
    version_pattern = r'^\d+\.\d+\.\d+$'
    assert re.match(version_pattern, captured.out.strip())  # strip the newline from print


@pytest.mark.parametrize(
    'argv_str',
    [
        pytest.param(
            'wait',
            id='missing_ready',
        ),
        pytest.param(
            'wait --unknown-argument',
            id='unknown_argument',
        ),
        pytest.param(
            'wait --error',
            id='error_missing_value',
        ),
        pytest.param(
            'unknown-command --some-argument',
            id='unknown_command',
        ),
        pytest.param(
            'wait True --verbose --quiet',
            id='one_verbosity_argument_only',
        ),
    ],
)
def test_parse_error(argv_str: str) -> None:
    with pytest.raises(SystemExit):  # Raised by the ArgumentParser object.
        main(argv_str.split())


def test_parse_empty() -> None:
    """Test running the CLI without any arguments."""

    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code != 0


def test_defaults_no_error_expression(mock_wait: MagicMock) -> None:
    exit_code = main(['wait', 'status.model.name=="mdl"'])

    assert exit_code == 0
    assert mock_wait.call_count == 1

    kwargs = mock_wait.call_args.kwargs
    assert all(
        k in kwargs
        for k in [
            'ready',
            'delay',
            'timeout',
            'error',
            'successes',
        ]
    )
    assert kwargs['error'] is None


def test_defaults_with_error_expression(mock_wait: MagicMock) -> None:
    exit_code = main(
        [
            'wait',
            'status.model.name=="mdl"',
            '--error',
            'status.apps["snappass-test"].app_status.current=="error"',
        ],
    )

    assert exit_code == 0
    assert mock_wait.call_count == 1

    kwargs = mock_wait.call_args.kwargs
    assert all(
        k in kwargs
        for k in [
            'ready',
            'delay',
            'error',
            'timeout',
            'successes',
        ]
    )


@pytest.mark.parametrize(
    'ready_str',
    [
        'status.model.name=="tt"',
        'status.apps["snappass-test"].charm=="snappass-test"',
    ],
)
def test_eval_context_ok(ready_str: str, mock_wait: MagicMock) -> None:
    status = Status._from_dict(json.loads(SNAPPASS_JSON))

    exit_code = main([
        'wait',
        ready_str,
    ])

    assert exit_code == 0
    assert mock_wait.call_count == 1
    assert mock_wait.call_args.kwargs['ready'](status)


@pytest.mark.parametrize(
    'expression',
    [
        pytest.param(
            'outside[0]=="boo"',
            id='use_undefine_variable',
        ),
        pytest.param(
            'os.name=="posix"',
            id='use_non_included_module',
        ),
    ],
)
def test_eval_context_error(
    expression: str,
    mock_wait: MagicMock,
) -> None:
    status = Status._from_dict(json.loads(MINIMAL_JSON))
    main(['wait', expression])
    with pytest.raises(NameError):
        mock_wait.call_args.kwargs['ready'](status)

    main(['wait', 'True', '--error', expression])
    with pytest.raises(NameError):
        mock_wait.call_args.kwargs['error'](status)


def test_wait_error_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_wait_error(*args: Any, **kwargs: Any) -> None:
        raise jubilant.WaitError('error function returned true\n...status...')

    monkeypatch.setattr('jubilant.Juju.wait', raise_wait_error)

    exit_code = main(['wait', 'True'])
    assert exit_code != 0


def test_timeout_error_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_timeout_error(*args: Any, **kwargs: Any) -> None:
        raise TimeoutError('wait timed out after 180.0s\n...status...')

    monkeypatch.setattr('jubilant.Juju.wait', raise_timeout_error)

    exit_code = main(['wait', 'True'])
    assert exit_code == 124


def test_keyboard_interrupt_while_waiting_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_keyboard_interrupt(*args: Any, **kwargs: Any) -> None:
        raise KeyboardInterrupt()

    monkeypatch.setattr('jubilant.Juju.wait', raise_keyboard_interrupt)

    exit_code = main(['wait', 'True'])
    assert exit_code == 130


@pytest.mark.parametrize(
    'expression',
    [
        pytest.param('0/0', id='division_by_zero'),
        pytest.param('+', id='syntax_error'),
    ],
)
def test_exception_from_ready_expression(
    expression: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _helper(*args: Any, **kwargs: Any) -> None:
        kwargs['ready'](MagicMock())

    monkeypatch.setattr('jubilant.Juju.wait', _helper)

    assert main(['wait', expression]) != 0


def test_juju_cli_bin(mock_wait: MagicMock) -> None:
    exit_code = main([
        'wait',
        '--juju-cli-bin',
        '/snap/juju',
        'juju.cli_binary=="/snap/juju"',
    ])
    assert exit_code == 0

    wait_kwargs = mock_wait.call_args.kwargs
    status = Status._from_dict(json.loads(MINIMAL_JSON))

    assert wait_kwargs['ready'](status)


def test_juju_cli_bin_default(mock_wait: MagicMock) -> None:
    exit_code = main([
        'wait',
        'juju.cli_binary=="juju"',
    ])
    assert exit_code == 0

    wait_kwargs = mock_wait.call_args.kwargs
    status = Status._from_dict(json.loads(MINIMAL_JSON))

    assert wait_kwargs['ready'](status)


def test_model(mock_juju: MagicMock) -> None:
    exit_code = main([
        'wait',
        '--model',
        'mycontroller:alice/my-model',
        'True',
    ])
    assert exit_code == 0

    wait_kwargs = mock_juju.call_args.kwargs
    assert wait_kwargs['model'] == 'mycontroller:alice/my-model'


def test_model_none(mock_juju: MagicMock) -> None:
    exit_code = main([
        'wait',
        'True',
    ])
    assert exit_code == 0

    wait_kwargs = mock_juju.call_args.kwargs
    assert wait_kwargs['model'] is None
