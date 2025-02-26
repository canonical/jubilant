"""Dataclasses used to hold parsed output from "juju status --format=json"."""

from __future__ import annotations

import dataclasses
from typing import Any

__all__ = [
    'AppStatus',
    'AppStatusRelation',
    'CombinedStorage',
    'ControllerStatus',
    'EntityStatus',
    'FilesystemAttachment',
    'FilesystemAttachments',
    'FilesystemInfo',
    'FormattedBase',
    'LxdProfileContents',
    'MachineStatus',
    'ModelStatus',
    'NetworkInterface',
    'OfferStatus',
    'RemoteAppStatus',
    'RemoteEndpoint',
    'Status',
    'StatusError',
    'StatusInfoContents',
    'StorageAttachments',
    'StorageInfo',
    'UnitStatus',
    'UnitStorageAttachment',
    'VolumeAttachment',
    'VolumeAttachments',
    'VolumeInfo',
]


class StatusError(Exception):
    """Raised when "juju status" returns a status-error for certain types."""


@dataclasses.dataclass(frozen=True, kw_only=True)
class FormattedBase:
    name: str
    channel: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FormattedBase:
        return cls(
            name=d['name'],
            channel=d['channel'],
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StatusInfoContents:
    current: str = ''
    message: str = ''
    reason: str = ''
    since: str = ''
    version: str = ''
    life: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StatusInfoContents:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            current=d.get('current') or '',
            message=d.get('message') or '',
            reason=d.get('reason') or '',
            since=d.get('since') or '',
            version=d.get('version') or '',
            life=d.get('life') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class AppStatusRelation:
    related_app: str = ''
    interface: str = ''
    scope: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AppStatusRelation:
        return cls(
            related_app=d.get('related-application') or '',
            interface=d.get('interface') or '',
            scope=d.get('scope') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitStatus:
    workload_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    juju_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    leader: bool = False
    upgrading_from: str = ''
    machine: str = ''
    open_ports: list[str] = dataclasses.field(default_factory=list)
    public_address: str = ''
    address: str = ''
    provider_id: str = ''
    subordinates: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitStatus:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            workload_status=(
                StatusInfoContents._from_dict(d['workload-status'])
                if 'workload-status' in d
                else StatusInfoContents()
            ),
            juju_status=(
                StatusInfoContents._from_dict(d['juju-status'])
                if 'juju-status' in d
                else StatusInfoContents()
            ),
            leader=d.get('leader') or False,
            upgrading_from=d.get('upgrading-from') or '',
            machine=d.get('machine') or '',
            open_ports=d.get('open-ports') or [],
            public_address=d.get('public-address') or '',
            address=d.get('address') or '',
            provider_id=d.get('provider-id') or '',
            subordinates=(
                {k: UnitStatus._from_dict(v) for k, v in d['subordinates'].items()}
                if 'subordinates' in d
                else {}
            ),
        )

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


@dataclasses.dataclass(frozen=True, kw_only=True)
class AppStatus:
    charm: str
    charm_origin: str
    charm_name: str
    charm_rev: int
    exposed: bool

    base: FormattedBase | None = None
    charm_channel: str = ''
    charm_version: str = ''
    charm_profile: str = ''
    can_upgrade_to: str = ''
    scale: int = 0
    provider_id: str = ''
    address: str = ''
    life: str = ''
    app_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    relations: dict[str, list[AppStatusRelation]] = dataclasses.field(default_factory=dict)
    subordinate_to: list[str] = dataclasses.field(default_factory=list)
    units: dict[str, UnitStatus] = dataclasses.field(default_factory=dict)
    version: str = ''
    endpoint_bindings: dict[str, str] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> AppStatus:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            charm=d['charm'],
            charm_origin=d['charm-origin'],
            charm_name=d['charm-name'],
            charm_rev=d['charm-rev'],
            exposed=d['exposed'],
            base=FormattedBase._from_dict(d['base']) if 'base' in d else None,
            charm_channel=d.get('charm-channel') or '',
            charm_version=d.get('charm-version') or '',
            charm_profile=d.get('charm-profile') or '',
            can_upgrade_to=d.get('can-upgrade-to') or '',
            scale=d.get('scale') or 0,
            provider_id=d.get('provider-id') or '',
            address=d.get('address') or '',
            life=d.get('life') or '',
            app_status=(
                StatusInfoContents._from_dict(d['application-status'])
                if 'application-status' in d
                else StatusInfoContents()
            ),
            relations=(
                {
                    k: [AppStatusRelation._from_dict(x) for x in v]
                    for k, v in d['relations'].items()
                }
                if 'relations' in d
                else {}
            ),
            subordinate_to=d.get('subordinate-to') or [],
            units=(
                {k: UnitStatus._from_dict(v) for k, v in d['units'].items()}
                if 'units' in d
                else {}
            ),
            version=d.get('version') or '',
            endpoint_bindings=d.get('endpoint-bindings') or {},
        )

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


