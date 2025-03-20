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


def test_method_order():
    # We like to keep the methods in alphabetical order, so we don't have to think
    # about where to put each new method. Test that we've done that.
    method_linenos = {
        k: v.__code__.co_firstlineno
        for k, v in jubilant.Juju.__dict__.items()
        if not k.startswith('_') and callable(v)
    }
    sorted_by_alpha = sorted(method_linenos)
    sorted_by_lines = sorted(method_linenos, key=lambda k: method_linenos[k])
    assert sorted_by_lines == sorted_by_alpha, 'Please keep Juju methods in alphabetical order'
