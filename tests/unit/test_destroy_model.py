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


def test_destroy_user_qualified(run: mocks.Run):
    """destroy_model('alice/other') resets self.model when self.model == 'alice/other'."""
    run.handle(['juju', 'destroy-model', 'alice/other', '--no-prompt'])
    juju = jubilant.Juju(model='alice/other')

    juju.destroy_model('alice/other')

    assert juju.model is None


def test_destroy_qualified_matches_unqualified_self(run: mocks.Run):
    """destroy_model('admin/m') resets self.model when self.model == 'm'."""
    run.handle(['juju', 'destroy-model', 'admin/m', '--no-prompt'])
    juju = jubilant.Juju(model='m')

    juju.destroy_model('admin/m')

    assert juju.model is None


def test_destroy_unqualified_matches_qualified_self(run: mocks.Run):
    """destroy_model('m') resets self.model when self.model == 'admin/m'."""
    run.handle(['juju', 'destroy-model', 'm', '--no-prompt'])
    juju = jubilant.Juju(model='admin/m')

    juju.destroy_model('m')

    assert juju.model is None


def test_destroy_controller_qualified(run: mocks.Run):
    """destroy_model('c1:m') resets self.model when self.model == 'c1:m'."""
    run.handle(['juju', 'destroy-model', 'c1:m', '--no-prompt'])
    juju = jubilant.Juju(model='c1:m')

    juju.destroy_model('c1:m')

    assert juju.model is None


def test_destroy_controller_qualified_matches_unqualified_self(run: mocks.Run):
    """destroy_model('c1:m') resets self.model when self.model == 'm'."""
    run.handle(['juju', 'destroy-model', 'c1:m', '--no-prompt'])
    juju = jubilant.Juju(model='m')

    juju.destroy_model('c1:m')

    assert juju.model is None


def test_destroy_controller_unqualified_matches_qualified_self(run: mocks.Run):
    """destroy_model('m') resets self.model when self.model == 'c1:m'."""
    run.handle(['juju', 'destroy-model', 'm', '--no-prompt'])
    juju = jubilant.Juju(model='c1:m')

    juju.destroy_model('m')

    assert juju.model is None


def test_destroy_different_user_does_not_reset_self(run: mocks.Run):
    """destroy_model('bob/m') is a different model from self.model == 'alice/m'."""
    run.handle(['juju', 'destroy-model', 'bob/m', '--no-prompt'])
    juju = jubilant.Juju(model='alice/m')

    juju.destroy_model('bob/m')

    assert juju.model == 'alice/m'


def test_destroy_different_controller_does_not_reset_self(run: mocks.Run):
    """destroy_model('c2:m') is a different model from self.model == 'c1:m'."""
    run.handle(['juju', 'destroy-model', 'c2:m', '--no-prompt'])
    juju = jubilant.Juju(model='c1:m')

    juju.destroy_model('c2:m')

    assert juju.model == 'c1:m'


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
