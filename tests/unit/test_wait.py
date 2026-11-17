import json
import logging
import subprocess
from typing import Any, NoReturn

import pytest

import jubilant

from . import mocks
from .fake_statuses import DATABASE_WEBAPP_JSON, MINIMAL_JSON, MINIMAL_STATUS, SNAPPASS_JSON


def test_ready_normal(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.wait(lambda _: True)

    assert len(run.calls) == 3
    assert time.monotonic() == 2
    assert status == MINIMAL_STATUS


def test_logging_wait_debug(run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()
    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.DEBUG, logger='jubilant.wait')

    juju.wait(lambda _: True)

    assert len(caplog.records) == 2  # status-changed diff, plus the ready-after-Xs summary
    record = caplog.records[0]
    assert record.levelname == 'DEBUG'
    message = record.getMessage()
    assert (
        message
        == """wait: status changed:
+ .model.name = 'mdl'
+ .model.type = 'typ'
+ .model.controller = 'ctl'
+ .model.cloud = 'aws'
+ .model.version = '3.0.0'"""
    )
    ready_record = caplog.records[1]
    assert ready_record.name == 'jubilant'
    assert ready_record.levelname == 'INFO'
    # Three successes needed (the default), with a 1s sleep between each.
    assert ready_record.getMessage() == 'wait: ready after 2.0s'


def test_logging_wait_info(run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture):
    run.handle(['juju', 'status', '--format', 'json'], stdout=SNAPPASS_JSON)
    juju = jubilant.Juju()
    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.INFO, logger='jubilant.wait')

    juju.wait(lambda _: True)

    assert len(caplog.records) == 3  # 1 app line + 1 unit line + ready-after-Xs summary
    record = caplog.records[0]
    assert record.levelname == 'INFO'
    message = record.getMessage()
    assert message == '[snappass-test] status: active (snappass started)'
    unit_record = caplog.records[1]
    assert unit_record.levelname == 'INFO'
    assert unit_record.getMessage() == '[snappass-test/0] status: active (snappass started)'
    ready_record = caplog.records[2]
    assert ready_record.name == 'jubilant'
    assert ready_record.levelname == 'INFO'
    # Three successes needed (the default), with a 1s sleep between each.
    assert ready_record.getMessage() == 'wait: ready after 2.0s'


def test_logging_wait_info_multiples(
    run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture
):
    # Test that we log each app status change individually.
    run.handle(['juju', 'status', '--format', 'json'], stdout=DATABASE_WEBAPP_JSON)
    juju = jubilant.Juju()
    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.INFO, logger='jubilant.wait')

    juju.wait(lambda _: True)

    assert len(caplog.records) == 5  # 2 apps, each app has 2 units, plus ready-after-Xs summary
    for record in caplog.records[:-1]:
        assert record.levelname == 'INFO'
    assert caplog.records[-1].name == 'jubilant'
    # Three successes needed (the default), with a 1s sleep between each.
    assert caplog.records[-1].getMessage() == 'wait: ready after 2.0s'


def test_logging_wait_app_error(
    run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture
):
    error_snappass_json = json.loads(SNAPPASS_JSON)
    error_snappass_json['applications']['snappass-test']['application-status']['current'] = 'error'
    error_snappass_json['applications']['snappass-test']['application-status']['message'] = (
        'something bad happened'
    )

    run.handle(['juju', 'status', '--format', 'json'], stdout=json.dumps(error_snappass_json))
    juju = jubilant.Juju()

    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.INFO, logger='jubilant.wait')

    juju.wait(lambda _: True)

    assert len(caplog.records) == 3  # 1 app error line + 1 unit line + ready-after-Xs summary
    record = caplog.records[0]
    assert record.levelname == 'ERROR'
    message = record.getMessage()
    assert message == '[snappass-test] status: error (something bad happened)'
    unit_record = caplog.records[1]
    assert unit_record.levelname == 'INFO'
    assert unit_record.getMessage() == '[snappass-test/0] status: active (snappass started)'
    ready_record = caplog.records[2]
    assert ready_record.name == 'jubilant'
    assert ready_record.levelname == 'INFO'
    # Three successes needed (the default), with a 1s sleep between each.
    assert ready_record.getMessage() == 'wait: ready after 2.0s'


def test_logging_wait_error_unit(
    run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture
):
    error_snappass_json = json.loads(SNAPPASS_JSON)
    unit_json = error_snappass_json['applications']['snappass-test']['units']['snappass-test/0']
    unit_json['workload-status']['current'] = 'error'
    unit_json['workload-status']['message'] = 'something bad happened'

    run.handle(['juju', 'status', '--format', 'json'], stdout=json.dumps(error_snappass_json))
    juju = jubilant.Juju()

    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.INFO, logger='jubilant.wait')

    juju.wait(lambda _: True)

    assert len(caplog.records) == 3  # 1 app line + 1 unit error line + ready-after-Xs summary
    record = caplog.records[0]
    assert record.levelname == 'INFO'
    message = record.getMessage()
    assert message == '[snappass-test] status: active (snappass started)'
    unit_record = caplog.records[1]
    assert unit_record.levelname == 'ERROR'
    assert unit_record.getMessage() == '[snappass-test/0] status: error (something bad happened)'
    ready_record = caplog.records[2]
    assert ready_record.name == 'jubilant'
    assert ready_record.levelname == 'INFO'
    # Three successes needed (the default), with a 1s sleep between each.
    assert ready_record.getMessage() == 'wait: ready after 2.0s'


