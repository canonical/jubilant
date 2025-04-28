from __future__ import annotations

import dataclasses
import difflib
from collections.abc import Generator, Sequence
from typing import cast

_MAX_VALUE = 150
_INDENT = 2
_SIMPLE_TYPES = (type(None), bool, int, float, str)


def dump(value: object, indent: str = '') -> str:
    """Pretty-print a value with special cases for dataclasses, lists, and dicts.

    If *value*'s fields or sub-values are simple scalar types and the result fits in a limited
    number of characters, use a single-line format. Otherwise, split onto multiple lines and
    indent each line.

    For dataclasses, omit fields that are set to their default (or default_factory return value).
    """
    sub_indent = indent + ' ' * _INDENT

    if dataclasses.is_dataclass(value):
        fields: list[str] = []
        is_simple = True
        for field in dataclasses.fields(value):
            v = getattr(value, field.name)
            if field.default is not dataclasses.MISSING and v == field.default:
                continue
            if field.default_factory is not dataclasses.MISSING and v == field.default_factory():
                continue
            v_str = dump(v, sub_indent)
            fields.append(f'{field.name}={v_str}')
            is_simple = is_simple and isinstance(v, _SIMPLE_TYPES)

        class_name = value.__class__.__name__  # type: ignore
        if is_simple:
            # If one of the dumped fields above has been split onto multiple lines due to it
            # exceeding _MAX_VALUE, this will definitely not fit in _MAX_VALUE.
            single_line = f'{class_name}({", ".join(fields)})'
            if len(single_line) <= _MAX_VALUE:
                return single_line

        lines_str = '\n'.join(sub_indent + f + ',' for f in fields)
        return f'{class_name}(\n{lines_str}\n{indent})'

    elif isinstance(value, list):
        value = cast('list[object]', value)
        is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value)
        if is_simple:
            single_line = repr(value)
            if len(single_line) <= _MAX_VALUE:
                return single_line

        items = [dump(v, sub_indent) for v in value]
        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'[\n{lines_str}\n{indent}]'

    elif isinstance(value, dict):
        value = cast('dict[str, object]', value)
        is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value.values())
        if is_simple:
            single_line = repr(value)
            if len(single_line) <= _MAX_VALUE:
                return single_line

        items = [f'{k!r}: {dump(v, sub_indent)}' for k, v in sorted(value.items())]
        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'{{\n{lines_str}\n{indent}}}'

    else:
        return repr(value)


def gron(value: object, prefix: str = '') -> Generator[str]:
    """Yield gron-style lines of all fields within value, recursively.

    This handles dataclasses, lists, and dicts. It's inspired by gron:
    https://github.com/tomnomnom/gron

    Example output for a :class:`Status` instance with ``prefix='status'`` (some lines omitted
    for brevity)::

        status.model.name = 'tt'
        status.model.controller = 'microk8s-localhost'
        status.model.version = '3.6.1'
        status.apps['database'].charm = 'local:database-0'
        status.apps['database'].charm_rev = 0
        status.apps['database'].base.name = 'ubuntu'
        status.apps['database'].base.channel = '22.04'
        status.apps['database'].app_status.current = 'active'
        status.apps['database'].app_status.message = 'relation-created: added new secret'
        status.apps['database'].app_status.since = '24 Feb 2025 16:59:43+13:00'
        status.apps['database'].relations['db'][0].related_app = 'webapp'
        status.apps['database'].relations['db'][0].interface = 'dbi'
        status.apps['database'].relations['db'][0].scope = 'global'
        ...
    """
    if dataclasses.is_dataclass(value):
        for field in dataclasses.fields(value):
            v = getattr(value, field.name)
            if field.default is not dataclasses.MISSING and v == field.default:
                continue
            if field.default_factory is not dataclasses.MISSING and v == field.default_factory():
                continue
            yield from gron(v, f'{prefix}.{field.name}')

    elif isinstance(value, list):
        value = cast('list[object]', value)
        for i, v in enumerate(value):
            yield from gron(v, f'{prefix}[{i}]')

    elif isinstance(value, dict):
        value = cast('dict[str, object]', value)
        for k, v in sorted(value.items()):
            yield from gron(v, f'{prefix}[{k!r}]')

    else:
        yield f'{prefix} = {value!r}'


def diff(seq1: Sequence[str], seq2: Sequence[str]) -> Generator[str]:
    """Compare seq1 and seq1; yield lines that have been removed, changed, or added.

    Example::

        - .apps['database'].app_status.current = 'active'
        + .apps['database'].app_status.current = 'waiting'
        - .apps['database'].relations['db'][0].scope = 'global'
        - .apps['database'].relations['db'][1].related_app = 'dummy'
        - .apps['database'].relations['db'][1].interface = 'xyz'
        - .apps['database'].relations['db'][1].scope = 'foobar'
        + .apps['database'].relations['db'][0].scope = 'testy'
    """
    matcher = difflib.SequenceMatcher(None, seq1, seq2)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {'replace', 'delete'}:
            for line in seq1[i1:i2]:
                yield '- ' + line
        if tag in {'replace', 'insert'}:
            for line in seq2[j1:j2]:
                yield '+ ' + line
