from __future__ import annotations

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest

from . import mocks


@pytest.fixture
def run(monkeypatch: pytest.MonkeyPatch) -> Generator[mocks.Run]:
    """Pytest fixture that patches subprocess.run with mocks.Run."""
    run_mock = mocks.Run()
    monkeypatch.setattr('subprocess.run', run_mock)
    yield run_mock
    assert len(run_mock.calls) >= 1, 'subprocess.run not called'


@pytest.fixture
def time(monkeypatch: pytest.MonkeyPatch) -> Generator[mocks.Time]:
    """Pytest fixture that patches time.monotonic and time.sleep with mocks.Time."""
    time_mock = mocks.Time()
    monkeypatch.setattr('time.monotonic', time_mock.monotonic)
    monkeypatch.setattr('time.sleep', time_mock.sleep)
    yield time_mock


@pytest.fixture
def mock_file(monkeypatch: pytest.MonkeyPatch) -> Generator[mocks.NamedTemporaryFile]:
    """Pytest fixture that patches tempfile.NamedTemporaryFile with mocks.File."""
    file_mock = mocks.NamedTemporaryFile()
    monkeypatch.setattr('tempfile.NamedTemporaryFile', file_mock)
    yield file_mock


@pytest.fixture(scope='function', autouse=True)
def juju_non_snap(monkeypatch: pytest.MonkeyPatch) -> None:
    """Pytest fixture that patches shutil.which to make ``Juju._juju_is_snap()`` return ``True``.

    Autouse because we want our unit tests to be isolated from the external environment.
    If a test relies on `Juju._juju_is_snap()` returning ``False``, it can override with
    monkeypatch.setattr.

    Override example::

        monkeypatch.setattr('shutil.which', lambda _: '/snap/bin/juju')
    """
    monkeypatch.setattr('shutil.which', lambda _: '/bin/juju')  # type: ignore


@pytest.fixture
def mock_wait(monkeypatch: pytest.MonkeyPatch) -> Generator[MagicMock]:
    """Pytest fixture that patches jubilant.Juju.wait with a MagicMock."""
    mock = MagicMock()
    monkeypatch.setattr('jubilant.Juju.wait', mock)
    yield mock
