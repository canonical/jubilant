from __future__ import annotations

import urllib.request

import pytest

import jubilant

from . import helpers


@pytest.fixture(scope='module', autouse=True)
def setup(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    juju.wait(jubilant.all_active)


def test_deploy(juju: jubilant.Juju):
    # Setup has already done "juju deploy", this tests it.
    status = juju.status()
    address = status.apps['snappass-test'].units['snappass-test/0'].address

    with urllib.request.urlopen(f'http://{address}:5000/', timeout=10) as resp:
        assert 200 <= resp.status < 300
        body = resp.read().decode()

    assert '<title>' in body
    assert 'snappass' in body.lower()

    # Ensure refresh works (though it will already be up to date).
    juju.refresh('snappass-test')

    # Wait for all unit agents to be idle (and ensure all_agents_idle works).
    status = juju.wait(jubilant.all_agents_idle)
    assert jubilant.all_agents_idle(status, 'snappass-test')


def test_refresh_switch_to_charmhub(juju: jubilant.Juju, tmp_path):
    # Download the existing Charmhub charm to a local .charm file.
    local_charm = tmp_path / 'snappass-test.charm'
    juju.cli(
        'download',
        'snappass-test',
        '--filepath',
        str(local_charm),
        include_model=False,
    )
    assert local_charm.is_file()

    # Switch from Charmhub to the local charm.
    juju.refresh('snappass-test', switch=local_charm)
    juju.wait(
        lambda status: (
            'snappass-test' in status.apps and status.apps['snappass-test'].charm_origin == 'local'
        )
    )

    # Switch back to Charmhub.
    juju.refresh('snappass-test', switch='snappass-test')
    juju.wait(
        lambda status: (
            jubilant.all_active(status, 'snappass-test')
            and status.apps['snappass-test'].charm_origin == 'charmhub'
            and status.apps['snappass-test'].charm_name == 'snappass-test'
        )
    )


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


def test_deploy_with_local_file_resource(juju: jubilant.Juju, empty_tar: str):
    juju.deploy(
        helpers.find_charm('testapp'),
        resources={'test-file': empty_tar},
    )
    juju.wait(
        lambda status: 'testapp' in status.apps and 'testapp/0' in status.apps['testapp'].units
    )


def test_refresh_path(juju: jubilant.Juju):
    juju.deploy(helpers.find_charm('testdb'))
    juju.wait(
        lambda status: status.apps['testdb'].units['testdb/0'].workload_status.current == 'unknown'
    )
    juju.refresh('testdb', path=helpers.find_charm('testdb'))
    juju.wait(
        lambda status: status.apps['testdb'].units['testdb/0'].workload_status.current == 'unknown'
    )


def test_version(juju: jubilant.Juju):
    version = juju.version()
    raw_version = juju.cli('version', include_model=False).strip()
    assert str(version) == raw_version
