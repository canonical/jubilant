from __future__ import annotations

from typing import Any, Protocol, TypeVar, overload

import yaml

# These types were taken from typeshed:
# https://github.com/python/typeshed/blob/e6165eadd680f45b00e37ba9342b5073bc884132/stubs/PyYAML/yaml/__init__.pyi
_T_co = TypeVar('_T_co', covariant=True)


class SupportsRead(Protocol[_T_co]):
    def read(self, length: int = ..., /) -> _T_co: ...


type _ReadStream = str | bytes | SupportsRead[str] | SupportsRead[bytes]

_T_contra = TypeVar('_T_contra', str, bytes, contravariant=True)


class _WriteStream(Protocol[_T_contra]):
    def write(self, data: _T_contra, /) -> object: ...


# Use C speedups if available.
_safe_loader = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)
_safe_dumper = getattr(yaml, 'CSafeDumper', yaml.SafeDumper)


def safe_load(stream: _ReadStream) -> Any:
    """Same as yaml.safe_load, but use fast C loader if available."""
    return yaml.load(stream, Loader=_safe_loader)  # noqa: S506


@overload
def safe_dump(data: Any, stream: _WriteStream[Any]) -> None: ...


@overload
def safe_dump(data: Any, stream: None = None) -> str: ...


def safe_dump(data: Any, stream: _WriteStream[Any] | None = None) -> str | None:
    """Same as yaml.safe_dump, but use fast C dumper if available."""
    return yaml.dump(data, stream=stream, Dumper=_safe_dumper)
