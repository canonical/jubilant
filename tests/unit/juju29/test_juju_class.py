import pytest

import jubilant

from . import mocks


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_init_defaults(juju_version: str, run: mocks.Run):
    run.handle(['juju', 'version', '--format', 'json'], stdout=f'"{juju_version}"\n')
    juju = jubilant.Juju()

    assert juju.model is None
    assert juju.wait_timeout is not None  # don't test the exact value of the default
    assert juju.cli_binary == 'juju'
    assert juju.cli_version == juju_version
    assert juju.cli_major_version == int(juju_version.split('.', 1)[0])


def test_init_args():
    juju = jubilant.Juju(model='m', wait_timeout=7, cli_binary='/bin/juju3', cli_version='28.8.6')

    assert juju.model == 'm'
    assert juju.wait_timeout == 7
    assert juju.cli_binary == '/bin/juju3'
    assert juju.cli_version == '28.8.6'


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_repr_args(juju_version: str, run: mocks.Run):
    run.handle(['/bin/juju', 'version', '--format', 'json'], stdout=f'"{juju_version}"\n')
    juju = jubilant.Juju(model='m', wait_timeout=7, cli_binary='/bin/juju')

    assert (
        repr(juju)
        == f"Juju(model='m', wait_timeout=7, cli_binary='/bin/juju', cli_version='{juju_version}')"
    )


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
