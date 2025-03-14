#!/usr/bin/env python3
"""Test app ("db" consumer) charm for Jubilant integration tests"""

import ops


class Charm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.framework.observe(self.on['db'].relation_changed, self._on_db_relation_changed)

    def _on_db_relation_changed(self, event: ops.RelationChangedEvent):
        if 'dbkey' not in event.relation.data[event.app]:
            self.unit.status = ops.BlockedStatus('dbkey not found')
            return
        dbkey = event.relation.data[event.app]['dbkey']
        self.unit.status = ops.ActiveStatus(f'relation changed: dbkey={dbkey}')


if __name__ == '__main__':
    ops.main(Charm)
