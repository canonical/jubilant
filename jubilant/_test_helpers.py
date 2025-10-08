from __future__ import annotations

import contextlib
import logging
import secrets
import subprocess
from collections.abc import Mapping
from typing import Generator

from ._juju import ConfigValue, Juju

logger = logging.getLogger('jubilant')


@contextlib.contextmanager
def temp_model(
    keep: bool = False,
    controller: str | None = None,
    cloud: str | None = None,
    config: Mapping[str, ConfigValue] | None = None,
    credential: str | None = None,
) -> Generator[Juju]:
    """Context manager to create a temporary model for running tests in.

    This creates a new model with a random name in the format ``jubilant-abcd1234``, and destroys
    it and its storage when the context manager exits.

    If destroying the model takes longer than 10 minutes, log an error and return successfully.
    This is mainly to work around issues with Microk8s destroy-model hanging indefinitely.

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
        cloud: Name of cloud or region (or cloud/region) to use for the temporary model.
        config: Temporary model configuration as key-value pairs, for example,
            ``{'image-stream': 'daily'}``.
        credential: Name of cloud credential to use for the temporary model.
    """
    juju = Juju()
    model = 'jubilant-' + secrets.token_hex(4)  # 4 bytes (8 hex digits) should be plenty
    juju.add_model(model, cloud=cloud, controller=controller, config=config, credential=credential)
    try:
        yield juju
    finally:
        if not keep:
            assert juju.model is not None
            try:
                # We're not using juju.destroy_model() here, as it doesn't have a timeout
                # parameter. If we add such a parameter, we can update this.
                args = ['destroy-model', juju.model, '--no-prompt', '--destroy-storage', '--force']
                juju._cli(*args, include_model=False, timeout=10 * 60)
                juju.model = None
            except subprocess.TimeoutExpired as exc:
                logger.error(
                    'timeout destroying model: %s\nStdout:\n%s\nStderr:\n%s',
                    exc,
                    exc.stdout,
                    exc.stderr,
                )
