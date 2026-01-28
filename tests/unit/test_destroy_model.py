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


def test_destroy_with_destroy_storage(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'xyz', '--no-prompt', '--destroy-storage'])
    juju = jubilant.Juju()

    juju.destroy_model('xyz', destroy_storage=True)

    assert juju.model is None


def test_destroy_with_force(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'xyz', '--no-prompt', '--force'])
    juju = jubilant.Juju()

    juju.destroy_model('xyz', force=True)

    assert juju.model is None


def test_destroy_with_no_wait(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'xyz', '--no-prompt', '--no-wait'])
    juju = jubilant.Juju()

    juju.destroy_model('xyz', no_wait=True)

    assert juju.model is None


def test_destroy_with_release_storage(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'xyz', '--no-prompt', '--release-storage'])
    juju = jubilant.Juju()

    juju.destroy_model('xyz', release_storage=True)

    assert juju.model is None


def test_destroy_with_timeout(run: mocks.Run):
    run.handle(['juju', 'destroy-model', 'xyz', '--no-prompt', '--force', '--timeout', '120s'])
    juju = jubilant.Juju()

    juju.destroy_model('xyz', force=True, timeout=120)

    assert juju.model is None
