from __future__ import annotations

import contextlib
import secrets
from typing import Generator

from ._juju import Juju


@contextlib.contextmanager
def temp_model(keep: bool = False, controller: str | None = None) -> Generator[Juju]:
    """Context manager to create a temporary model for running tests in.

    This creates a new model with a random name in the format ``jubilant-abcd1234``, and destroys
    it and its storage when the context manager exits.

    Provides a :class:`Juju` instance to operate on.

    If you want to configure its parameters, such as ``wait_timeout``, set the appropriate
    attribute inside the ``with`` statement. For example, to create a pytest fixture using
    ``temp_model``::

        @pytest.fixture(scope='module')
        def juju():
            with jubilant.temp_model() as juju:
                juju.wait_timeout = 10 * 60
                yield juju  # run the test

    Args:
        keep: If true, keep the created model around when the context manager exits.
        controller: Name of controller where the temporary model will be added.
    """
    juju = Juju()
    model = 'jubilant-' + secrets.token_hex(4)  # 4 bytes (8 hex digits) should be plenty
    juju.add_model(model, controller=controller)
    try:
        yield juju
    finally:
        if not keep:
            assert juju.model is not None
            juju.destroy_model(juju.model, destroy_storage=True, force=True)
