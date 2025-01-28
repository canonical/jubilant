import jubilant


def test_repr():
    juju = jubilant.Juju()
    assert repr(juju) == "Juju(model=None, wait_timeout=180.0, cli_binary='juju')"
