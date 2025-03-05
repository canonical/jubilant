import dataclasses
from typing import cast

_MAX_VALUE = 150
_INDENT = 2
_SIMPLE_TYPES = (type(None), bool, int, float, str)


def _dump(value: object, indent: str = '') -> str:
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
            v_str = _dump(v, sub_indent)
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
        value = cast(list[object], value)
        is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value)
        if is_simple:
            single_line = repr(value)
            if len(single_line) <= _MAX_VALUE:
                return single_line

        items = [_dump(v, sub_indent) for v in value]
        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'[\n{lines_str}\n{indent}]'

    elif isinstance(value, dict):
        value = cast(dict[str, object], value)
        is_simple = all(isinstance(v, _SIMPLE_TYPES) for v in value.values())
        if is_simple:
            single_line = repr(value)
            if len(single_line) <= _MAX_VALUE:
                return single_line

        items = [f'{k!r}: {_dump(v, sub_indent)}' for k, v in sorted(value.items())]
        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'{{\n{lines_str}\n{indent}}}'

    else:
        return repr(value)
