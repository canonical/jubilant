import pytest

import jubilant_backports as jubilant

from .. import mocks


@pytest.mark.parametrize('juju_version', ['2.9.52', '3.6.8'])
def test_init_defaults(juju_version: str, run: mocks.Run):
    # This will replace the one that the mock installs by default.
    run.handle(['juju', 'version', '--format', 'json'], stdout=f'"{juju_version}"\n')
    juju = jubilant.Juju()

    assert juju.model is None
    assert juju.wait_timeout is not None  # don't test the exact value of the default
    assert juju.cli_binary == 'juju'
    assert juju._is_juju_2 == (juju_version[0] == '2')
