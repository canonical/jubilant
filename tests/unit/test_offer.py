from __future__ import annotations

import pytest

import jubilant

from . import mocks


def test(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint='db')


def test_controller_arg(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db', '--controller', 'inctl'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint='db', controller='inctl')


@pytest.mark.parametrize('self_model', ['origmodel', 'origctl:origmodel'])
def test_controller_arg_raises(self_model: str):
    juju = jubilant.Juju(model=self_model)

    with pytest.raises(ValueError):
        juju.offer('mysql', endpoint='db', controller='inctl')


def test_insert_model(run: mocks.Run):
    # "juju offer" isn't a model-based command, so we insert self.model
    # (if app isn't a dotted name and controller is None).
    run.handle(['juju', 'offer', 'origmodel.mysql:db'])
    juju = jubilant.Juju(model='origmodel')

    juju.offer('mysql', endpoint='db')


def test_insert_controller_and_model(run: mocks.Run):
    run.handle(['juju', 'offer', 'origmodel.mysql:db', '--controller', 'origctl'])
    juju = jubilant.Juju(model='origctl:origmodel')

    juju.offer('mysql', endpoint='db')


@pytest.mark.parametrize('self_model', [None, 'origmodel', 'origctl:origmodel'])
def test_dotted_app(self_model: str | None, run: mocks.Run):
    # If app is a dotted name, we ignore self.model.
    run.handle(['juju', 'offer', 'inmodel.mysql:db'])
    juju = jubilant.Juju(model=self_model)

    juju.offer('inmodel.mysql', endpoint='db')


@pytest.mark.parametrize('self_model', [None, 'origmodel', 'origctl:origmodel'])
def test_dotted_app_controller_arg(self_model: str | None, run: mocks.Run):
    run.handle(['juju', 'offer', 'inmodel.mysql:db', '--controller', 'inctl'])
    juju = jubilant.Juju(model=self_model)

    juju.offer('inmodel.mysql', endpoint='db', controller='inctl')


def test_name(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db', 'nam'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint='db', name='nam')


def test_multiple_endpoints(run: mocks.Run):
    run.handle(['juju', 'offer', 'mysql:db,log'])
    juju = jubilant.Juju()

    juju.offer('mysql', endpoint=['db', 'log'])
