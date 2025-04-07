import pytest

import jubilant

from . import mocks


def test_single(run: mocks.Run):
    run.handle(['juju', 'remove-unit', '--no-prompt', 'unit/0'])
    juju = jubilant.Juju()

    juju.remove_unit('unit/0')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'remove-unit', '--model', 'mdl', '--no-prompt', 'unit/0'])
    juju = jubilant.Juju(model='mdl')

    juju.remove_unit('unit/0')


def test_num_units(run: mocks.Run):
    run.handle(['juju', 'remove-unit', '--no-prompt', 'wordpress', '--num-units', '2'])
    juju = jubilant.Juju()

    juju.remove_unit('wordpress', num_units=2)


def test_force_and_destroy(run: mocks.Run):
    run.handle(['juju', 'remove-unit', '--no-prompt', 'unit/0', '--destroy-storage', '--force'])
    juju = jubilant.Juju()

    juju.remove_unit('unit/0', destroy_storage=True, force=True)


def test_multiple(run: mocks.Run):
    run.handle(['juju', 'remove-unit', '--no-prompt', 'unit/0', 'unit/1', 'unit/2'])
    juju = jubilant.Juju()

    juju.remove_unit('unit/0', 'unit/1', 'unit/2')


def test_two_units_error():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.remove_unit('unit/0', 'unit/1', num_units=2)


def test_three_units_error():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.remove_unit('unit/0', 'unit/1', 'unit/2', num_units=3)