def test_logging_wait_no_change(
    run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture
):
    snappass_json = json.loads(SNAPPASS_JSON)

    run.handle(['juju', 'status', '--format', 'json'], stdout=json.dumps(snappass_json))
    juju = jubilant.Juju()

    count = 0

    def helper() -> bool:
        # Return False once, then True.
        nonlocal count
        if count < 1:
            count += 1
            return False

        return True

    caplog.set_level(logging.INFO, logger='jubilant')
    caplog.set_level(logging.INFO, logger='jubilant.wait')

    juju.wait(lambda _: helper())

    assert len(caplog.records) == 3  # 1 unit + 1 app the first time, plus ready-after-Xs summary
    ready_record = caplog.records[2]
    assert ready_record.name == 'jubilant'
    assert ready_record.levelname == 'INFO'
    # One not-ready poll, then three successes (the default), with a 1s sleep between each.
    assert ready_record.getMessage() == 'wait: ready after 3.0s'


def test_logging_wait_summary_with_status_logs_disabled(
    run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture
):
    run.handle(['juju', 'status', '--format', 'json'], stdout=SNAPPASS_JSON)
    juju = jubilant.Juju()
    caplog.set_level(logging.WARNING, logger='jubilant.wait')
    caplog.set_level(logging.INFO, logger='jubilant')

    juju.wait(lambda _: True)

    # Three successes needed (the default), with a 1s sleep between each.
    assert [(r.name, r.getMessage()) for r in caplog.records] == [
        ('jubilant', 'wait: ready after 2.0s'),
    ]


def test_with_model(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--model', 'mdl', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju(model='mdl')

    status = juju.wait(lambda _: True)

    assert len(run.calls) == 3
    assert time.monotonic() == 2
    assert status == MINIMAL_STATUS


def test_ready_glitch(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    n = 0

    def ready_glitch(_: jubilant.Status):
        nonlocal n
        n += 1
        return n != 2  # Glitch on second call

    status = juju.wait(ready_glitch)

    # Should wait for three successful calls to ready in a row:
    # ready, not ready, ready, ready, ready (5 total)
    assert len(run.calls) == 5
    assert time.monotonic() == 4
    assert status == MINIMAL_STATUS


def test_modified_delay_and_successes(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.wait(lambda _: True, delay=0.75, successes=5)

    assert len(run.calls) == 5
    assert time.monotonic() == 3.0
    assert status == MINIMAL_STATUS


def test_error(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    with pytest.raises(jubilant.WaitError) as excinfo:
        juju.wait(lambda _: True, error=lambda _: True)

    assert len(run.calls) == 1
    assert time.monotonic() == 0
    assert 'mdl' in str(excinfo.value)
    assert str(excinfo.value).startswith(
        'error function test_error.<locals>.<lambda> returned true after 0.0s\n'
    )


def test_timeout_default(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError) as excinfo:
        juju.wait(lambda _: False)

    assert len(run.calls) == 180
    assert time.monotonic() == 180
    assert 'mdl' in str(excinfo.value)


def test_timeout_override(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError) as excinfo:
        juju.wait(lambda _: False, timeout=5)

    assert len(run.calls) == 5
    assert time.monotonic() == 5
    assert 'mdl' in str(excinfo.value)


def test_timeout_zero(time: mocks.Time):
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError) as excinfo:
        juju.wait(lambda _: False, timeout=0)

    assert time.monotonic() == 0
    assert 'mdl' not in str(excinfo.value)


def test_timeout_bounds_status_call(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError):
        juju.wait(lambda _: False, timeout=3)

    # Each status call gets only the time left until the overall deadline.
    assert [call.timeout for call in run.calls] == [3, 2, 1]


def test_timeout_status_call_hangs(monkeypatch: pytest.MonkeyPatch, time: mocks.Time):
    timeouts: list[float | None] = []

    def hanging_run(args: list[str], **kwargs: Any) -> NoReturn:
        # Simulate "juju status" hanging (for example, an unreachable controller) until
        # subprocess.run kills it at the timeout it was given.
        timeouts.append(kwargs['timeout'])
        time.sleep(kwargs['timeout'])
        raise subprocess.TimeoutExpired(args, kwargs['timeout'])

    monkeypatch.setattr('subprocess.run', hanging_run)
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError) as excinfo:
        juju.wait(lambda _: False, timeout=2)

    assert timeouts == [2]
    assert time.monotonic() == 2
    assert str(excinfo.value) == 'wait timed out after 2s'


def test_timeout_status_call_hangs_after_status(monkeypatch: pytest.MonkeyPatch, time: mocks.Time):
    calls = 0

    def run_then_hang(args: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        # The first status call succeeds; the next one hangs until its timeout.
        nonlocal calls
        calls += 1
        if calls == 1:
            return subprocess.CompletedProcess(args, 0, stdout=MINIMAL_JSON, stderr='')
        time.sleep(kwargs['timeout'])
        raise subprocess.TimeoutExpired(args, kwargs['timeout'])

    monkeypatch.setattr('subprocess.run', run_then_hang)
    juju = jubilant.Juju()

    with pytest.raises(TimeoutError) as excinfo:
        juju.wait(lambda _: False, timeout=5)

    assert calls == 2
    assert time.monotonic() == 5
    # The status from before the hang is still included in the error.
    assert 'mdl' in str(excinfo.value)
