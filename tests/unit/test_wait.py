import logging

import pytest

import jubilant

from . import mocks
from .fake_statuses import MINIMAL_JSON, MINIMAL_STATUS


def test_ready_normal(run: mocks.Run, time: mocks.Time):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()

    status = juju.wait(lambda _: True)

    assert len(run.calls) == 3
    assert time.monotonic() == 2
    assert status == MINIMAL_STATUS


def test_logging(run: mocks.Run, time: mocks.Time, caplog: pytest.LogCaptureFixture):
    run.handle(['juju', 'status', '--format', 'json'], stdout=MINIMAL_JSON)
    juju = jubilant.Juju()
    caplog.set_level(logging.INFO, logger='jubilant')

    juju.wait(lambda _: True)

    logs = [r for r in caplog.records if r.msg.startswith('wait:')]
    assert len(logs) == 1  # only logs on first call or when status changes
    message = logs[0].getMessage()
    assert 'status changed' in message
    assert 'mdl' in message


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
