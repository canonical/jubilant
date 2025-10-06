import jubilant

from . import mocks


def test_destroy_this(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'initial', '--no-prompt'])
    juju = jubilant.Juju(model='initial')

    juju.destroy_model('initial')

    assert juju.model is None


def test_destroy_other(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'other', '--no-prompt'])
    juju = jubilant.Juju(model='initial')

    juju.destroy_model('other')

    assert juju.model == 'initial'


def test_args(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'bad', '--no-prompt', '--destroy-storage', '--force'])
    juju = jubilant.Juju()

    juju.destroy_model('bad', destroy_storage=True, force=True)

    assert juju.model is None
