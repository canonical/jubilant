"""Jubilant is a Pythonic wrapper around the Juju CLI for integration testing."""

from . import statustypes
from ._all_any import (
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
from ._juju import CLIError, ConfigValue, Juju, SecretURI, WaitError
from .statustypes import Status

__all__ = [
    'CLIError',
    'ConfigValue',
    'Juju',
    'SecretURI',
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
    'statustypes',
]

__version__ = '0.0.0a1'
