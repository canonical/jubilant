from collections.abc import Generator
from unittest import mock

import mocks
import pytest


@pytest.fixture
def run() -> Generator[mocks.Run, None, None]:
    """Pytest fixture that patches subprocess.run with mocks.Run."""
    run_mock = mocks.Run()
    with mock.patch('subprocess.run', run_mock):
        yield run_mock
    assert run_mock.call_count >= 1, 'subprocess.run not called'


@pytest.fixture
def time() -> Generator[mocks.Time, None, None]:
    """Pytest fixture that patches time.monotonic and time.sleep with mocks.Time."""
    time_mock = mocks.Time()
    with (
        mock.patch('time.monotonic', time_mock.monotonic),
        mock.patch('time.sleep', time_mock.sleep),
    ):
        yield time_mock
