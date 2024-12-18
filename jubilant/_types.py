import dataclasses


@dataclasses.dataclass
class StatusInfoContents:
    current: str | None = None
    message: str | None = None

    @classmethod
    def from_dict(cls, d):
        self = cls()
        self.current = d.get('current')
        self.message = d.get('message')
        return self


@dataclasses.dataclass
class UnitStatus:
    workload_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)

    @classmethod
    def from_dict(cls, d):
        self = cls()
        self.workload_status = StatusInfoContents.from_dict(d.get('workload-status') or {})
        return self

    @property
    def is_active(self) -> bool:
        """Report whether the workload status for this unit status is "active"."""
        return self.workload_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the workload status for this unit status is "blocked"."""
        return self.workload_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the workload status for this unit status is "error"."""
        return self.workload_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the workload status for this unit status is "maintenance"."""
        return self.workload_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the workload status for this unit status is "waiting"."""
        return self.workload_status.current == 'waiting'


@dataclasses.dataclass
class ApplicationStatus:
    app_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    units: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, d):
        self = cls()
        self.app_status = StatusInfoContents.from_dict(d.get('application-status') or {})
        return self

    @property
    def is_active(self) -> bool:
        """Report whether the application status for this app is "active"."""
        return self.app_status.current == 'active'

    @property
    def is_blocked(self) -> bool:
        """Report whether the application status for this app is "blocked"."""
        return self.app_status.current == 'blocked'

    @property
    def is_error(self) -> bool:
        """Report whether the application status for this app is "error"."""
        return self.app_status.current == 'error'

    @property
    def is_maintenance(self) -> bool:
        """Report whether the application status for this app is "maintenance"."""
        return self.app_status.current == 'maintenance'

    @property
    def is_waiting(self) -> bool:
        """Report whether the application status for this app is "waiting"."""
        return self.app_status.current == 'waiting'


@dataclasses.dataclass
class Status:
    # TODO: Ideally we can generate the list of fields from the Go source in Juju:
    # cmd/juju/status/formatted.go
    apps: dict[str, ApplicationStatus] = dataclasses.field(default_factory=dict)

    @classmethod
    def from_dict(cls, d):
        self = cls()
        apps = d.get('applications') or {}
        self.apps = {name: ApplicationStatus.from_dict(status) for name, status in apps.items()}
        return self

    # TODO: add a nice succinct __str__, similar to "juju status" text output
