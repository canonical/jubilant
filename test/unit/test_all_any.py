import copy
import json
from typing import Any

import pytest

import jubilant

from .fake_statuses import MINIMAL_STATUS, SNAPPASS_JSON


@pytest.mark.parametrize(
    'all_func',
    [
        jubilant.all_active,
        jubilant.all_blocked,
        jubilant.all_error,
        jubilant.all_maintenance,
        jubilant.all_waiting,
    ],
)
def test_all_no_apps(all_func: Any):
    # Just like Python's all(), all_* helpers return True if no apps
    assert all_func(MINIMAL_STATUS)
    assert all_func(MINIMAL_STATUS, [])


@pytest.mark.parametrize(
    'any_func',
    [
        jubilant.any_active,
        jubilant.any_blocked,
        jubilant.any_error,
        jubilant.any_maintenance,
        jubilant.any_waiting,
    ],
)
def test_any_no_apps(any_func: Any):
    # Just like Python's any(), any_* helpers return False if no apps
    assert not any_func(MINIMAL_STATUS)
    assert not any_func(MINIMAL_STATUS, [])


@pytest.mark.parametrize(
    'all_func,expected,unexpected',
    [
        (jubilant.all_active, 'active', 'error'),
        (jubilant.all_blocked, 'blocked', 'error'),
        (jubilant.all_error, 'error', 'active'),
        (jubilant.all_maintenance, 'maintenance', 'error'),
        (jubilant.all_waiting, 'waiting', 'error'),
    ],
)
def test_all_one_app(all_func: Any, expected: str, unexpected: str):
    status_dict = json.loads(SNAPPASS_JSON)
    set_app_and_unit_status(status_dict, 'snappass-test', expected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert all_func(status)
    assert all_func(status, ['snappass-test'])
    assert not all_func(status, ['other'])
    assert not all_func(status, ['snappass-test', 'other'])

    # Should return False if app status is not the expected status
    set_app_and_unit_status(status_dict, 'snappass-test', unexpected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)

    # Should return False if one of the unit's statuses is not the expected status
    set_app_and_unit_status(status_dict, 'snappass-test', expected, unexpected)
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)


@pytest.mark.parametrize(
    'any_func,expected,unexpected',
    [
        (jubilant.any_active, 'active', 'error'),
        (jubilant.any_blocked, 'blocked', 'error'),
        (jubilant.any_error, 'error', 'active'),
        (jubilant.any_maintenance, 'maintenance', 'error'),
        (jubilant.any_waiting, 'waiting', 'error'),
    ],
)
def test_any_one_app(any_func: Any, expected: str, unexpected: str):
    status_dict = json.loads(SNAPPASS_JSON)
    set_app_and_unit_status(status_dict, 'snappass-test', expected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)
    assert any_func(status, ['snappass-test'])
    assert not any_func(status, ['other'])
    assert any_func(status, ['snappass-test', 'other'])

    # Should return True if app status is not the expected status but unit status is
    set_app_and_unit_status(status_dict, 'snappass-test', unexpected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)

    # Should return True if app status is expected but one of the unit's statuses is not
    set_app_and_unit_status(status_dict, 'snappass-test', expected, unexpected)
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)


@pytest.mark.parametrize(
    'all_func,expected,unexpected',
    [
        (jubilant.all_active, 'active', 'error'),
        (jubilant.all_blocked, 'blocked', 'error'),
        (jubilant.all_error, 'error', 'active'),
        (jubilant.all_maintenance, 'maintenance', 'error'),
        (jubilant.all_waiting, 'waiting', 'error'),
    ],
)
def test_all_two_apps(all_func: Any, expected: str, unexpected: str):
    status_dict = json.loads(SNAPPASS_JSON)
    set_app_and_unit_status(status_dict, 'snappass-test', expected, expected)
    add_app(status_dict, 'snappass-test', 'app2')
    status = jubilant.Status._from_dict(status_dict)
    assert all_func(status)
    assert all_func(status, ['snappass-test'])
    assert all_func(status, ['snappass-test', 'app2'])
    assert not all_func(status, ['snappass-test', 'other'])
    assert not all_func(status, ['snappass-test', 'app2', 'other'])
    assert not all_func(status, ['other1', 'other2'])

    # Should return False if one app is the expected status but the other is not
    set_app_and_unit_status(status_dict, 'snappass-test', unexpected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)

    # Should return False if neither app has the expected status
    set_app_and_unit_status(status_dict, 'app2', unexpected, expected)
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)


@pytest.mark.parametrize(
    'any_func,expected,unexpected',
    [
        (jubilant.any_active, 'active', 'error'),
        (jubilant.any_blocked, 'blocked', 'error'),
        (jubilant.any_error, 'error', 'active'),
        (jubilant.any_maintenance, 'maintenance', 'error'),
        (jubilant.any_waiting, 'waiting', 'error'),
    ],
)
def test_any_two_apps(any_func: Any, expected: str, unexpected: str):
    status_dict = json.loads(SNAPPASS_JSON)
    set_app_and_unit_status(status_dict, 'snappass-test', expected, expected)
    add_app(status_dict, 'snappass-test', 'app2')
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)
    assert any_func(status, ['snappass-test'])
    assert any_func(status, ['snappass-test', 'app2'])
    assert any_func(status, ['snappass-test', 'other'])
    assert any_func(status, ['snappass-test', 'app2', 'other'])
    assert not any_func(status, ['other1', 'other2'])

    # Should return True if one app is the expected status but the other is not
    set_app_and_unit_status(status_dict, 'snappass-test', unexpected, unexpected)
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)

    # Should return False if neither app has the expected status
    set_app_and_unit_status(status_dict, 'app2', unexpected, unexpected)
    status = jubilant.Status._from_dict(status_dict)
    assert not any_func(status)


@pytest.mark.parametrize(
    'func',
    [
        jubilant.all_active,
        jubilant.all_blocked,
        jubilant.all_error,
        jubilant.all_maintenance,
        jubilant.all_waiting,
        jubilant.any_active,
        jubilant.any_blocked,
        jubilant.any_error,
        jubilant.any_maintenance,
        jubilant.any_waiting,
    ],
)
def test_all_and_any_type_errors(func: Any):
    with pytest.raises(TypeError):
        func(MINIMAL_STATUS, apps='app')
    with pytest.raises(TypeError):
        func(MINIMAL_STATUS, apps=b'app')


def set_app_and_unit_status(
    status_dict: dict[str, Any], app: str, app_status: str, unit_status: str, *, unit: int = 0
):
    """Set a status dict's app and unit status."""
    status_dict['applications'][app]['application-status']['current'] = app_status
    status_dict['applications'][app]['units'][f'{app}/{unit}']['workload-status']['current'] = (
        unit_status
    )


def add_app(status_dict: dict[str, Any], src_app: str, dest_app: str):
    """Add a new app named dest_app (with one unit) to status dict, based on src_app."""
    app = status_dict['applications'][src_app]
    unit = status_dict['applications'][src_app]['units'][f'{src_app}/0']
    status_dict['applications'][dest_app] = copy.deepcopy(app)
    status_dict['applications'][dest_app]['units'] = {f'{dest_app}/0': copy.deepcopy(unit)}
