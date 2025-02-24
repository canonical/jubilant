import copy
import json
from collections.abc import Callable

import pytest
from test_status import MINIMAL_STATUS, SNAPPASS_JSON

import jubilant


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
def test_all_no_apps(all_func: Callable):
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
def test_any_no_apps(any_func: Callable):
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
def test_all_one_app(all_func: Callable, expected: str, unexpected: str):
    status_dict = copy.deepcopy(json.loads(SNAPPASS_JSON))
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert all_func(status)
    assert all_func(status, ['snappass-test'])
    assert not all_func(status, ['other'])
    assert not all_func(status, ['snappass-test', 'other'])

    # Should return False if app status is not the expected status
    status_dict['applications']['snappass-test']['application-status']['current'] = unexpected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)

    # Should return False if one of the unit's statuses is not the expected status
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = unexpected
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
def test_any_one_app(any_func: Callable, expected: str, unexpected: str):
    status_dict = copy.deepcopy(json.loads(SNAPPASS_JSON))
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)
    assert any_func(status, ['snappass-test'])
    assert not any_func(status, ['other'])
    assert any_func(status, ['snappass-test', 'other'])

    # Should return True if app status is not the expected status but unit status is
    status_dict['applications']['snappass-test']['application-status']['current'] = unexpected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)

    # Should return True if app status is expected but one of the unit's statuses is not
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = unexpected
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
def test_all_two_apps(all_func: Callable, expected: str, unexpected: str):
    status_dict = copy.deepcopy(json.loads(SNAPPASS_JSON))
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    # Add another app named "app2" unit one unit named "app2/0"
    status_dict['applications']['app2'] = copy.deepcopy(
        status_dict['applications']['snappass-test']
    )
    status_dict['applications']['app2']['units']['app2/0'] = status_dict['applications']['app2'][
        'units'
    ]['snappass-test/0']
    del status_dict['applications']['app2']['units']['snappass-test/0']
    status_dict['applications']['app2']['application-status']['current'] = expected
    status_dict['applications']['app2']['units']['app2/0']['workload-status']['current'] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert all_func(status)
    assert all_func(status, ['snappass-test'])
    assert all_func(status, ['snappass-test', 'app2'])
    assert not all_func(status, ['snappass-test', 'other'])
    assert not all_func(status, ['snappass-test', 'app2', 'other'])
    assert not all_func(status, ['other1', 'other2'])

    # Should return False if one app is the expected status but the other is not
    status_dict['applications']['snappass-test']['application-status']['current'] = unexpected
    status = jubilant.Status._from_dict(status_dict)
    assert not all_func(status)

    # Should return False if neither app has the expected status
    status_dict['applications']['app2']['application-status']['current'] = unexpected
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
def test_any_two_apps(any_func: Callable, expected: str, unexpected: str):
    status_dict = copy.deepcopy(json.loads(SNAPPASS_JSON))
    status_dict['applications']['snappass-test']['application-status']['current'] = expected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = expected
    # Add another app named "app2" unit one unit named "app2/0"
    status_dict['applications']['app2'] = copy.deepcopy(
        status_dict['applications']['snappass-test']
    )
    status_dict['applications']['app2']['units']['app2/0'] = status_dict['applications']['app2'][
        'units'
    ]['snappass-test/0']
    del status_dict['applications']['app2']['units']['snappass-test/0']
    status_dict['applications']['app2']['application-status']['current'] = expected
    status_dict['applications']['app2']['units']['app2/0']['workload-status']['current'] = expected
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)
    assert any_func(status, ['snappass-test'])
    assert any_func(status, ['snappass-test', 'app2'])
    assert any_func(status, ['snappass-test', 'other'])
    assert any_func(status, ['snappass-test', 'app2', 'other'])
    assert not any_func(status, ['other1', 'other2'])

    # Should return True if one app is the expected status but the other is not
    status_dict['applications']['snappass-test']['application-status']['current'] = unexpected
    status_dict['applications']['snappass-test']['units']['snappass-test/0']['workload-status'][
        'current'
    ] = unexpected
    status = jubilant.Status._from_dict(status_dict)
    assert any_func(status)

    # Should return False if neither app has the expected status
    status_dict['applications']['app2']['application-status']['current'] = unexpected
    status_dict['applications']['app2']['units']['app2/0']['workload-status']['current'] = (
        unexpected
    )
    status = jubilant.Status._from_dict(status_dict)
    assert not any_func(status)


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
def test_all_type_errors(all_func: Callable):
    with pytest.raises(TypeError):
        all_func(None, 'app')
    with pytest.raises(TypeError):
        all_func(None, b'app')


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
def test_any_type_errors(any_func: Callable):
    with pytest.raises(TypeError):
        any_func(None, 'app')
    with pytest.raises(TypeError):
        any_func(None, b'app')
