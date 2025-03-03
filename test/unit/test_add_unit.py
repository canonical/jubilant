import jubilant

from . import mocks


def test_defaults(run: mocks.Run):
    run.handle(['juju', 'add-unit', 'app1'])
    juju = jubilant.Juju()

    juju.add_unit('app1')


def test_defaults_with_model(run: mocks.Run):
    run.handle(['juju', 'add-unit', '--model', 'mdl', 'app1'])
    juju = jubilant.Juju(model='mdl')

    juju.add_unit('app1')


def test_all_args(run: mocks.Run):
    run.handle(
        [
            'juju',
            'add-unit',
            'app2',
            '--attach-storage',
            'stg',
            '--num-units',
            '3',
            '--to',
            'lxd:25',
        ]
    )
    juju = jubilant.Juju()

    juju.add_unit('app2', attach_storage='stg', num_units=3, to='lxd:25')


def test_list_args(run: mocks.Run):
    run.handle(['juju', 'add-unit', 'app1', '--attach-storage', 'stg1,stg2', '--to', 'to1,to2'])
    juju = jubilant.Juju()

    juju.add_unit('app1', attach_storage=['stg1', 'stg2'], to=['to1', 'to2'])
