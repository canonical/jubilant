import pathlib

import requests

import jubilant

CHARMS_PATH = pathlib.Path(__file__).parent / 'charms'


def test_deploy(juju: jubilant.Juju):
    charm = 'snappass-test'
    juju.deploy(charm)
    status = juju.wait(jubilant.all_active)

    address = status.apps[charm].units[charm + '/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert '<title>' in response.text
    assert 'snappass' in response.text.lower()


def test_add_and_remove_unit(juju: jubilant.Juju):
    charm = 'snappass-test'
    juju.deploy(charm)
    juju.wait(jubilant.all_active)

    juju.add_unit(charm)
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps[charm].units) == 2)

    juju.remove_unit(charm, num_units=1)
    juju.wait(lambda status: jubilant.all_active(status) and len(status.apps[charm].units) == 1)


def test_config_and_run(juju: jubilant.Juju):
    charm = 'testdb'
    juju.deploy(charm_path(charm))

    # unit should come up as "unknown"
    juju.wait(
        lambda status: status.apps[charm].units[charm + '/0'].workload_status.current == 'unknown'
    )

    config = juju.config(charm)
    assert config['testoption'] == ''

    app_config = juju.config(charm, app_config=True)
    assert app_config['trust'] is False

    juju.config(charm, {'testoption': 'foobar'})
    config = juju.config(charm)
    assert config['testoption'] == 'foobar'

    result = juju.run(charm + '/0', 'do-thing', {'param1': 'value1'})
    assert result.success
    assert result.return_code == 0
    assert result.results == {
        'config': {'testoption': 'foobar'},
        'params': {'param1': 'value1'},
        'thingy': 'foo',
    }


def test_integrate(juju: jubilant.Juju):
    juju.deploy(charm_path('testdb'))
    juju.deploy(charm_path('testapp'))

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'


def charm_path(name: str) -> pathlib.Path:
    """Return full absolute path to given test charm."""
    # .charm filename has platform in it, so search with *.charm
    charms = [p.absolute() for p in (CHARMS_PATH / name).glob('*.charm')]
    assert charms, f'{name} .charm file not found'
    assert len(charms) == 1, f'{name} has more than one .charm file, unsure which to use'
    return charms[0]
