import contextlib
import secrets
from typing import Generator, Union

from ._juju import Juju


@contextlib.contextmanager
def temp_model(
    keep: bool = False, controller: Union[str, None] = None
) -> Generator[Juju, None, None]:
    """Context manager to create a temporary model for running tests in.

    This creates a new model with a random name in the format ``jubilant-abcd1234``, and destroys
    it and its storage when the context manager exits.

    Provides a :class:`Juju` instance to operate on.

    Args:
        keep: If true, keep the created model around when the context manager exits.
        controller: The controller where the temp model will be deployed.
    """
    juju = Juju()
    model = 'jubilant-' + secrets.token_hex(4)  # 4 bytes (8 hex digits) should be plenty
    juju.add_model(model, controller=controller)
    try:
        yield juju
    finally:
        if not keep:
            juju.destroy_model(model, destroy_storage=True, force=True)
