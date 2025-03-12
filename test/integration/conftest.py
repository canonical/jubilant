from collections.abc import Generator
from typing import cast

import pytest

import jubilant


def pytest_addoption(parser: pytest.OptionGroup):
    parser.addoption(
        '--model',
        help='existing model to use for tests (default is to create a randomly-named one per test)',
    )
    parser.addoption(
        '--keep-models',
        action='store_true',
        default=False,
        help='keep temporarily-created models',
    )


@pytest.fixture
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps :meth:`jubilant.with_model`.

    This adds command line parameters ``--model`` and ``--keep-models`` (see help for details).
    """
    model = cast(str | None, request.config.getoption('--model'))
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    if model:
        yield jubilant.Juju(model=model)
    else:
        with jubilant.temp_model(keep=keep_models) as juju:
            yield juju
