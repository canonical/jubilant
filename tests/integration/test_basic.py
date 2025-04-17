import pytest

import jubilant

from . import helpers


# Tests config get, config set, trust, run, exec, and cli with input
def test_charm_basics(juju: jubilant.Juju):
    charm = 'testdb'
    juju.deploy(helpers.find_charm(charm))

    # Unit should come up as "unknown"
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

    # Test cli with input
    stdout = juju.cli('ssh', '--container', 'charm', charm + '/0', 'cat', stdin='foo')
    assert stdout == 'foo'
