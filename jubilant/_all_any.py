from __future__ import annotations

from collections.abc import Iterable

from .statustypes import Status


def all_active(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "active".

    Examples::

        # Use the callable directly to wait for all apps in status to be active.
        juju.wait(jubilant.all_active)

        # Use a lambda to wait for all apps specified (blog, mysql) to be active.
        juju.wait(lambda status: jubilant.all_active(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('active', status, apps)


def all_blocked(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "blocked".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('blocked', status, apps)


def all_error(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "error".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('error', status, apps)


def all_maintenance(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "maintenance".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('maintenance', status, apps)


def all_waiting(status: Status, *apps: str) -> bool:
    """Report whether all apps and units in *status* (or in *apps* if provided) are "waiting".

    See :func:`all_active` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested. If an app is not
            present in ``status.apps``, returns False.
    """
    return _all_statuses_are('waiting', status, apps)


def any_active(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "active".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('active', status, apps)


def any_blocked(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "blocked".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('blocked', status, apps)


def any_error(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "error".

    Examples::

        # Use the callable directly to raise an error if any apps go into error.
        juju.wait(jubilant.all_active, error=jubilant.any_error)

        # Use a lambda to wait for any of the apps specified (blog, mysql) to go into error.
        juju.wait(
            jubilant.all_active,
            error=lambda status: jubilant.any_error(status, 'blog', 'mysql')),
        )

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('error', status, apps)


def any_maintenance(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "maintenance".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('maintenance', status, apps)


def any_waiting(status: Status, *apps: str) -> bool:
    """Report whether any app or unit in *status* (or in *apps* if provided) is "waiting".

    See :func:`any_error` for examples.

    Args:
        status: The status object being tested.
        apps: If provided, only these applications (and their units) are tested.
    """
    return _any_status_is('waiting', status, apps)


def all_agents_idle(status: Status, *apps: str) -> bool:
    """Report whether all unit agents in *status* (filtered to *apps* if provided) are "idle".

    Unlike the other ``all_*`` and ``any_*`` helpers, this method looks at the status of each
    Juju unit agent, not the workload's application or unit status.

    Examples::

        # Use the callable directly to wait for unit agents from all apps to be idle.
        juju.wait(jubilant.all_agents_idle)

        # Use a lambda to wait for unit agents only from specified apps (blog, mysql).
        juju.wait(lambda status: jubilant.all_agents_idle(status, 'blog', 'mysql'))

    Args:
        status: The status object being tested.
        apps: If provided, only the unit agents of units from these applications are tested.
            If an app is not present in ``status.apps``, returns False.
    """
    return _all_agent_statuses_are('idle', status, apps)


def _all_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            return False
        if app_info.app_status.current != expected:
            return False
        for unit_info in app_info.units.values():
            if unit_info.workload_status.current != expected:
                return False
    return True


def _any_status_is(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            continue
        if app_info.app_status.current == expected:
            return True
        for unit_info in app_info.units.values():
            if unit_info.workload_status.current == expected:
                return True
    return False


def _all_agent_statuses_are(expected: str, status: Status, apps: Iterable[str]) -> bool:
    if not apps:
        apps = status.apps

    for app in apps:
        app_info = status.apps.get(app)
        if app_info is None:
            return False
        for unit_info in app_info.units.values():
            if unit_info.juju_status.current != expected:
                return False
    return True
