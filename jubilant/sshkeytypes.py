"""Dataclasses that contain parsed output from juju ssh-keys."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass(frozen=True)
class SSHKey:
    """Represents an SSH key in the model."""

    fingerprint: str
    """The fingerprint of the SSH key."""

    comment: str
    """The comment or label of the SSH key."""

    key: str | None = None
    """The full SSH public key (only present when --full is used)."""

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> SSHKey:
        return SSHKey(
            fingerprint=d['fingerprint'],
            comment=d['comment'],
            key=d.get('key'),
        )
