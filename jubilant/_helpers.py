from ._types import Status


def any_error(status: Status) -> bool:
    """Return true if any application or unit in *status* is in "error" status."""
    for app_info in status.applications.values():
        if app_info.application_status.current == 'error':
            return True
        for unit_info in app_info.units.values():
            if unit_info.workload_status.current == 'error':
                return True
        # TODO: what about juju_status (agent status)?
    return False


def any_blocked(status: Status) -> bool:
    """Return true if any application or unit in *status* is in "blocked" status."""
    return False  # TODO
