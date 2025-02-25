from __future__ import annotations

from collections.abc import Callable

from . import statustypes


def _status_str(self: statustypes.Status) -> str:
    # Implementation of Status.__str__ is here to avoid it having to be in the
    # generated code. The parameter name is "self" as it would be if defined
    # in Status.__str__ directly.

    writes = []

    notes = ''
    if self.model.model_status.message:
        notes = self.model.model_status.message
    elif self.model.upgrade_available:
        notes = f'upgrade available: {self.model.upgrade_available}'
    _format_rows(
        writes.append,
        [
            ['Model', 'Controller', 'Cloud/Region', 'Version', 'Timestamp', 'Notes'],
            [
                self.model.name,
                self.model.controller,
                self.model.cloud + ('/' + self.model.region if self.model.region else ''),
                self.model.version,
                self.controller.timestamp,
                notes,
            ],
        ],
    )

    # TODO: need remote applications / app_endpoints

    app_rows = [
        [
            'App',
            'Version',
            'Status',
            'Scale',
            'Charm',
            'Channel',
            'Rev',
            'Address',
            'Exposed',
            'Message',
        ]
    ]
    unit_rows = [
        [
            'Unit',
            'Workload',
            'Agent',
            'Machine',
            'Address' if self.model.type == 'caas' else 'Public address',
            'Ports',
            'Message',
        ],
    ]
    relation_rows = [
        ['Integration provider', 'Requirer', 'Interface', 'Type', 'Message'],
    ]
    for app_name, app in sorted(self.apps.items()):
        app_rows.append(
            [
                app_name,
                app.version.split('\n', maxsplit=1)[0],
                app.app_status.current,
                str(app.scale),  # TODO: only for CAAS, see formattedStatus.applicationScale
                app.charm_name,
                app.charm_channel,
                str(app.charm_rev),
                app.address,
                'yes' if app.exposed else 'no',
                app.app_status.message,
            ]
        )
        for unit_name, unit in sorted(app.units.items()):
            unit_rows.append(
                [
                    unit_name + '*' if unit.leader else unit_name,
                    unit.workload_status.current,
                    unit.juju_status.current,
                    '' if self.model.type == 'caas' else unit.machine,
                    unit.address if self.model.type == 'caas' else unit.public_address,
                    ','.join(unit.open_ports),  # TODO: not like Juju
                    unit.juju_status.message,  # TODO: not quite correct, see Juju
                ]
            )

    machine_rows = [['Machine', 'State', 'Address', 'Inst id', 'Base', 'AZ', 'Message']]
    if self.model.type != 'caas' and self.machines:
        for name, machine in sorted(self.machines.items()):
            status = machine.juju_status.current
            message = machine.machine_status.message
            if machine.modification_status.current == 'error':
                status = machine.modification_status.current
                message = machine.modification_status.message
            machine_rows.append(
                [
                    name,
                    status,
                    machine.dns_name,
                    machine.display_name or machine.instance_id,
                    machine.base.name + '@' + machine.base.channel if machine.base else '',
                    'TODO:az',
                    message,
                ]
            )

    if len(app_rows) > 1:
        writes.append('\n')
        _format_rows(writes.append, app_rows)
    if len(unit_rows) > 1:
        writes.append('\n')
        _format_rows(writes.append, unit_rows)
    if len(machine_rows) > 1:
        writes.append('\n')
        _format_rows(writes.append, machine_rows)
    if len(relation_rows) > 1:
        writes.append('\n')
        _format_rows(writes.append, relation_rows)

    return ''.join(writes)


def _format_rows(write: Callable, rows: list[list[str]]):
    widths = [0] * len(rows[0])
    for col in range(len(rows[0])):
        widths[col] = max(len(row[col]) for row in rows)
    for row in rows:
        for col, value in enumerate(row):
            padding = 2 if col < len(row) - 1 else 0
            write(value.ljust(widths[col] + padding))
        write('\n')
