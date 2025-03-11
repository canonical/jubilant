from collections.abc import Generator
from typing import cast

import pytest

import jubilant

# TODO ben: need to improve logging; just log all subprocess.run args?


def pytest_addoption(parser: pytest.OptionGroup):
    parser.addoption(
        '--model',
        help='existing model to use for tests (default is to create a randomly-named one per test)',
    )
    parser.addoption(
        '--keep-models',
        action='store_true',
        default=False,
        help='keep created models (implied if --model is specified)',
    )


@pytest.fixture
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju, None, None]:
    """Pytest fixture that wraps :meth:`jubilant.with_model`.

    This adds command line parameters ``--model`` and ``--keep-models`` (see help for details).
    """
    model = cast(str | None, request.config.getoption('--model'))
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    with jubilant.with_model(model, keep=keep_models) as juju:
        yield juju
