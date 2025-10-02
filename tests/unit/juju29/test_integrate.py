import pytest

import jubilant

from . import mocks


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test(juju_version: str, run: mocks.Run):
    run.handle(['juju', 'relate' if juju_version[0] == '2' else 'integrate', 'app1', 'app2'])
    juju = jubilant.Juju(cli_version=juju_version)
    juju.cli_version = juju_version

    juju.integrate('app1', 'app2')


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_with_model(juju_version: str, run: mocks.Run):
    run.handle(
        [
            'juju',
            'relate' if juju_version[0] == '2' else 'integrate',
            '--model',
            'mdl',
            'app1',
            'app2',
        ]
    )
    juju = jubilant.Juju(model='mdl', cli_version=juju_version)
    juju.cli_version = juju_version

    juju.integrate('app1', 'app2')


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_with_endpoints(juju_version: str, run: mocks.Run):
    run.handle(['juju', 'relate' if juju_version[0] == '2' else 'integrate', 'app1:db', 'app2:db'])
    juju = jubilant.Juju(cli_version=juju_version)
    juju.cli_version = juju_version

    juju.integrate('app1:db', 'app2:db')


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_via(juju_version: str, run: mocks.Run):
    run.handle(
        [
            'juju',
            'relate' if juju_version[0] == '2' else 'integrate',
            'app1',
            'mdl.app2',
            '--via',
            '192.168.0.0/16',
        ]
    )
    juju = jubilant.Juju(cli_version=juju_version)
    juju.cli_version = juju_version

    juju.integrate('app1', 'mdl.app2', via='192.168.0.0/16')


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_via_list(juju_version: str, run: mocks.Run):
    run.handle(
        [
            'juju',
            'relate' if juju_version[0] == '2' else 'integrate',
            'app1',
            'mdl.app2',
            '--via',
            '192.168.0.0/16,16,10.0.0.0/8',
        ]
    )
    juju = jubilant.Juju(cli_version=juju_version)
    juju.cli_version = juju_version

    juju.integrate('app1', 'mdl.app2', via=['192.168.0.0/16', '16,10.0.0.0/8'])
