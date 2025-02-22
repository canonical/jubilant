import unittest.mock
from collections.abc import Generator

import mocks
import pytest


@pytest.fixture
def run() -> Generator[mocks.Run, None, None]:
    """Pytest fixture that patches subprocess.run with a mocks.Run instance."""
    run_mock = mocks.Run()
    with unittest.mock.patch('subprocess.run', run_mock):
        yield run_mock
    assert run_mock.call_count >= 1, 'subprocess.run not called'
