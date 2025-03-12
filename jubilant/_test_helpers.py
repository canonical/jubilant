import contextlib
import secrets
from collections.abc import Generator

from ._juju import Juju


@contextlib.contextmanager
def with_model(model: str | None = None, keep: bool = False) -> Generator[Juju, None, None]:
    """Context manager to create a model for running tests in (or use an existing one).

    Provides a :class:`Juju` instance to operate on.

    If *model* is not provided, create a new model with a random name in the format
    ``jubilant-abcd1234``, and destroy it and its storage when the context manager exits.

    Args:
        model: If set, operate in this existing model, and don't destroy it when the context
            manager exits (in other words, implies *keep=True*).
        keep: If true (and *model* is not set), keep the created model around instead of
            destroying it when the context manager exits.
    """
    juju = Juju(model=model)

    model_added = False
    if model is None:
        model = 'jubilant-' + secrets.token_hex(4)  # 4 bytes (8 hex digits) should be plenty
        juju.add_model(model)
        model_added = True

    try:
        yield juju
    finally:
        if model_added and not keep:
            juju.destroy_model(model, destroy_storage=True, force=True)
