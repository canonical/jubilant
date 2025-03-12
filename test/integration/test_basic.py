import jubilant


def test_deploy(juju: jubilant.Juju):
    juju.deploy('snappass-test')

    juju.wait(jubilant.all_error, timeout=60) # TODO: revert
