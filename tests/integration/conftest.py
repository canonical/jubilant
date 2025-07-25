from __future__ import annotations

from typing import Generator, cast

import pytest

import jubilant


def pytest_addoption(parser: pytest.OptionGroup):
    parser.addoption(
        '--keep-models',
        action='store_true',
        default=False,
        help='keep temporarily-created models',
    )


@pytest.fixture(scope='module')
def juju(request: pytest.FixtureRequest) -> Generator[jubilant.Juju]:
    """Module-scoped pytest fixture that creates a temporary model."""
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    with jubilant.temp_model(keep=keep_models) as juju:
        yield juju
        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end='')


@pytest.fixture(scope='module')
def model2(request: pytest.FixtureRequest) -> Generator[jubilant.Juju]:
    """Module-scoped pytest fixture that creates a (second) temporary model."""
    keep_models = cast(bool, request.config.getoption('--keep-models'))
    with jubilant.temp_model(keep=keep_models) as juju:
        yield juju
