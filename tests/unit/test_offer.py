import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint='db')


def test_name(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db', 'nam'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint='db', name='nam')


def test_multiple_endpoints(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db,log'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint=['db', 'log'])
