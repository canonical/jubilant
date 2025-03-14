#!/usr/bin/env python3
"""Test "db" provider charm for Jubilant integration tests."""

import ops


class Charm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on['db'].relation_created, self._on_db_relation_created)
        self.framework.observe(self.on.do_thing_action, self._do_thing)

    def _on_start(self, _: ops.StartEvent):
        self.unit.status = ops.BlockedStatus('waiting for relation')

    def _do_thing(self, event: ops.ActionEvent):
        event.set_results({'thingy': 'foo', 'params': event.params, 'config': dict(self.config)})

    def _on_db_relation_created(self, event: ops.RelationCreatedEvent):
        event.relation.data[self.app]['dbkey'] = 'dbvalue'
        self.unit.status = ops.ActiveStatus('relation created')


if __name__ == '__main__':
    ops.main(Charm)
