"""Dataclasses that contain parsed output from ``juju show-model --format=json``.

These dataclasses were originally `generated from <https://github.com/juju/juju/compare/main...benhoyt:juju:modelinfo-dataclasses-4>`_
the Go structs in the Juju codebase, to ensure they are correct. Class names
come from the Go struct name, whereas attribute names come from the JSON field
names.
"""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class ModelCredential:
    name: str
    owner: str
    cloud: str

    validity_check: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelCredential:
        return cls(
            name=d['name'],
            owner=d['owner'],
            cloud=d['cloud'],
            validity_check=d.get('validity-check') or '',
        )


@dataclasses.dataclass(frozen=True)
class ModelStatusInfo:
    current: str = ''
    message: str = ''
    reason: str = ''
    since: str = ''
    migration: str = ''
    migration_start: str = ''
    migration_end: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelStatusInfo:
        return cls(
            current=d.get('current') or '',
            message=d.get('message') or '',
            reason=d.get('reason') or '',
            since=d.get('since') or '',
            migration=d.get('migration') or '',
            migration_start=d.get('migration-start') or '',
            migration_end=d.get('migration-end') or '',
        )


@dataclasses.dataclass(frozen=True)
class ModelUserInfo:
    access: str
    last_connection: str

    display_name: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelUserInfo:
        return cls(
            access=d['access'],
            last_connection=d['last-connection'],
            display_name=d.get('display-name') or '',
        )


@dataclasses.dataclass(frozen=True)
class ModelMachineInfo:
    cores: int

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelMachineInfo:
        return cls(
            cores=d['cores'],
        )


@dataclasses.dataclass(frozen=True)
class SecretBackendInfo:
    num_secrets: int
    status: str

    message: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SecretBackendInfo:
        return cls(
            num_secrets=d['num-secrets'],
            status=d['status'],
            message=d.get('message') or '',
        )


@dataclasses.dataclass(frozen=True)
class SupportedFeature:
    name: str
    description: str

    version: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SupportedFeature:
        return cls(
            name=d['name'],
            description=d['description'],
            version=d.get('version') or '',
        )


@dataclasses.dataclass(frozen=True)
class ModelInfo:
    """Parsed version of the object returned by ``juju show-model --format=json``."""

    name: str
    short_name: str
    model_uuid: str
    model_type: str
    controller_uuid: str
    controller_name: str
    is_controller: bool
    cloud: str
    life: str

    region: str = ''
    type: str = ''
    status: ModelStatusInfo = dataclasses.field(default_factory=ModelStatusInfo)
    users: dict[str, ModelUserInfo] = dataclasses.field(default_factory=dict)  # type: ignore
    machines: dict[str, ModelMachineInfo] = dataclasses.field(default_factory=dict)  # type: ignore
    secret_backends: dict[str, SecretBackendInfo] = dataclasses.field(default_factory=dict)  # type: ignore
    agent_version: str = ''
    credential: ModelCredential | None = None
    supported_features: list[SupportedFeature] = dataclasses.field(default_factory=list)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> ModelInfo:
        return cls(
            name=d['name'],
            short_name=d['short-name'],
            model_uuid=d['model-uuid'],
            model_type=d['model-type'],
            controller_uuid=d['controller-uuid'],
            controller_name=d['controller-name'],
            is_controller=d['is-controller'],
            cloud=d['cloud'],
            life=d['life'],
            region=d.get('region') or '',
            type=d.get('type') or '',
            status=ModelStatusInfo._from_dict(d['status']) if 'status' in d else ModelStatusInfo(),
            users=(
                {k: ModelUserInfo._from_dict(v) for k, v in d['users'].items()}
                if 'users' in d
                else {}
            ),
            machines=(
                {k: ModelMachineInfo._from_dict(v) for k, v in d['machines'].items()}
                if 'machines' in d
                else {}
            ),
            secret_backends=(
                {k: SecretBackendInfo._from_dict(v) for k, v in d['secret-backends'].items()}
                if 'secret-backends' in d
                else {}
            ),
            agent_version=d.get('agent-version') or '',
            credential=ModelCredential._from_dict(d['credential']) if 'credential' in d else None,
            supported_features=(
                [SupportedFeature._from_dict(x) for x in d['supported-features']]
                if 'supported-features' in d
                else []
            ),
        )
