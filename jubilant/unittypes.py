"""Dataclasses that contain parsed output from ``juju show-unit --format=json``."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class UnitRelationData:
    in_scope: bool = False
    data: dict[str, Any] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitRelationData:
        return cls(
            in_scope=d.get('in-scope') or False,
            data=d.get('data') or {},
        )


@dataclasses.dataclass(frozen=True)
class UnitRelationInfo:
    endpoint: str = ''
    relation_id: int = 0
    related_endpoint: str = ''
    cross_model: bool = False
    application_data: dict[str, Any] = dataclasses.field(default_factory=dict)  # type: ignore
    local_unit: UnitRelationData = dataclasses.field(default_factory=UnitRelationData)
    related_units: dict[str, UnitRelationData] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitRelationInfo:
        return cls(
            endpoint=d.get('endpoint') or '',
            relation_id=d.get('relation-id') or 0,
            related_endpoint=d.get('related-endpoint') or '',
            cross_model=d.get('cross-model') or False,
            application_data=d.get('application-data') or {},
            local_unit=(
                UnitRelationData._from_dict(d['local-unit'])
                if 'local-unit' in d
                else UnitRelationData()
            ),
            related_units={
                k: UnitRelationData._from_dict(v) for k, v in d.get('related-units', {}).items()
            },
        )


@dataclasses.dataclass(frozen=True)
class UnitInfo:
    """Parsed version of the object returned by ``juju show-unit --format=json``."""

    workload_version: str = ''
    machine: str = ''
    relation_info: list[UnitRelationInfo] = dataclasses.field(default_factory=list)  # type: ignore
    opened_ports: list[str] = dataclasses.field(default_factory=list)  # type: ignore
    public_address: str = ''
    charm: str = ''
    leader: bool = False
    life: str = ''
    provider_id: str = ''
    address: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitInfo:
        return cls(
            workload_version=d.get('workload-version') or '',
            machine=d.get('machine') or '',
            relation_info=[UnitRelationInfo._from_dict(x) for x in d.get('relation-info', [])],
            opened_ports=d.get('opened-ports') or [],
            public_address=d.get('public-address') or '',
            charm=d.get('charm') or '',
            leader=d.get('leader') or False,
            life=d.get('life') or '',
            provider_id=d.get('provider-id') or '',
            address=d.get('address') or '',
        )
