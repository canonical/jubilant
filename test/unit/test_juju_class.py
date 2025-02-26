import jubilant


def test_init_defaults():
    juju = jubilant.Juju()

    assert juju.model is None
    assert juju.wait_timeout is not None  # don't test the exact value of the default
    assert juju.cli_binary == 'juju'


def test_init_args():
    juju = jubilant.Juju(model='m', wait_timeout=7, cli_binary='/bin/juju3')

    assert juju.model == 'm'
    assert juju.wait_timeout == 7
    assert juju.cli_binary == '/bin/juju3'


def test_repr_args():
    juju = jubilant.Juju(model='m', wait_timeout=7, cli_binary='/bin/juju3')

    assert repr(juju) == "Juju(model='m', wait_timeout=7, cli_binary='/bin/juju3')"
