import pytest

import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db'])
    juju = jubilant.Juju()

    juju.offer('mysql', 'db')


def test_with_model(run: mocks.Run):
    run.handle(['juju', 'offer', '--model', 'mdl', 'mysql:db'])
    juju = jubilant.Juju(model='mdl')

    juju.offer('mysql', 'db')


def test_name(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db', 'nam'])
    juju = jubilant.Juju()

    juju.offer('mysql', 'db', name='nam')


def test_multiple_endpoints(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db,log'])
    juju = jubilant.Juju()

    juju.offer('mysql', 'db', 'log')


def test_type_errors():
    juju = jubilant.Juju()

    with pytest.raises(TypeError):
        juju.offer('mysql:db', 'name')  # endpoint in "app" argument
    with pytest.raises(TypeError):
        juju.offer('mysql')  # no endpoint provided
