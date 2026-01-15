"""Dataclasses that contain parsed output from juju secrets."""

from __future__ import annotations

import dataclasses
import datetime
from typing import Any


class SecretURI(str):
    """A string subclass that represents a secret URI ("secret:...")."""

    def __repr__(self):
        """Override to make the type obvious in error messages."""
        return f'SecretURI({super().__repr__()})'

    @property
    def unique_identifier(self) -> str:
        """Unique identifier of this secret URI.

        This is the secret's globally-unique identifier (currently a 20-character Xid,
        for example "9m4e2mr0ui3e8a215n4g").
        """
        if '/' in self:
            # Handle 'secret://MODEL-UUID/UNIQUE-IDENTIFIER'
            return self.rsplit('/', maxsplit=1)[-1]
        elif self.startswith('secret:'):
            # Handle common case of 'secret:UNIQUE-IDENTIFIER'
            return self[len('secret:') :]
        else:
            return str(self)


@dataclasses.dataclass(frozen=True)
class Secret:
    """Represents a secret."""

    uri: SecretURI
    revision: int
    owner: str
    created: datetime.datetime
    updated: datetime.datetime
    expires: str | None
    rotation: str | None
    rotates: datetime.datetime | None
    name: str | None
    label: str | None
    description: str | None
    access: list[Access] | None
    revisions: list[Revision] | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Secret:
        return Secret(
            uri=SecretURI('secret:' + d['uri']),
            revision=d['revision'],
            owner=d['owner'],
            created=_datetime_from_iso(d['created']),
            updated=_datetime_from_iso(d['updated']),
            expires=d.get('expires'),
            rotation=d.get('rotation'),
            rotates=_datetime_from_iso(d['rotates']) if 'rotates' in d else None,
            name=d.get('name'),
            label=d.get('label'),
            description=d.get('description'),
            access=[Access._from_dict(access) for access in d.get('access', [])] or None,
            revisions=[Revision._from_dict(revision) for revision in d.get('revisions', [])]
            or None,
        )


@dataclasses.dataclass(frozen=True)
class RevealedSecret(Secret):
    """Represents a secret that was revealed, which has a content field that's populated."""

    checksum: str
    """Checksum of the secret value or an empty string for Juju controllers < 3.6.0."""

    content: dict[str, str]
    """Mapping of secret keys to secret values."""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RevealedSecret:
        kwargs = dataclasses.asdict(super()._from_dict(d))
        return RevealedSecret(
            # Secret content checksums were introduced in Juju 3.6.0
            content=d['content']['Data'],
            checksum=d.get('checksum', ''),
            **kwargs,
        )


@dataclasses.dataclass(frozen=True)
class Revision:
    """Represents a revision of a secret."""

    revision: int
    backend: str
    created: datetime.datetime
    updated: datetime.datetime
    expires: datetime.datetime | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Revision:
        return cls(
            revision=d['revision'],
            backend=d.get('backend', ''),
            created=_datetime_from_iso(d['created']),
            updated=_datetime_from_iso(d['updated']),
            expires=_datetime_from_iso(d['expires']) if 'expires' in d else None,
        )


@dataclasses.dataclass(frozen=True)
class Access:
    """Represents access to a secret."""

    target: str
    scope: str
    role: str

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Access:
        return cls(target=d['target'], scope=d['scope'], role=d['role'])


def _datetime_from_iso(dt: str) -> datetime.datetime:
    """Converts a Juju-specific ISO 8601 string to a datetime object."""
    return datetime.datetime.fromisoformat(dt.replace('Z', '+00:00'))
