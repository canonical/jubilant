from collections.abc import Generator

import pytest

from . import mocks


@pytest.fixture
def run(monkeypatch: pytest.MonkeyPatch) -> Generator[mocks.Run, None, None]:
    """Pytest fixture that patches subprocess.run with mocks.Run."""
    run_mock = mocks.Run()
    monkeypatch.setattr('subprocess.run', run_mock)
    yield run_mock
    assert run_mock.call_count >= 1, 'subprocess.run not called'


@pytest.fixture
def time(monkeypatch: pytest.MonkeyPatch) -> Generator[mocks.Time, None, None]:
    """Pytest fixture that patches time.monotonic and time.sleep with mocks.Time."""
    time_mock = mocks.Time()
    monkeypatch.setattr('time.monotonic', time_mock.monotonic)
    monkeypatch.setattr('time.sleep', time_mock.sleep)
    yield time_mock
