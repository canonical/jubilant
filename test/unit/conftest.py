import unittest.mock
from collections.abc import Generator

import mocks
import pytest


@pytest.fixture
def run() -> Generator[mocks.Run, None, None]:
    run_mock = mocks.Run()
    with unittest.mock.patch('subprocess.run', run_mock):
        yield run_mock
