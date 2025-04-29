from __future__ import annotations

import pytest
import requests

import jubilant


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    juju.wait(jubilant.all_active)


def test_deploy(juju: jubilant.Juju):
    # Setup has already done "juju deploy", this tests it.
    status = juju.status()
    address = status.apps['snappass-test'].units['snappass-test/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert '<title>' in response.text
    assert 'snappass' in response.text.lower()

    # Ensure refresh works (though it will already be up to date).
    juju.refresh('snappass-test')

    # Wait for all unit agents to be idle (and ensure all_agents_idle works).
    status = juju.wait(jubilant.all_agents_idle)
    assert jubilant.all_agents_idle(status, 'snappass-test')


def test_add_and_remove_unit(juju: jubilant.Juju):
    juju.add_unit('snappass-test')
    juju.wait(
        lambda status: jubilant.all_active(status) and len(status.apps['snappass-test'].units) == 2
    )

    juju.remove_unit('snappass-test', num_units=1)
    juju.wait(
        lambda status: jubilant.all_active(status) and len(status.apps['snappass-test'].units) == 1
    )


def test_remove_application(juju: jubilant.Juju):
    juju.remove_application('snappass-test')
    juju.wait(lambda status: not status.apps)


def test_deploy_with_resources(juju: jubilant.Juju):
    juju.deploy(
        'snappass-test',
        'snappass-with-resources',
        base='ubuntu@20.04',
        resources={
            'snappass-image': 'benhoyt/snappass-test',
            'redis-image': 'redis',
        },
    )
    juju.wait(lambda status: status.apps['snappass-with-resources'].is_active)
