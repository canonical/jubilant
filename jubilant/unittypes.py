"""Dataclasses that contain parsed output from ``juju show-unit --format=json``."""

# These dataclasses were originally generated from the Go structs in the Juju codebase.
# See the comment at the top of statustypes.py for details (but use the
# "unittypes-dataclasses" branch).

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class UnitRelationData:
    in_scope: bool
    data: dict[str, Any]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitRelationData:
        return cls(
            in_scope=d['in-scope'],
            data=d['data'],
        )


@dataclasses.dataclass(frozen=True)
class RelationData:
    relation_id: int
    endpoint: str
    related_endpoint: str
    app_data: dict[str, Any]

    cross_model: bool = False
    local_unit: UnitRelationData | None = None
    related_units: dict[str, UnitRelationData] = dataclasses.field(default_factory=dict)  # type: ignore

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RelationData:
        return cls(
            relation_id=d['relation-id'],
            endpoint=d['endpoint'],
            cross_model=d.get('cross-model') or False,
            related_endpoint=d['related-endpoint'],
            app_data=d['application-data'],
            local_unit=UnitRelationData._from_dict(d['local-unit']) if 'local-unit' in d else None,
            related_units={
                k: UnitRelationData._from_dict(v) for k, v in d.get('related-units', {}).items()
            },
        )


@dataclasses.dataclass(frozen=True)
class UnitInfo:
    opened_ports: list[str]
    charm: str
    leader: bool

    workload_version: str = ''
    machine: str = ''
    public_address: str = ''
    life: str = ''
    relation_info: list[RelationData] = dataclasses.field(default_factory=list)  # type: ignore
    provider_id: str = ''
    address: str = ''

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> UnitInfo:
        return cls(
            workload_version=d.get('workload-version') or '',
            machine=d.get('machine') or '',
            opened_ports=d['opened-ports'],
            public_address=d.get('public-address') or '',
            charm=d['charm'],
            leader=d['leader'],
            life=d.get('life') or '',
            relation_info=[RelationData._from_dict(x) for x in d.get('relation-info', [])],
            provider_id=d.get('provider-id') or '',
            address=d.get('address') or '',
        )
