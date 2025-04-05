import pathlib

import pytest
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


# Tests config get, config set, run, and exec
def test_charm_basics(juju: jubilant.Juju):
    charm = 'testdb'
    juju.deploy(charm_path(charm))

    # unit should come up as "unknown"
    juju.wait(
        lambda status: status.apps[charm].units[charm + '/0'].workload_status.current == 'unknown'
    )

    # Test config get and set
    config = juju.config(charm)
    assert config['testoption'] == ''

    app_config = juju.config(charm, app_config=True)
    assert app_config['trust'] is False

    juju.config(charm, {'testoption': 'foobar'})
    config = juju.config(charm)
    assert config['testoption'] == 'foobar'

    # Test trust command (at least that app_config value updates)
    juju.trust(charm, scope='cluster')
    app_config = juju.config(charm, app_config=True)
    assert app_config['trust'] is True
    juju.trust(charm, remove=True, scope='cluster')
    app_config = juju.config(charm, app_config=True)
    assert app_config['trust'] is False

    # Test run (running an action)
    task = juju.run(charm + '/0', 'do-thing', {'param1': 'value1'})
    assert task.success
    assert task.return_code == 0
    assert task.results == {
        'config': {'testoption': 'foobar'},
        'params': {'param1': 'value1'},
        'thingy': 'foo',
    }

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.run(charm + '/0', 'do-thing', {'error': 'ERR'})
    task = excinfo.value.task
    assert not task.success
    assert task.status == 'failed'
    assert task.return_code == 0  # return_code is 0 even if action fails
    assert task.message == 'failed with error: ERR'

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.run(charm + '/0', 'do-thing', {'exception': 'EXC'})
    task = excinfo.value.task
    assert not task.success
    assert task.status == 'failed'
    assert task.return_code != 0
    assert 'EXC' in task.stderr

    with pytest.raises(TimeoutError):
        juju.run(charm + '/0', 'do-thing', wait=0.001)

    with pytest.raises(ValueError):
        juju.run(charm + '/0', 'action-not-defined')
    with pytest.raises(ValueError):
        juju.run(charm + '/42', 'do-thing')  # unit not found

    # Test exec
    task = juju.exec('echo foo', unit=charm + '/0')
    assert task.success
    assert task.return_code == 0
    assert task.stdout == 'foo\n'
    assert task.stderr == ''

    task = juju.exec('echo', 'bar', 'baz', unit=charm + '/0')
    assert task.success
    assert task.stdout == 'bar baz\n'

    with pytest.raises(jubilant.TaskError) as excinfo:
        juju.exec('sleep x', unit=charm + '/0')
    task = excinfo.value.task
    assert not task.success
    assert task.stdout == ''
    assert 'invalid time' in task.stderr

    with pytest.raises(TimeoutError):
        juju.exec('sleep 1', unit=charm + '/0', wait=0.001)

    with pytest.raises(ValueError):
        juju.exec('echo foo', unit=charm + '/42')  # unit not found
    with pytest.raises(jubilant.CLIError):
        juju.exec('echo foo', machine=0)  # unable to target machines with a k8s controller


def test_integrate(juju: jubilant.Juju):
    juju.deploy(charm_path('testdb'))
    juju.deploy(charm_path('testapp'))

    juju.integrate('testdb', 'testapp')
    status = juju.wait(jubilant.all_active)
    assert status.apps['testdb'].relations['db'][0].related_app == 'testapp'
    assert status.apps['testapp'].relations['db'][0].related_app == 'testdb'
    assert status.apps['testdb'].app_status.message == 'relation created'
    assert status.apps['testapp'].app_status.message == 'relation changed: dbkey=dbvalue'

    juju.remove_relation('testdb', 'testapp')
    juju.wait(
        lambda status: (
            not status.apps['testdb'].relations and not status.apps['testapp'].relations
        )
    )


def charm_path(name: str) -> pathlib.Path:
    """Return full absolute path to given test charm."""
    # .charm filename has platform in it, so search with *.charm
    charms = [p.absolute() for p in (CHARMS_PATH / name).glob('*.charm')]
    assert charms, f'{name} .charm file not found'
    assert len(charms) == 1, f'{name} has more than one .charm file, unsure which to use'
    return charms[0]
