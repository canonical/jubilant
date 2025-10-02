import dataclasses
from typing import Union

import pytest

import jubilant
import jubilant as real_jubilant
from jubilant import statustypes

from . import mocks
from .fake_statuses import (
    MINIMAL_JSON,
    MINIMAL_JSON29,
    MINIMAL_STATUS,
    MINIMAL_STATUS29,
    SNAPPASS_JSON,
    SNAPPASS_JSON29,
)


@pytest.mark.parametrize(
    'version,input_status,output_status',
    [
        pytest.param('2.9.52', MINIMAL_JSON, MINIMAL_STATUS, id='cli2-ctl3'),
        pytest.param('3.6.8', MINIMAL_JSON29, MINIMAL_STATUS29, id='cli3-ctl2.9'),
        pytest.param('3.6.8', MINIMAL_JSON, MINIMAL_STATUS, id='cli3-ctl3'),
        pytest.param('2.9.52', MINIMAL_JSON29, MINIMAL_STATUS29, id='cli2-ctl2.9'),
    ],
)
def test_minimal(
    version: str,
    input_status: str,
    output_status: Union[real_jubilant.Status, jubilant.Status],
    run: mocks.Run,
):
    run.handle(['juju', 'status', '--format', 'json'], stdout=input_status)
    juju = jubilant.Juju(cli_version=version)

    status = juju.status()

    assert status == output_status


@pytest.mark.parametrize(
    'input_status,output_status',
    [
        pytest.param(MINIMAL_JSON, MINIMAL_STATUS, id='3'),
        pytest.param(MINIMAL_JSON29, MINIMAL_STATUS29, id='2.9'),
    ],
)
def test_minimal_with_model(
    input_status: str, output_status: Union[real_jubilant.Status, jubilant.Status], run: mocks.Run
):
    run.handle(['juju', 'status', '--model', 'mdl', '--format', 'json'], stdout=input_status)
    juju = jubilant.Juju(model='mdl', cli_version='2.9.52')

    status = juju.status()

    assert status == output_status


@pytest.mark.parametrize(
    'version,input_status',
    [
        pytest.param('2.9.52', SNAPPASS_JSON, id='cli2-ctl3'),
        pytest.param('3.6.8', SNAPPASS_JSON29, id='cli3-ctl2.9'),
        pytest.param('3.6.8', SNAPPASS_JSON, id='cli3-ctl3'),
        pytest.param('2.9.52', SNAPPASS_JSON29, id='cli2-ctl2.9'),
    ],
)
def test_real_status(version: str, input_status: str, run: mocks.Run):
    run.handle(['juju', 'status', '--format', 'json'], stdout=input_status)
    juju = jubilant.Juju(cli_version=version)

    status = juju.status()

    assert status.model.type == 'caas'
    assert status.apps['snappass-test'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].is_active
    assert status.apps['snappass-test'].units['snappass-test/0'].leader


@pytest.mark.parametrize(
    'input_status',
    [pytest.param(MINIMAL_STATUS, id='3'), pytest.param(MINIMAL_STATUS29, id='2.9')],
)
def test_status_eq(input_status: Union[jubilant.Status, real_jubilant.Status]):
    # Status.__eq__ should ignore "controller" attribute with its ever-changing timestamp.
    status1 = dataclasses.replace(
        input_status, controller=statustypes.ControllerStatus(timestamp='foo')
    )
    status1b = dataclasses.replace(
        input_status, controller=statustypes.ControllerStatus(timestamp='foo')
    )
    status2 = dataclasses.replace(
        input_status, controller=statustypes.ControllerStatus(timestamp='bar')
    )
    assert status1 == status1b
    assert status1 == status2