@dataclasses.dataclass(frozen=True, kw_only=True)
class EntityStatus:
    current: str = ''
    message: str = ''
    since: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> EntityStatus:
        return cls(
            current=d.get('current') or '',
            message=d.get('message') or '',
            since=d.get('since') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class UnitStorageAttachment:
    machine: str = ''
    location: str = ''
    life: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitStorageAttachment:
        return cls(
            machine=d.get('machine') or '',
            location=d.get('location') or '',
            life=d.get('life') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StorageAttachments:
    units: dict[str, UnitStorageAttachment]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StorageAttachments:
        return cls(
            units={k: UnitStorageAttachment._from_dict(v) for k, v in d['units'].items()},
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class StorageInfo:
    kind: str
    status: EntityStatus
    persistent: bool

    life: str = ''
    attachments: StorageAttachments | None = None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> StorageInfo:
        return cls(
            kind=d['kind'],
            status=EntityStatus._from_dict(d['status']),
            persistent=d['persistent'],
            life=d.get('life') or '',
            attachments=(
                StorageAttachments._from_dict(d['attachments']) if 'attachments' in d else None
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class FilesystemAttachment:
    mount_point: str
    read_only: bool

    life: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FilesystemAttachment:
        return cls(
            mount_point=d['mount-point'],
            read_only=d['read-only'],
            life=d.get('life') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class FilesystemAttachments:
    machines: dict[str, FilesystemAttachment] = dataclasses.field(default_factory=dict)
    containers: dict[str, FilesystemAttachment] = dataclasses.field(default_factory=dict)
    units: dict[str, UnitStorageAttachment] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FilesystemAttachments:
        return cls(
            machines=(
                {k: FilesystemAttachment._from_dict(v) for k, v in d['machines'].items()}
                if 'machines' in d
                else {}
            ),
            containers=(
                {k: FilesystemAttachment._from_dict(v) for k, v in d['containers'].items()}
                if 'containers' in d
                else {}
            ),
            units=(
                {k: UnitStorageAttachment._from_dict(v) for k, v in d['units'].items()}
                if 'units' in d
                else {}
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class FilesystemInfo:
    size: int

    provider_id: str = ''
    volume: str = ''
    storage: str = ''
    attachments: FilesystemAttachments = dataclasses.field(default_factory=FilesystemAttachments)
    pool: str = ''
    life: str = ''
    status: EntityStatus = dataclasses.field(default_factory=EntityStatus)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> FilesystemInfo:
        return cls(
            size=d['size'],
            provider_id=d.get('provider-id') or '',
            volume=d.get('volume') or '',
            storage=d.get('storage') or '',
            attachments=(
                FilesystemAttachments._from_dict(d['attachments'])
                if 'attachments' in d
                else FilesystemAttachments()
            ),
            pool=d.get('pool') or '',
            life=d.get('life') or '',
            status=EntityStatus._from_dict(d['status']) if 'status' in d else EntityStatus(),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class VolumeAttachment:
    read_only: bool

    device: str = ''
    device_link: str = ''
    bus_address: str = ''
    life: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VolumeAttachment:
        return cls(
            read_only=d['read-only'],
            device=d.get('device') or '',
            device_link=d.get('device-link') or '',
            bus_address=d.get('bus-address') or '',
            life=d.get('life') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class VolumeAttachments:
    machines: dict[str, VolumeAttachment] = dataclasses.field(default_factory=dict)
    containers: dict[str, VolumeAttachment] = dataclasses.field(default_factory=dict)
    units: dict[str, UnitStorageAttachment] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VolumeAttachments:
        return cls(
            machines=(
                {k: VolumeAttachment._from_dict(v) for k, v in d['machines'].items()}
                if 'machines' in d
                else {}
            ),
            containers=(
                {k: VolumeAttachment._from_dict(v) for k, v in d['containers'].items()}
                if 'containers' in d
                else {}
            ),
            units=(
                {k: UnitStorageAttachment._from_dict(v) for k, v in d['units'].items()}
                if 'units' in d
                else {}
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class VolumeInfo:
    size: int
    persistent: bool

    provider_id: str = ''
    storage: str = ''
    attachments: VolumeAttachments = dataclasses.field(default_factory=VolumeAttachments)
    pool: str = ''
    hardware_id: str = ''
    wwn: str = ''
    life: str = ''
    status: EntityStatus = dataclasses.field(default_factory=EntityStatus)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> VolumeInfo:
        return cls(
            size=d['size'],
            persistent=d['persistent'],
            provider_id=d.get('provider-id') or '',
            storage=d.get('storage') or '',
            attachments=(
                VolumeAttachments._from_dict(d['attachments'])
                if 'attachments' in d
                else VolumeAttachments()
            ),
            pool=d.get('pool') or '',
            hardware_id=d.get('hardware-id') or '',
            wwn=d.get('wwn') or '',
            life=d.get('life') or '',
            status=EntityStatus._from_dict(d['status']) if 'status' in d else EntityStatus(),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class CombinedStorage:
    storage: dict[str, StorageInfo] = dataclasses.field(default_factory=dict)
    filesystems: dict[str, FilesystemInfo] = dataclasses.field(default_factory=dict)
    volumes: dict[str, VolumeInfo] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> CombinedStorage:
        return cls(
            storage=(
                {k: StorageInfo._from_dict(v) for k, v in d['storage'].items()}
                if 'storage' in d
                else {}
            ),
            filesystems=(
                {k: FilesystemInfo._from_dict(v) for k, v in d['filesystems'].items()}
                if 'filesystems' in d
                else {}
            ),
            volumes=(
                {k: VolumeInfo._from_dict(v) for k, v in d['volumes'].items()}
                if 'volumes' in d
                else {}
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ControllerStatus:
    timestamp: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ControllerStatus:
        return cls(
            timestamp=d.get('timestamp') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LxdProfileContents:
    config: dict[str, str]
    description: str
    devices: dict[str, dict[str, str]]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> LxdProfileContents:
        return cls(
            config=d['config'],
            description=d['description'],
            devices=d['devices'],
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class NetworkInterface:
    ip_addresses: list[str]
    mac_address: str
    is_up: bool

    gateway: str = ''
    dns_nameservers: list[str] = dataclasses.field(default_factory=list)
    space: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> NetworkInterface:
        return cls(
            ip_addresses=d['ip-addresses'],
            mac_address=d['mac-address'],
            is_up=d['is-up'],
            gateway=d.get('gateway') or '',
            dns_nameservers=d.get('dns-nameservers') or [],
            space=d.get('space') or '',
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class MachineStatus:
    juju_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    hostname: str = ''
    dns_name: str = ''
    ip_addresses: list[str] = dataclasses.field(default_factory=list)
    instance_id: str = ''
    display_name: str = ''
    machine_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    modification_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    base: FormattedBase | None = None
    network_interfaces: dict[str, NetworkInterface] = dataclasses.field(default_factory=dict)
    containers: dict[str, MachineStatus] = dataclasses.field(default_factory=dict)
    constraints: str = ''
    hardware: str = ''
    controller_member_status: str = ''
    ha_primary: bool = False
    lxd_profiles: dict[str, LxdProfileContents] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> MachineStatus:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            juju_status=(
                StatusInfoContents._from_dict(d['juju-status'])
                if 'juju-status' in d
                else StatusInfoContents()
            ),
            hostname=d.get('hostname') or '',
            dns_name=d.get('dns-name') or '',
            ip_addresses=d.get('ip-addresses') or [],
            instance_id=d.get('instance-id') or '',
            display_name=d.get('display-name') or '',
            machine_status=(
                StatusInfoContents._from_dict(d['machine-status'])
                if 'machine-status' in d
                else StatusInfoContents()
            ),
            modification_status=(
                StatusInfoContents._from_dict(d['modification-status'])
                if 'modification-status' in d
                else StatusInfoContents()
            ),
            base=FormattedBase._from_dict(d['base']) if 'base' in d else None,
            network_interfaces=(
                {k: NetworkInterface._from_dict(v) for k, v in d['network-interfaces'].items()}
                if 'network-interfaces' in d
                else {}
            ),
            containers=(
                {k: MachineStatus._from_dict(v) for k, v in d['containers'].items()}
                if 'containers' in d
                else {}
            ),
            constraints=d.get('constraints') or '',
            hardware=d.get('hardware') or '',
            controller_member_status=d.get('controller-member-status') or '',
            ha_primary=d.get('ha-primary') or False,
            lxd_profiles=(
                {k: LxdProfileContents._from_dict(v) for k, v in d['lxd-profiles'].items()}
                if 'lxd-profiles' in d
                else {}
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class ModelStatus:
    name: str
    type: str
    controller: str
    cloud: str
    version: str

    region: str = ''
    upgrade_available: str = ''
    model_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelStatus:
        return cls(
            name=d['name'],
            type=d['type'],
            controller=d['controller'],
            cloud=d['cloud'],
            version=d['version'],
            region=d.get('region') or '',
            upgrade_available=d.get('upgrade-available') or '',
            model_status=(
                StatusInfoContents._from_dict(d['model-status'])
                if 'model-status' in d
                else StatusInfoContents()
            ),
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RemoteEndpoint:
    interface: str
    role: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RemoteEndpoint:
        return cls(
            interface=d['interface'],
            role=d['role'],
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class OfferStatus:
    app: str
    endpoints: dict[str, RemoteEndpoint]

    charm: str = ''
    total_connected_count: int = 0
    active_connected_count: int = 0

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> OfferStatus:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            app=d['application'],
            endpoints={k: RemoteEndpoint._from_dict(v) for k, v in d['endpoints'].items()},
            charm=d.get('charm') or '',
            total_connected_count=d.get('total-connected-count') or 0,
            active_connected_count=d.get('active-connected-count') or 0,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class RemoteAppStatus:
    url: str

    endpoints: dict[str, RemoteEndpoint] = dataclasses.field(default_factory=dict)
    life: str = ''
    app_status: StatusInfoContents = dataclasses.field(default_factory=StatusInfoContents)
    relations: dict[str, list[str]] = dataclasses.field(default_factory=dict)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RemoteAppStatus:
        if 'status-error' in d:
            raise StatusError(d['status-error'])
        return cls(
            url=d['url'],
            endpoints=(
                {k: RemoteEndpoint._from_dict(v) for k, v in d['endpoints'].items()}
                if 'endpoints' in d
                else {}
            ),
            life=d.get('life') or '',
            app_status=(
                StatusInfoContents._from_dict(d['application-status'])
                if 'application-status' in d
                else StatusInfoContents()
            ),
            relations=d.get('relations') or {},
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class Status:
    """Parsed version of the status object returned by "juju status --format=json"."""

    model: ModelStatus
    machines: dict[str, MachineStatus]
    apps: dict[str, AppStatus]

    app_endpoints: dict[str, RemoteAppStatus] = dataclasses.field(default_factory=dict)
    offers: dict[str, OfferStatus] = dataclasses.field(default_factory=dict)
    storage: CombinedStorage = dataclasses.field(default_factory=CombinedStorage)
    controller: ControllerStatus = dataclasses.field(default_factory=ControllerStatus)

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Status:
        return cls(
            model=ModelStatus._from_dict(d['model']),
            machines={k: MachineStatus._from_dict(v) for k, v in d['machines'].items()},
            apps={k: AppStatus._from_dict(v) for k, v in d['applications'].items()},
            app_endpoints=(
                {k: RemoteAppStatus._from_dict(v) for k, v in d['application-endpoints'].items()}
                if 'application-endpoints' in d
                else {}
            ),
            offers=(
                {k: OfferStatus._from_dict(v) for k, v in d['offers'].items()}
                if 'offers' in d
                else {}
            ),
            storage=(
                CombinedStorage._from_dict(d['storage']) if 'storage' in d else CombinedStorage()
            ),
            controller=(
                ControllerStatus._from_dict(d['controller'])
                if 'controller' in d
                else ControllerStatus()
            ),
        )

    def __repr__(self):
        return _dump_dataclass(self)


def _dump_dataclass(dc: Any, indent='') -> str:
    lines = []
    sub_indent = indent + '    '
    for field in dataclasses.fields(dc):
        value = getattr(dc, field.name)
        if field.default is not dataclasses.MISSING and value == field.default:
            continue
        if field.default_factory is not dataclasses.MISSING and value == field.default_factory():
            continue
        value_str = _dump_value(value, sub_indent)
        lines.append(f'{sub_indent}{field.name}={value_str},')
    if not lines:
        return f'{dc.__class__.__name__}()'
    lines_str = '\n'.join(lines)
    return f'{dc.__class__.__name__}(\n{lines_str}{indent}\n{indent})'


def _dump_value(value: Any, indent='') -> str:
    if dataclasses.is_dataclass(value):
        return _dump_dataclass(value, indent)
    elif isinstance(value, dict):
        if not value:
            return '{}'
        sub_indent = indent + '    '
        lines = []
        for k, v in sorted(value.items()):
            v_str = _dump_value(v, sub_indent)
            lines.append(f'{sub_indent}{k!r}: {v_str},')
        return f'{{\n' + '\n'.join(lines) + f'\n{indent}}}'
    else:
        return repr(value)
