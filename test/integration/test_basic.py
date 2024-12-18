import pytest

import jubilant


@pytest.fixture
def juju():
    j = jubilant.Juju()
    j.add_model('tt')  # TODO: random model name
    yield j
    j.destroy_model('tt')


def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')

    juju.wait(lambda status: status.apps['snappass-test'].is_active)
