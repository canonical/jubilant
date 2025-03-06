"""Fixtures for using Jubilant with pytest."""

import secrets
from collections.abc import Generator

import pytest

from ._juju import Juju

__all__ = ['juju']


@pytest.fixture  # TODO: what should the scope be?
def juju() -> Generator[Juju, None, None]:
    """Fixture that creates a model and destroys it when done."""
    juju = Juju()
    model = 'jubilant-' + secrets.token_hex(6)  # 6 bytes (12 hex digits) should be plenty
    juju.add_model(model)
    try:
        yield juju
    finally:
        juju.destroy_model(model, force=True)  # TODO: anything wrong with using --force here?
