from collections.abc import Iterable

from ._types import Status


def all_active(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether all applications or units in *status* are in "active" status.

    Args:
        status: The :class:`Status` object being tested.
        apps: An optional list of application names. If provided, only these applications
            (and their units) are tested.
    """
    return _all_statuses_are('active', status, apps)


def all_error(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether all applications or units in *status* are in "error" status.

    TODO: Args
    """
    return _any_status_is('error', status, apps)


def all_blocked(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether all applications or units in *status* are in "blocked" status.

    TODO: Args
    """
    return _any_status_is('blocked', status, apps)


def all_maintenance(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether all applications or units in *status* are in "maintenance" status.

    TODO: Args
    """
    return _any_status_is('maintenance', status, apps)


def all_waiting(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether all applications or units in *status* are in "waiting" status.

    TODO: Args
    """
    return _any_status_is('waiting', status, apps)


def any_active(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether any application or unit in *status* is in "active" status.

    Args:
        status: The :class:`Status` object being tested.
        apps: An optional list of application names. If provided, only these applications
            (and their units) are tested.
    """
    return _any_status_is('active', status, apps)


def any_error(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether any application or unit in *status* is in "error" status.

    TODO: Args
    """
    return _any_status_is('error', status, apps)


def any_blocked(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether any application or unit in *status* is in "blocked" status.

    TODO: Args
    """
    return _any_status_is('blocked', status, apps)


def any_maintenance(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether any application or unit in *status* is in "maintenance" status.

    TODO: Args
    """
    return _any_status_is('maintenance', status, apps)


def any_waiting(status: Status, apps: Iterable[str] | None = None) -> bool:
    """Report whether any application or unit in *status* is in "waiting" status.

    TODO: Args
    """
    return _any_status_is('waiting', status, apps)


def _all_statuses_are(expected: str, status: Status, apps: Iterable[str] | None) -> bool:
    if apps is None:
        apps = list(status.applications.keys())
    for app in apps:
        app_info = status.applications.get(app)
        if app_info is None:
            return False
        if app_info.application_status.current != expected:
            return False
        for unit_info in app_info.units.values():
            if unit_info.workload_status.current != expected:
                return False
    return True


def _any_status_is(expected: str, status: Status, apps: Iterable[str] | None) -> bool:
    if apps is None:
        apps = list(status.applications.keys())
    for app in apps:
        app_info = status.applications.get(app)
        if app_info is None:
            continue
        if app_info.application_status.current == expected:
            return True
        for unit_info in app_info.units.values():
            if unit_info.workload_status.current == expected:
                return True
        # TODO: what about juju_status (agent status)?
    return False
