"""Jubilant is a Pythonic wrapper around the Juju CLI for integration testing."""

from . import types
from ._errors import CLIError, WaitError
from ._helpers import (
    all_active,
    all_blocked,
    all_error,
    all_maintenance,
    all_waiting,
    any_active,
    any_blocked,
    any_error,
    any_maintenance,
    any_waiting,
)
from ._juju import Juju
from .types import Status

__all__ = [
    'CLIError',
    'Juju',
    'Status',
    'WaitError',
    'all_active',
    'all_blocked',
    'all_error',
    'all_maintenance',
    'all_waiting',
    'any_active',
    'any_blocked',
    'any_error',
    'any_maintenance',
    'any_waiting',
    'types',
]

__version__ = '0.0.0a1'
