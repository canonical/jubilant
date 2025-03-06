import jubilant
from jubilant.fixtures import juju

_ = juju  # used as fixture (argument name)


def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')

    juju.wait(jubilant.all_error, timeout=60)  # TODO: make it fail temporarily
