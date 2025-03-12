import requests

import jubilant


def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    status = juju.wait(jubilant.all_active)

    address = status.apps['snappass-test'].units['snappass-test/0'].address
    response = requests.get(f'http://{address}:5000/', timeout=10)
    response.raise_for_status()
    assert '<title>' in response.text
    assert 'snappass' in response.text.lower()


def test_add_and_remove_unit(juju: jubilant.Juju):
    juju.deploy('snappass-test')
    juju.wait(jubilant.all_active)

    juju.add_unit('snappass-test')
    juju.wait(
        lambda status: jubilant.all_active(status) and len(status.apps['snappass-test'].units) == 2
    )

    juju.remove_unit('snappass-test', num_units=1)
    juju.wait(
        lambda status: jubilant.all_active(status) and len(status.apps['snappass-test'].units) == 1
    )


def test_config(juju: jubilant.Juju):
    juju.deploy('wordpress-k8s')
    juju.wait(jubilant.all_blocked)  # Waiting for db relation/config

    config = juju.config('wordpress-k8s')
    assert config['blog_hostname'] == ''

    app_config = juju.config('wordpress-k8s', app_config=True)
    assert app_config['trust'] is False

    juju.config('wordpress-k8s', {'blog_hostname': 'example.com'})
    config = juju.config('wordpress-k8s')
    assert config['blog_hostname'] == 'example.com'


def test_integrate_and_run(juju: jubilant.Juju):
    juju.deploy('wordpress-k8s')
    juju.deploy('mysql-k8s')
    juju.integrate('wordpress-k8s', 'mysql-k8s')
    status = juju.wait(jubilant.all_active)

    address = status.apps['wordpress-k8s'].units['wordpress-k8s/0'].address
    response = requests.get(f'http://{address}/', timeout=10)
    response.raise_for_status()
    assert '<title>' in response.text
    assert 'wordpress' in response.text.lower()

    result = juju.run('wordpress-k8s/0', 'get-initial-password')
    assert result.success
    assert result.return_code == 0
    assert len(result.results['password']) >= 8
