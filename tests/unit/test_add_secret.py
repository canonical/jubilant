from __future__ import annotations

import os.path
import subprocess
from typing import Any

import pytest
import yaml

import jubilant


def test_normal(monkeypatch: pytest.MonkeyPatch):
    path = None

    def mock_run(args: list[str], **_: Any) -> subprocess.CompletedProcess[str]:
        nonlocal path
        *most_args, path = args
        assert most_args == [
            'juju',
            'add-secret',
            'sec1',
            '--info',
            'A description.',
            '--file',
        ]
        with open(path) as f:
            params = yaml.safe_load(f)
        assert params == {'username': 'usr', 'password': 'hunter2'}
        return subprocess.CompletedProcess(
            args=args, returncode=0, stdout='secret:0123456789abcdefghji\n'
        )

    monkeypatch.setattr('subprocess.run', mock_run)
    juju = jubilant.Juju()

    secret_uri = juju.add_secret(
        'sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.'
    )

    assert isinstance(secret_uri, jubilant.SecretURI)
    assert secret_uri == 'secret:0123456789abcdefghji'  # noqa: S105
    assert path is not None
    assert not os.path.exists(path)
