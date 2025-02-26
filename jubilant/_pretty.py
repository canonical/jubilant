import dataclasses

_MAX_VALUE = 150
_INDENT = 2


def _dump(value: object, indent='') -> str:
    """Pretty-print a value with special cases for dataclasses, lists, and dicts.

    If the value fits on a single (long) line, use that. Otherwise, split onto
    multiple lines and indent each line.

    For dataclasses, omit fields that are set to their default (or
    default_factory return value).
    """
    sub_indent = indent + ' ' * _INDENT

    if dataclasses.is_dataclass(value):
        fields = []
        for field in dataclasses.fields(value):
            v = getattr(value, field.name)
            if field.default is not dataclasses.MISSING and v == field.default:
                continue
            if field.default_factory is not dataclasses.MISSING and v == field.default_factory():
                continue
            v_str = _dump(v, sub_indent)
            fields.append(f'{field.name}={v_str}')

        class_name = value.__class__.__name__  # type: ignore
        single_line = f'{class_name}({", ".join(fields)})'
        if len(indent) + len(single_line) <= _MAX_VALUE:
            return single_line

        lines_str = '\n'.join(sub_indent + f + ',' for f in fields)
        return f'{class_name}(\n{lines_str}\n{indent})'

    elif isinstance(value, list):
        items = [_dump(v, sub_indent) for v in value]

        single_line = '[' + ', '.join(items) + ']'
        if len(indent) + len(single_line) <= _MAX_VALUE:
            return single_line

        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'[\n{lines_str}\n{indent}]'

    elif isinstance(value, dict):
        items = [f'{k!r}: {_dump(v, sub_indent)}' for k, v in sorted(value.items())]

        single_line = '{' + ', '.join(items) + '}'
        if len(indent) + len(single_line) <= _MAX_VALUE:
            return single_line

        lines_str = '\n'.join(sub_indent + item + ',' for item in items)
        return f'{{\n{lines_str}\n{indent}}}'

    else:
        return repr(value)
